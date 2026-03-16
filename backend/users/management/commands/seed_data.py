import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import User
from clients.models import Client
from cars.models import Car
from services.models import Service
from suppliers.models import Supplier
from parts.models import Part
from orders.models import Order, OrderService, OrderPart
from payments.models import Payment


class Command(BaseCommand):
    help = 'Seed the database with demo data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')

        # --- Users ---
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'role': 'admin',
                'first_name': 'Admin',
                'last_name': 'User',
                'email': 'admin@autoservice.local',
                'is_staff': True,
                'is_superuser': True,
            },
        )
        admin_user.set_password('admin123')
        admin_user.save()

        manager, _ = User.objects.get_or_create(
            username='manager',
            defaults={
                'role': 'manager',
                'first_name': 'Ivan',
                'last_name': 'Petrov',
                'email': 'manager@autoservice.local',
                'phone': '+79001112233',
            },
        )
        manager.set_password('manager123')
        manager.save()

        mechanics = []
        mechanic_names = [
            ('Alexey', 'Smirnov'), ('Dmitry', 'Kozlov'), ('Sergey', 'Novikov'),
        ]
        for i, (fn, ln) in enumerate(mechanic_names, start=1):
            m, _ = User.objects.get_or_create(
                username=f'mechanic{i}',
                defaults={
                    'role': 'mechanic',
                    'first_name': fn,
                    'last_name': ln,
                    'email': f'mechanic{i}@autoservice.local',
                    'phone': f'+7900222{i:04d}',
                },
            )
            m.set_password(f'mechanic{i}')
            m.save()
            mechanics.append(m)

        # --- Clients ---
        client_data = [
            ('Andrey Volkov', '+79101112233', 'volkov@mail.ru'),
            ('Maria Kuznetsova', '+79102223344', 'mkuz@mail.ru'),
            ('Oleg Fedorov', '+79103334455', 'oleg.f@mail.ru'),
            ('Elena Sokolova', '+79104445566', 'elena.s@mail.ru'),
            ('Pavel Morozov', '+79105556677', 'pmorozov@mail.ru'),
        ]
        clients = []
        for name, phone, email in client_data:
            c, _ = Client.objects.get_or_create(
                phone=phone,
                defaults={'name': name, 'email': email},
            )
            clients.append(c)

        # --- Cars ---
        car_data = [
            (0, 'Toyota', 'Camry', 2020, 'XTA12345678901234', 'A123BC77', 'White', 45000),
            (0, 'BMW', '320i', 2019, 'WBA23456789012345', 'B456DE99', 'Black', 62000),
            (1, 'Hyundai', 'Solaris', 2021, 'Z8N34567890123456', 'C789FG50', 'Silver', 28000),
            (2, 'Kia', 'Rio', 2022, 'XWE45678901234567', 'D012HJ77', 'Red', 15000),
            (3, 'Mercedes', 'E200', 2018, 'WDD56789012345678', 'E345KL99', 'Blue', 88000),
            (4, 'Volkswagen', 'Polo', 2023, 'XW867890123456789', 'F678MN50', 'Gray', 5000),
        ]
        cars = []
        for ci, brand, model, year, vin, plate, color, ml in car_data:
            car, _ = Car.objects.get_or_create(
                vin=vin,
                defaults={
                    'client': clients[ci],
                    'brand': brand, 'model': model, 'year': year,
                    'license_plate': plate, 'color': color, 'mileage': ml,
                },
            )
            cars.append(car)

        # --- Services ---
        service_data = [
            ('Oil Change', 3500, 45),
            ('Brake Pads Replacement', 6000, 90),
            ('Wheel Alignment', 2500, 60),
            ('Diagnostics', 2000, 30),
            ('A/C Recharge', 4000, 60),
            ('Timing Belt Replacement', 15000, 180),
            ('Tire Mounting', 1500, 30),
            ('Body Polishing', 8000, 120),
        ]
        services = []
        for name, price, dur in service_data:
            s, _ = Service.objects.get_or_create(
                name=name,
                defaults={'price': Decimal(price), 'duration_minutes': dur, 'is_active': True},
            )
            services.append(s)

        # --- Suppliers ---
        supplier_data = [
            ('AutoParts Pro', 'Mikhail', '+79200001111', 'info@autopartspro.ru'),
            ('TurboSpares', 'Natalia', '+79200002222', 'sales@turbospares.ru'),
        ]
        suppliers = []
        for name, cp, phone, email in supplier_data:
            su, _ = Supplier.objects.get_or_create(
                name=name,
                defaults={'contact_person': cp, 'phone': phone, 'email': email, 'is_active': True},
            )
            suppliers.append(su)

        # --- Parts ---
        part_data = [
            ('Oil Filter', 'OF-001', 450, 280, 50, 10, 0),
            ('Air Filter', 'AF-002', 650, 400, 35, 10, 0),
            ('Brake Pad Set', 'BP-003', 3200, 2100, 20, 5, 0),
            ('Spark Plug', 'SP-004', 350, 200, 100, 20, 1),
            ('Coolant 5L', 'CL-005', 1200, 800, 15, 5, 1),
            ('Wiper Blade', 'WB-006', 800, 500, 3, 5, 0),
        ]
        parts = []
        for name, pn, price, cost, qty, minq, si in part_data:
            p, _ = Part.objects.get_or_create(
                part_number=pn,
                defaults={
                    'name': name, 'price': Decimal(price), 'cost_price': Decimal(cost),
                    'quantity': qty, 'minimum_stock': minq, 'supplier': suppliers[si],
                },
            )
            parts.append(p)

        # --- Orders ---
        statuses = ['pending', 'diagnostics', 'repairing', 'waiting_parts', 'completed', 'delivered']
        orders = []
        for i in range(8):
            car = random.choice(cars)
            order, created = Order.objects.get_or_create(
                client=car.client,
                car=car,
                description=f'Demo order #{i + 1}',
                defaults={
                    'status': random.choice(statuses),
                    'assigned_mechanic': random.choice(mechanics),
                },
            )
            if created:
                # Add 1-2 services
                chosen = random.sample(services, k=min(random.randint(1, 2), len(services)))
                for svc in chosen:
                    OrderService.objects.get_or_create(order=order, service=svc, defaults={'price': svc.price})

                # Add 0-2 parts
                for part in random.sample(parts, k=min(random.randint(0, 2), len(parts))):
                    OrderPart.objects.get_or_create(order=order, part=part, defaults={'quantity': 1})

                order.recalculate_total()
                order.save()
            orders.append(order)

        # --- Payments for completed / delivered orders ---
        for order in orders:
            if order.status in ('completed', 'delivered') and not Payment.objects.filter(order=order).exists():
                Payment.objects.create(
                    order=order,
                    amount=order.total_price,
                    payment_method=random.choice(['cash', 'card', 'transfer']),
                )

        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
        self.stdout.write(f'  Users: admin / admin123, manager / manager123, mechanic1..3 / mechanic<N>')
