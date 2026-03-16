from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count, F, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta, date as date_type
from decimal import Decimal
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from orders.models import Order, OrderService
from payments.models import Payment
from parts.models import Part
from clients.models import Client
from cars.models import Car
from users.models import User
from users.permissions import IsAdmin


@login_required
def dashboard_view(request):
    today = timezone.now().date()
    month_start = today.replace(day=1)

    # ── All-time totals ──────────────────────────────────────────────
    total_clients = Client.objects.count()
    total_orders  = Order.objects.count()
    total_revenue = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0

    # ── Today ───────────────────────────────────────────────────────
    orders_today  = Order.objects.filter(created_at__date=today).count()
    revenue_today = Payment.objects.filter(created_at__date=today).aggregate(total=Sum('amount'))['total'] or 0

    # ── This month ──────────────────────────────────────────────────
    orders_this_month  = Order.objects.filter(created_at__date__gte=month_start).count()
    revenue_this_month = Payment.objects.filter(created_at__date__gte=month_start).aggregate(total=Sum('amount'))['total'] or 0

    # ── Active & stock ──────────────────────────────────────────────
    active_repairs = Order.objects.filter(status__in=['diagnostics', 'repairing', 'waiting_parts']).count()
    low_stock_count = Part.objects.filter(is_active=True, quantity__lte=F('minimum_stock')).count()

    # ── Recent data for tables ───────────────────────────────────────
    recent_orders = Order.objects.select_related('client', 'car', 'assigned_mechanic').order_by('-created_at')[:10]
    low_parts     = Part.objects.filter(is_active=True, quantity__lte=F('minimum_stock')).order_by('quantity')[:8]

    context = {
        # All-time
        'total_clients': total_clients,
        'total_orders':  total_orders,
        'total_revenue': total_revenue,
        # Active
        'active_repairs': active_repairs,
        'low_stock_count': low_stock_count,
        # Today
        'orders_today':  orders_today,
        'revenue_today': revenue_today,
        # Month
        'orders_this_month':  orders_this_month,
        'total_revenue_month': revenue_this_month,
        # Tables
        'recent_orders': recent_orders,
        'low_parts':     low_parts,
    }
    return render(request, 'dashboard/index.html', context)


def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


# ─── Analytics page helpers ───────────────────────────────────────────────────

def _collect_period_data(date_from, date_to):
    """Collect all analytics data for a given period."""
    orders   = Order.objects.filter(created_at__date__gte=date_from, created_at__date__lte=date_to)
    payments = Payment.objects.filter(created_at__date__gte=date_from, created_at__date__lte=date_to)

    total_revenue = payments.aggregate(t=Sum('amount'))['t'] or Decimal('0')
    orders_count  = orders.count()
    avg_order     = total_revenue / orders_count if orders_count else Decimal('0')

    completed_orders = orders.filter(status__in=['completed', 'delivered'])
    orders_completed = completed_orders.count()

    # Status breakdown
    status_map = dict(Order.Status.choices)
    orders_by_status = {}
    for row in orders.values('status').annotate(c=Count('id')):
        orders_by_status[status_map.get(row['status'], row['status'])] = row['c']

    # Monthly revenue & orders
    monthly_rev = (
        payments
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )
    monthly_data = [(r['month'].strftime('%B %Y'), r['total']) for r in monthly_rev]

    monthly_ord = (
        orders
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(c=Count('id'), rev=Sum('total_price'))
        .order_by('month')
    )
    monthly_orders = [(r['month'].strftime('%B %Y'), r['c'], r['rev'] or Decimal('0'))
                      for r in monthly_ord]
    monthly_orders_count = {m: c for m, c, _ in monthly_orders}

    # Payment methods
    pm = payments.values('payment_method').annotate(t=Sum('amount'))
    payment_by_method = {r['payment_method']: r['t'] or Decimal('0') for r in pm}

    # Services revenue
    svc_qs = (
        OrderService.objects
        .filter(order__created_at__date__gte=date_from, order__created_at__date__lte=date_to)
        .values('service__name')
        .annotate(cnt=Count('id'), rev=Sum('price'))
        .order_by('-rev')[:20]
    )
    services_revenue = [(r['service__name'], r['cnt'], r['rev'] or Decimal('0')) for r in svc_qs]

    # Parts cost (from deliveries received in this period)
    try:
        from deliveries.models import DeliveryItem
        parts_cost = (
            DeliveryItem.objects
            .filter(delivery__status='received',
                    delivery__delivery_date__gte=date_from,
                    delivery__delivery_date__lte=date_to)
            .aggregate(t=Sum(F('quantity') * F('unit_price')))['t'] or Decimal('0')
        )
    except Exception:
        parts_cost = Decimal('0')

    # Clients
    new_clients = Client.objects.filter(created_at__date__gte=date_from,
                                        created_at__date__lte=date_to).count()
    returning_clients = orders.exclude(
        client__in=Client.objects.filter(created_at__date__gte=date_from,
                                         created_at__date__lte=date_to)
    ).values('client').distinct().count()

    # Mechanics
    mechanics_qs = User.objects.filter(role='mechanic', is_active=True)
    mechanics = []
    mechanic_orders_flat = []
    for m in mechanics_qs:
        m_orders = orders.filter(assigned_mechanic=m)
        m_done   = m_orders.filter(status__in=['completed', 'delivered'])
        m_paid   = payments.filter(order__assigned_mechanic=m)
        m_rev    = m_paid.aggregate(t=Sum('amount'))['t'] or Decimal('0')
        m_tot    = m_orders.count()
        m_dcnt   = m_done.count()

        sb = {}
        for row in m_orders.values('status').annotate(c=Count('id')):
            sb[status_map.get(row['status'], row['status'])] = row['c']

        mechanics.append({
            'name':              m.get_full_name() or m.username,
            'orders_total':      m_tot,
            'orders_completed':  m_dcnt,
            'orders_active':     m_orders.filter(
                                    status__in=['diagnostics', 'repairing', 'waiting_parts']).count(),
            'revenue':           m_rev,
            'status_breakdown':  sb,
        })
        for o in m_orders.select_related('client', 'car').order_by('-created_at')[:50]:
            mechanic_orders_flat.append({
                'mechanic':    m.get_full_name() or m.username,
                'id':          o.pk,
                'date':        o.created_at.strftime('%d.%m.%Y'),
                'client':      o.client.name,
                'status':      o.get_status_display(),
                'total_price': o.total_price,
            })

    # Orders list for Excel
    orders_list = []
    by_client_map = {}
    for o in orders.select_related('client', 'car', 'assigned_mechanic').order_by('-created_at'):
        paid = payments.filter(order=o).aggregate(t=Sum('amount'))['t'] or Decimal('0')
        orders_list.append({
            'id':          o.pk,
            'date':        o.created_at.strftime('%d.%m.%Y'),
            'client':      o.client.name,
            'car':         f"{o.car.brand} {o.car.model} ({o.car.license_plate})",
            'mechanic':    o.assigned_mechanic.get_full_name() if o.assigned_mechanic else '—',
            'status':      o.get_status_display(),
            'total_price': o.total_price,
            'paid':        paid,
        })
        cn = o.client.name
        cp = o.client.phone
        if cn not in by_client_map:
            by_client_map[cn] = {'name': cn, 'phone': cp, 'count': 0, 'total': Decimal('0')}
        by_client_map[cn]['count'] += 1
        by_client_map[cn]['total'] += o.total_price

    by_client = sorted(by_client_map.values(), key=lambda x: x['total'], reverse=True)
    for c in by_client:
        c['avg'] = c['total'] / c['count'] if c['count'] else Decimal('0')

    # Chart data (for JS)
    chart_labels  = [m for m, _ in monthly_data]
    chart_revenue = [float(r) for _, r in monthly_data]
    chart_orders  = [c for _, c, _ in monthly_orders]
    svc_labels    = [n for n, _, _ in services_revenue[:10]]
    svc_values    = [int(c) for _, c, _ in services_revenue[:10]]
    mech_labels   = [m['name'] for m in mechanics]
    mech_values   = [int(m['orders_total']) for m in mechanics]

    return {
        'date_from':           date_from,
        'date_to':             date_to,
        'total_revenue':       total_revenue,
        'orders_count':        orders_count,
        'orders_completed':    orders_completed,
        'orders_total':        orders_count,
        'avg_order_value':     avg_order,
        'orders_by_status':    orders_by_status,
        'monthly_data':        monthly_data,
        'monthly_orders':      monthly_orders,
        'monthly_orders_count': monthly_orders_count,
        'payment_by_method':   payment_by_method,
        'services_revenue':    services_revenue,
        'parts_cost':          parts_cost,
        'new_clients':         new_clients,
        'returning_clients':   returning_clients,
        'mechanics':           mechanics,
        'mechanic_orders':     mechanic_orders_flat,
        'orders_list':         orders_list,
        'by_client':           by_client,
        # Charts
        'chart_labels_json':   chart_labels,
        'chart_revenue_json':  chart_revenue,
        'chart_orders_json':   chart_orders,
        'svc_labels_json':     svc_labels,
        'svc_values_json':     svc_values,
        'mech_labels_json':    mech_labels,
        'mech_values_json':    mech_values,
        'status_labels_json':  list(orders_by_status.keys()),
        'status_values_json':  list(orders_by_status.values()),
    }


@login_required
def analytics_page_view(request):
    if request.user.role != 'admin':
        messages.error(request, 'Доступ запрещён.')
        return redirect('dashboard')
    today = timezone.now().date()
    # Default: current month
    default_from = today.replace(day=1)
    default_to   = today

    raw_from = request.GET.get('date_from', '')
    raw_to   = request.GET.get('date_to', '')
    try:
        date_from = date_type.fromisoformat(raw_from) if raw_from else default_from
        date_to   = date_type.fromisoformat(raw_to)   if raw_to   else default_to
    except ValueError:
        date_from, date_to = default_from, default_to

    if date_from > date_to:
        date_from, date_to = date_to, date_from

    data = _collect_period_data(date_from, date_to)

    import json
    context = {
        **data,
        'chart_labels_json':  json.dumps(data['chart_labels_json'],  ensure_ascii=False),
        'chart_revenue_json': json.dumps(data['chart_revenue_json']),
        'chart_orders_json':  json.dumps(data['chart_orders_json']),
        'svc_labels_json':    json.dumps(data['svc_labels_json'],    ensure_ascii=False),
        'svc_values_json':    json.dumps(data['svc_values_json']),
        'mech_labels_json':   json.dumps(data['mech_labels_json'],   ensure_ascii=False),
        'mech_values_json':   json.dumps(data['mech_values_json']),
        'status_labels_json': json.dumps(data['status_labels_json'], ensure_ascii=False),
        'status_values_json': json.dumps(data['status_values_json']),
    }
    return render(request, 'analytics/index.html', context)


@login_required
def report_download_view(request):
    if request.user.role != 'admin':
        messages.error(request, 'Доступ запрещён.')
        return redirect('dashboard')
    from analytics.reports import (
        build_word_tax_report,
        build_word_productivity_report,
        build_word_mechanics_report,
        build_excel_financial_report,
        build_excel_orders_report,
        build_excel_mechanics_report,
    )
    today = timezone.now().date()
    raw_from = request.GET.get('date_from', '')
    raw_to   = request.GET.get('date_to', '')
    try:
        date_from = date_type.fromisoformat(raw_from) if raw_from else today.replace(day=1)
        date_to   = date_type.fromisoformat(raw_to)   if raw_to   else today
    except ValueError:
        date_from, date_to = today.replace(day=1), today

    report_type   = request.GET.get('type', 'financial')
    report_format = request.GET.get('format', 'excel')

    data = _collect_period_data(date_from, date_to)

    WORD_MIME  = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    EXCEL_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    df_str = date_from.strftime('%d.%m.%Y').replace('.', '-')
    dt_str = date_to.strftime('%d.%m.%Y').replace('.', '-')

    if report_format == 'word':
        generators = {
            'tax':          (build_word_tax_report,          f'nalog_{df_str}_{dt_str}.docx'),
            'productivity': (build_word_productivity_report, f'productivity_{df_str}_{dt_str}.docx'),
            'mechanics':    (build_word_mechanics_report,    f'mechanics_{df_str}_{dt_str}.docx'),
        }
        fn, filename = generators.get(report_type, generators['productivity'])
        buf = fn(data)
        response = HttpResponse(buf.read(), content_type=WORD_MIME)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    else:
        generators = {
            'financial': (build_excel_financial_report, f'financial_{df_str}_{dt_str}.xlsx'),
            'orders':    (build_excel_orders_report,    f'orders_{df_str}_{dt_str}.xlsx'),
            'mechanics': (build_excel_mechanics_report, f'mechanics_{df_str}_{dt_str}.xlsx'),
        }
        fn, filename = generators.get(report_type, generators['financial'])
        buf = fn(data)
        response = HttpResponse(buf.read(), content_type=EXCEL_MIME)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


# ─── API Endpoints for Charts ─────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAdmin])
def monthly_revenue_api(request):
    """Monthly revenue for the last 12 months."""
    twelve_months_ago = timezone.now() - timedelta(days=365)
    data = (
        Payment.objects
        .filter(created_at__gte=twelve_months_ago)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )
    labels = [d['month'].strftime('%b %Y') for d in data]
    values = [float(d['total']) for d in data]
    return Response({'labels': labels, 'values': values})


@api_view(['GET'])
@permission_classes([IsAdmin])
def service_popularity_api(request):
    """Most popular services."""
    data = (
        OrderService.objects
        .values('service__name')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )
    labels = [d['service__name'] for d in data]
    values = [d['count'] for d in data]
    return Response({'labels': labels, 'values': values})


@api_view(['GET'])
@permission_classes([IsAdmin])
def mechanic_workload_api(request):
    """Orders per mechanic."""
    mechanics = User.objects.filter(role='mechanic', is_active=True)
    labels = []
    values = []
    for m in mechanics:
        labels.append(m.get_full_name() or m.username)
        values.append(m.assigned_orders.filter(status__in=['diagnostics', 'repairing', 'waiting_parts']).count())
    return Response({'labels': labels, 'values': values})


@api_view(['GET'])
@permission_classes([IsAdmin])
def order_status_breakdown_api(request):
    """Order count per status."""
    data = Order.objects.values('status').annotate(count=Count('id'))
    labels = [dict(Order.Status.choices).get(d['status'], d['status']) for d in data]
    values = [d['count'] for d in data]
    return Response({'labels': labels, 'values': values})

