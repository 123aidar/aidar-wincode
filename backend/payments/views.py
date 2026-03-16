from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import viewsets
from .models import Payment
from .serializers import PaymentSerializer
from orders.models import Order
from users.permissions import IsAdminOrManager


@login_required
def payments_list_view(request):
    if request.user.role == 'mechanic':
        return redirect('dashboard')
    payments = Payment.objects.select_related('order__client').all()
    return render(request, 'payments/list.html', {'payments': payments})


@login_required
def payment_create_view(request, order_pk):
    if request.user.role == 'mechanic':
        return redirect('dashboard')
    order = get_object_or_404(Order, pk=order_pk)
    if request.method == 'POST':
        amount = request.POST.get('amount', 0)
        method = request.POST.get('payment_method', 'cash')
        notes = request.POST.get('notes', '').strip()
        Payment.objects.create(order=order, amount=amount, payment_method=method, notes=notes)
        messages.success(request, f'Платёж на сумму {amount} ₽ записан.')
        return redirect('order_detail', pk=order.pk)
    return render(request, 'payments/create.html', {'order': order})


@login_required
def payment_receipt_view(request, payment_id):
    payment = get_object_or_404(
        Payment.objects.select_related('order__client', 'order__car')
                       .prefetch_related('order__order_services__service', 'order__order_parts__part'),
        pk=payment_id
    )
    return render(request, 'payments/receipt.html', {
        'payment': payment,
        'order': payment.order,
        'client': payment.order.client,
    })


@login_required
def payment_delete_view(request, pk):
    if request.user.role != 'admin':
        return redirect('payments_list')
    payment = get_object_or_404(Payment, pk=pk)
    if request.method == 'POST':
        payment.delete()
        messages.success(request, 'Платёж удалён.')
        return redirect('payments_list')
    return redirect('payments_list')


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related('order').all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAdminOrManager]
    filterset_fields = ['order', 'payment_method']
