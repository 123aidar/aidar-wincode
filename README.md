# AutoService Pro — Auto Service Management System

## Quick Start


Doubleclick **start.bat** to install dependencies, apply migrations, seed demo data, and start the server automatically.

---

## Важно для PDF (WeasyPrint на Windows)

Для работы экспорта PDF (отчёты, чеки) требуется установить GTK3+:

1. Скачайте GTK3+ для Windows:
	- https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
	- Скачайте последний инсталлятор (например, gtk3-runtime-*.exe)
2. Установите GTK3+ (по умолчанию: C:\\Program Files\\GTK3-Runtime)
3. Добавьте папку `bin` в переменную среды PATH:
	- Пример: `C:\\Program Files\\GTK3-Runtime\\bin`
	- Панель управления → Система → Дополнительные параметры системы → Переменные среды
4. Перезапустите компьютер или терминал/VS Code
5. Проверьте:
	```
	py -c "import weasyprint; print(weasyprint.__version__)"
	```
	Ошибок быть не должно.

После этого PDF-отчёты и чеки будут работать корректно.

---

Or run manually:
```bash
py -m pip install -r requirements.txt
cd backend
py manage.py makemigrations
py manage.py migrate
py manage.py seed_data
py manage.py runserver
```

### 6. Access the system
- **App**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/

### Demo Accounts
| Username   | Password   | Role     |
|-----------|------------|----------|
| admin     | admin123   | Admin    |
| manager   | manager123 | Manager  |
| mechanic1 | mechanic1  | Mechanic |
| mechanic2 | mechanic2  | Mechanic |
| mechanic3 | mechanic3  | Mechanic |

## Features
- Role-based access control (Admin, Manager, Mechanic)
- Client & vehicle management
- Work order lifecycle (pending → diagnostics → repairing → waiting parts → completed → delivered)
- Service catalog & parts inventory with low-stock alerts
- Supplier management
- Payment tracking (cash, card, transfer)
- Analytics dashboard with Chart.js (revenue trends, service popularity, mechanic workload, order status)
- Glassmorphism UI with neon highlights, animations, and dark theme
- REST API with DRF (SessionAuthentication, filtering, search, pagination)
