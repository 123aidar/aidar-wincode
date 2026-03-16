@echo off
chcp 65001 >nul
title AutoService Pro

echo ========================================
echo   AutoService Pro — Запуск проекта
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] Установка зависимостей...
py -m pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo ОШИБКА: Не удалось установить зависимости.
    pause
    exit /b 1
)

cd backend

echo [2/4] Создание миграций...
py manage.py makemigrations --no-input

echo [3/4] Применение миграций...
py manage.py migrate --no-input

echo [4/4] Загрузка демо-данных...
py manage.py seed_data

echo.
echo ========================================
echo   Сервер запущен: http://127.0.0.1:8080
echo   Нажмите Ctrl+C для остановки
echo ========================================
echo.

py manage.py runserver 8080
pause
