from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from rest_framework import viewsets, status as drf_status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Order, OrderService, OrderPart
from .serializers import OrderSerializer, OrderCreateSerializer, OrderServiceSerializer, OrderPartSerializer
from clients.models import Client
from cars.models import Car
from services.models import Service
from parts.models import Part
from users.models import User
from users.permissions import IsAdminOrManagerOrMechanic
from .models_report import RepairReport, RepairReportPart
from django.http import HttpResponse


@login_required
def orders_list_view(request):
    orders = Order.objects.select_related('client', 'car', 'assigned_mechanic').all()
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(status=status_filter)
    # Mechanics only see their assigned orders
    if request.user.role == 'mechanic':
        orders = orders.filter(assigned_mechanic=request.user)
    return render(request, 'orders/list.html', {
        'orders': orders,
        'status_filter': status_filter,
        'statuses': Order.Status.choices,
    })


@login_required
def order_detail_view(request, pk):
    order = get_object_or_404(
        Order.objects.select_related('client', 'car', 'assigned_mechanic')
                     .prefetch_related('order_services__service', 'order_parts__part', 'payments'),
        pk=pk
    )
    # Mechanics can only view their orders
    if request.user.role == 'mechanic' and order.assigned_mechanic != request.user:
        return redirect('orders_list')
    services = Service.objects.filter(is_active=True)
    parts = Part.objects.filter(is_active=True, quantity__gt=0)
    return render(request, 'orders/detail.html', {
        'order': order,
        'services': services,
        'parts': parts,
        'statuses': Order.Status.choices,
    })


@login_required
def order_create_view(request):
    if request.user.role == 'mechanic':
        return redirect('orders_list')
    clients = Client.objects.all()
    cars = Car.objects.select_related('client').all()
    mechanics = User.objects.filter(role='mechanic', is_active=True)
    if request.method == 'POST':
        order = Order.objects.create(
            client_id=request.POST.get('client'),
            car_id=request.POST.get('car'),
            assigned_mechanic_id=request.POST.get('assigned_mechanic') or None,
            description=request.POST.get('description', '').strip(),
            status=request.POST.get('status', 'pending'),
        )
        messages.success(request, f'Заказ №{order.pk} создан.')
        return redirect('order_detail', pk=order.pk)
    return render(request, 'orders/create.html', {
        'clients': clients, 'cars': cars, 'mechanics': mechanics,
        'statuses': Order.Status.choices,
    })


@login_required
def order_update_status_view(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.user.role == 'mechanic' and order.assigned_mechanic != request.user:
        return redirect('orders_list')
    if request.method == 'POST':
        new_status = request.POST.get('status', order.status)
        order.status = new_status
        if new_status == 'completed' and not hasattr(order, 'repair_report'):
            # Автоматически создать RepairReport при завершении заказа
            report = RepairReport.objects.create(
                order=order,
                started_at=order.created_at,
                finished_at=order.completed_at or timezone.now(),
                total_price=order.total_price,
            )
            # Добавить механика (если назначен)
            if order.assigned_mechanic:
                report.mechanics.add(order.assigned_mechanic)
            # Добавить все использованные запчасти
            for op in order.order_parts.all():
                RepairReportPart.objects.create(
                    report=report,
                    part=op.part,
                    quantity=op.quantity,
                    price=op.part.price,
                )
            report.save()
        order.save()
        messages.success(request, f'Статус заказа №{order.pk} изменён на «{order.get_status_display()}».')
    return redirect('order_detail', pk=pk)


@login_required
def order_add_service_view(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.user.role == 'mechanic' and order.assigned_mechanic != request.user:
        return redirect('orders_list')
    if request.method == 'POST':
        service_id = request.POST.get('service')
        service = get_object_or_404(Service, pk=service_id)
        price = request.POST.get('price', service.price)
        OrderService.objects.create(order=order, service=service, price=price)
        order.recalculate_total()
        messages.success(request, f'Услуга «{service.name}» добавлена.')
    return redirect('order_detail', pk=pk)


@login_required
def order_add_part_view(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.user.role == 'mechanic' and order.assigned_mechanic != request.user:
        return redirect('orders_list')
    if request.method == 'POST':
        part_id = request.POST.get('part')
        quantity = int(request.POST.get('quantity', 1) or 1)
        part = get_object_or_404(Part, pk=part_id)
        if part.quantity < quantity:
            messages.error(request, f'Not enough stock for {part.name}.')
        else:
            OrderPart.objects.create(order=order, part=part, quantity=quantity)
            part.quantity -= quantity
            part.save(update_fields=['quantity'])
            order.recalculate_total()
            messages.success(request, f'Запчасть «{part.name}» x{quantity} добавлена.')
    return redirect('order_detail', pk=pk)


@login_required
def order_update_notes_view(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.user.role == 'mechanic' and order.assigned_mechanic != request.user:
        return redirect('orders_list')
    if request.method == 'POST':
        order.repair_notes = request.POST.get('repair_notes', '')
        order.save(update_fields=['repair_notes'])
        messages.success(request, 'Заметки о ремонте обновлены.')
    return redirect('order_detail', pk=pk)


@login_required
def repair_report_view(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if not hasattr(order, 'repair_report'):
        messages.error(request, 'Отчёт о ремонте ещё не сформирован.')
        return redirect('order_detail', pk=order_id)
    report = order.repair_report
    parts = report.repairreportpart_set.select_related('part').all()
    return render(request, 'orders/repair_report.html', {
        'order': order,
        'report': report,
        'parts': parts,
    })


@login_required
def repair_report_pdf_view(request, order_id):
    order = get_object_or_404(
        Order.objects.select_related('client', 'car', 'assigned_mechanic')
                     .prefetch_related('order_services__service', 'order_parts__part'),
        pk=order_id
    )
    if not hasattr(order, 'repair_report'):
        messages.error(request, 'Отчёт о ремонте ещё не сформирован.')
        return redirect('order_detail', pk=order_id)
    report = order.repair_report
    parts = report.repairreportpart_set.select_related('part').all()
    return render(request, 'orders/repair_report_print.html', {
        'order': order,
        'report': report,
        'parts': parts,
    })

@login_required
def order_delete_view(request, pk):
    if request.user.role != 'admin':
        return redirect('orders_list')
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        order.delete()
        messages.success(request, f'Заказ ↖7{pk} удалён.')
        return redirect('orders_list')
    return redirect('orders_list')

# ─── API ViewSet ──────────────────────────────────────────────────────
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related('client', 'car', 'assigned_mechanic').prefetch_related('order_services', 'order_parts')
    permission_classes = [IsAdminOrManagerOrMechanic]
    search_fields = ['client__name', 'car__license_plate']
    filterset_fields = ['status', 'assigned_mechanic']

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.role == 'mechanic':
            qs = qs.filter(assigned_mechanic=self.request.user)
        return qs

    @action(detail=True, methods=['post'])
    def add_service(self, request, pk=None):
        order = self.get_object()
        serializer = OrderServiceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(order=order)
        order.recalculate_total()
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=['post'])
    def add_part(self, request, pk=None):
        order = self.get_object()
        serializer = OrderPartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        part = serializer.validated_data['part']
        qty = serializer.validated_data.get('quantity', 1)
        if part.quantity < qty:
            return Response({'error': 'Not enough stock'}, status=drf_status.HTTP_400_BAD_REQUEST)
        serializer.save(order=order)
        part.quantity -= qty
        part.save(update_fields=['quantity'])
        order.recalculate_total()
        return Response(OrderSerializer(order).data)
