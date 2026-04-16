import csv
from django.core.management.base import BaseCommand
from administrator.models import Category


class Command(BaseCommand):
    help = "Import categories from CSV and remove duplicates"

    def handle(self, *args, **kwargs):

        file_path = "Dataset/ecommerce_dataset/category.csv"   # CSV file near manage.py

        unique_categories = set()

        # 1️⃣ Read CSV
        with open(file_path, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:
                category_name = row['category_name'].strip()

                if category_name:
                    unique_categories.add(category_name)

        # 2️⃣ Insert into DB (no duplicates)
        for name in unique_categories:
            Category.objects.get_or_create(category_name=name)

        self.stdout.write(
            self.style.SUCCESS("✅ Categories imported successfully (duplicates removed)")
        )
