from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from rest_framework import viewsets
from .models import User
from .serializers import UserSerializer, UserCreateSerializer
from .permissions import IsAdmin


# ─── Template Views ───────────────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Invalid username or password.')
    return render(request, 'auth/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def users_list_view(request):
    if request.user.role != 'admin':
        return redirect('dashboard')
    users = User.objects.all()
    return render(request, 'users/list.html', {'users': users})


@login_required
def user_create_view(request):
    if request.user.role != 'admin':
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        role = request.POST.get('role', 'mechanic')
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        else:
            user = User(username=username, email=email, first_name=first_name,
                        last_name=last_name, role=role, phone=phone)
            user.set_password(password)
            user.save()
            messages.success(request, f'Пользователь {username} создан.')
            return redirect('users_list')
    return render(request, 'users/create.html')


@login_required
def user_edit_view(request, pk):
    if request.user.role != 'admin':
        return redirect('dashboard')
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', '').strip()
        user.last_name = request.POST.get('last_name', '').strip()
        user.email = request.POST.get('email', '').strip()
        user.role = request.POST.get('role', user.role)
        user.phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '')
        if password:
            user.set_password(password)
        user.save()
        messages.success(request, f'Пользователь {user.username} обновлён.')
        return redirect('users_list')
    return render(request, 'users/edit.html', {'edit_user': user})


@login_required
def user_delete_view(request, pk):
    if request.user.role != 'admin':
        return redirect('dashboard')
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Пользователь удалён.')
        return redirect('users_list')
    return render(request, 'users/delete.html', {'edit_user': user})


@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', '').strip()
        user.last_name = request.POST.get('last_name', '').strip()
        user.email = request.POST.get('email', '').strip()
        user.phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '')
        if password:
            user.set_password(password)
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']
        if request.POST.get('remove_avatar') == '1':
            user.avatar = None
        user.save()
        if password:
            login(request, user)
        messages.success(request, 'Профиль обновлён.')
        return redirect('profile')
    return render(request, 'users/profile.html')


# ─── API ViewSet ──────────────────────────────────────────────────────
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAdmin]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
