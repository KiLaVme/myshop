"""Management-команда для наповнення БД демо-даними.

Використання:
    python manage.py seed_data

Створює категорії та товари на основі оригінального HTML-каталогу
Hop & Barley, щоб одразу мати наочний каталог після запуску проєкту.
"""

from __future__ import annotations

from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.products.models import Category, Product

PRODUCTS = [
    ("Citra Hops", "hops", "5.99", "Ideal for IPAs and Pale Ales", 40),
    ("Maris Otter Pale Malt", "malts", "2.50", "Perfect for traditional ales", 100),
    ("SafAle US-05 Dry Ale Yeast", "yeast", "3.25", "Clean fermenting American ale yeast", 60),
    ("Cascade Hops", "hops", "7.49", "Great for dry hopping", 35),
    ("Caramel Malt 60L", "malts", "3.00", "Head retention in darker beers", 80),
    ("Saaz Hops", "hops", "4.75", "Essential for Lagers", 25),
    ("Pilsner Malt", "malts", "2.20", "Foundation for lagers and pilsners", 90),
    ("Imperial Organic Yeast A07", "yeast", "8.99", "American ales with citrus notes", 20),
    ("Centennial Hops", "hops", "6.20", 'Often called "Super Cascade"', 30),
    ("Mosaic Hops", "hops", "9.50", "Ideal for IPAs and Pale Ales", 15),
    ("West Coast IPA - All-Grain Kit", "adjuncts", "60.00", "West Coast IPA all-grain brewing kit", 10),
    ("Unmalted Wheat", "adjuncts", "1.80", "Belgian Witbier", 70),
]

CATEGORIES = {
    "hops": "Hops",
    "malts": "Malts",
    "yeast": "Yeast",
    "adjuncts": "Adjuncts",
}


class Command(BaseCommand):
    help = "Наповнює базу даних демонстраційними категоріями та товарами."

    def handle(self, *args, **options) -> None:
        category_objs = {}
        for slug, name in CATEGORIES.items():
            category, _ = Category.objects.get_or_create(slug=slug, defaults={"name": name})
            category_objs[slug] = category
        self.stdout.write(self.style.SUCCESS(f"Категорій готово: {len(category_objs)}"))

        created_count = 0
        for name, cat_slug, price, description, stock in PRODUCTS:
            _, created = Product.objects.get_or_create(
                name=name,
                defaults={
                    "category": category_objs[cat_slug],
                    "price": Decimal(price),
                    "description": description,
                    "stock": stock,
                    "is_active": True,
                },
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Створено нових товарів: {created_count}"))
        self.stdout.write(self.style.SUCCESS("Готово! Запустіть сервер та відкрийте каталог."))
