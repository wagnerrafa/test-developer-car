"""
Management command to populate the database with fake car data.

This command creates fake data for all car-related models including brands, colors,
engines, car names, car models, and cars. It uses bulk_create for optimal performance
when inserting large amounts of data.

Usage:
    python manage.py populate_cars --count 100
    python manage.py populate_cars --count 500 --clear
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from faker import Faker

from apps.cars.constants import FuelTypeChoices, TransmissionChoices
from apps.cars.models import Brand, Car, CarModel, CarName, Color, Engine


class Command(BaseCommand):
    """Command to populate the database with fake car data."""

    help = "Populate the database with fake car data using bulk_create for optimal performance"

    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            "--count",
            type=int,
            default=100,
            help="Number of cars to create (default: 100)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing data before populating",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=1000,
            help="Batch size for bulk_create operations (default: 1000)",
        )

    def handle(self, *args, **options):
        """Handle the command execution."""
        count = options["count"]
        clear = options["clear"]
        batch_size = options["batch_size"]

        if count <= 0:
            raise CommandError("Count must be a positive integer")

        self.faker = Faker("pt_BR")  # Use Brazilian Portuguese for more realistic data

        if clear:
            self.stdout.write("Clearing existing data...")
            self._clear_data()

        self.stdout.write(f"Creating {count} cars with related data...")

        try:
            with transaction.atomic():
                # Create base data first
                brands = self._create_brands()
                colors = self._create_colors()
                engines = self._create_engines()
                car_models = self._create_car_models()

                # Create car names (depends on brands)
                car_names = self._create_car_names(brands)

                # Create cars (depends on all other models)
                cars = self._create_cars(count, brands, colors, engines, car_names, car_models, batch_size)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully created:\n"
                    f"- {len(brands)} brands\n"
                    f"- {len(colors)} colors\n"
                    f"- {len(engines)} engines\n"
                    f"- {len(car_models)} car models\n"
                    f"- {len(car_names)} car names\n"
                    f"- {len(cars)} cars"
                )
            )

        except Exception as e:
            raise CommandError(f"Error creating data: {e!s}") from e

    def _clear_data(self):
        """Clear existing data from all car-related tables."""
        Car.objects.all().delete()
        CarName.objects.all().delete()
        CarModel.objects.all().delete()
        Engine.objects.all().delete()
        Color.objects.all().delete()
        Brand.objects.all().delete()

    def _create_brands(self):
        """Create fake brand data."""
        self.stdout.write("Creating brands...")

        # Pre-defined realistic car brands
        brand_names = [
            "Toyota",
            "Honda",
            "Ford",
            "Chevrolet",
            "Volkswagen",
            "Fiat",
            "Renault",
            "Nissan",
            "Hyundai",
            "Kia",
            "BMW",
            "Mercedes-Benz",
            "Audi",
            "Volvo",
            "Peugeot",
            "Citroën",
            "Mitsubishi",
            "Subaru",
            "Mazda",
            "Suzuki",
            "Jeep",
            "Dodge",
            "Chrysler",
            "Buick",
            "Cadillac",
            "Lincoln",
            "Acura",
            "Infiniti",
            "Lexus",
            "Genesis",
        ]

        brands = []
        for name in brand_names:
            brands.append(Brand(name=name, description=f"Marca {name} - {self.faker.sentence(nb_words=6)}"))

        Brand.objects.bulk_create(brands, ignore_conflicts=True)
        return list(Brand.objects.all())

    def _create_colors(self):
        """Create fake color data."""
        self.stdout.write("Creating colors...")

        # Pre-defined realistic car colors
        color_names = [
            "Branco",
            "Preto",
            "Prata",
            "Cinza",
            "Azul",
            "Vermelho",
            "Verde",
            "Amarelo",
            "Laranja",
            "Marrom",
            "Bege",
            "Dourado",
            "Roxo",
            "Rosa",
            "Chumbo",
            "Grafite",
            "Perolado",
            "Metálico",
        ]

        colors = []
        for name in color_names:
            colors.append(Color(name=name, description=f"Cor {name} - {self.faker.sentence(nb_words=4)}"))

        Color.objects.bulk_create(colors, ignore_conflicts=True)
        return list(Color.objects.all())

    def _create_engines(self):
        """Create fake engine data."""
        self.stdout.write("Creating engines...")

        # Generate realistic engine specifications
        engines = []
        for _ in range(50):  # Create 50 different engines
            displacement = f"{self.faker.random_int(min=1, max=6)}.{self.faker.random_int(min=0, max=9)}"
            power = self.faker.random_int(min=80, max=600)

            engines.append(
                Engine(
                    name=f"{displacement}L {power}cv",
                    description=f"Motor {displacement}L com {power} cavalos de potência",
                    displacement=displacement,
                    power=power,
                )
            )

        Engine.objects.bulk_create(engines, ignore_conflicts=True)
        return list(Engine.objects.all())

    def _create_car_models(self):
        """Create fake car model data."""
        self.stdout.write("Creating car models...")

        # Pre-defined realistic car model types
        model_types = [
            "Sedan",
            "Hatchback",
            "SUV",
            "Crossover",
            "Pickup",
            "Coupe",
            "Convertible",
            "Wagon",
            "Minivan",
            "Crossover",
            "Compact",
            "Luxury",
            "Sports",
            "Electric",
            "Hybrid",
        ]

        car_models = []
        for _ in range(100):  # Create 100 different car models
            model_type = self.faker.random_element(model_types)
            model_name = f"{model_type} {self.faker.word().title()}"

            car_models.append(
                CarModel(name=model_name, description=f"Modelo {model_name} - {self.faker.sentence(nb_words=8)}")
            )

        CarModel.objects.bulk_create(car_models, ignore_conflicts=True)
        return list(CarModel.objects.all())

    def _create_car_names(self, brands):
        """Create fake car name data."""
        self.stdout.write("Creating car names...")

        car_names = []
        for brand in brands:
            # Create 3-5 car names per brand
            for _ in range(self.faker.random_int(min=3, max=5)):
                car_name = f"{brand.name} {self.faker.word().title()}"
                year = self.faker.random_int(min=2015, max=2024)

                car_names.append(
                    CarName(name=f"{car_name} {year}", description=f"Carro {car_name} ano {year}", brand=brand)
                )

        CarName.objects.bulk_create(car_names, ignore_conflicts=True)
        return list(CarName.objects.all())

    def _create_cars(self, count, brands, colors, engines, car_names, car_models, batch_size):
        """Create fake car data using bulk_create."""
        self.stdout.write(f"Creating {count} cars...")

        cars = []
        fuel_types = [choice[0] for choice in FuelTypeChoices.choices]
        transmission_types = [choice[0] for choice in TransmissionChoices.choices]

        for _ in range(count):
            # Select random related objects
            brand = self.faker.random_element(brands)
            color = self.faker.random_element(colors)
            engine = self.faker.random_element(engines)
            car_name = self.faker.random_element([cn for cn in car_names if cn.brand == brand])
            car_model = self.faker.random_element(car_models)

            # Generate realistic car data
            year_manufacture = self.faker.random_int(min=2015, max=2024)
            year_model = year_manufacture + self.faker.random_int(min=0, max=1)

            # Ensure year_model is not greater than current year + 1
            if year_model > 2024:
                year_model = 2024

            cars.append(
                Car(
                    car_name=car_name,
                    car_model=car_model,
                    color=color,
                    engine=engine,
                    year_manufacture=year_manufacture,
                    year_model=year_model,
                    fuel_type=self.faker.random_element(fuel_types),
                    transmission=self.faker.random_element(transmission_types),
                    mileage=self.faker.random_int(min=0, max=200000),
                    doors=self.faker.random_element([2, 4, 5]),
                    price=round(self.faker.random_number(digits=6) / 100, 2),
                    description=f"Carro {car_name.name} - {self.faker.sentence(nb_words=10)}",
                )
            )

            # Use bulk_create in batches for better performance
            if len(cars) >= batch_size:
                Car.objects.bulk_create(cars, ignore_conflicts=True)
                self.stdout.write(f"Created batch of {len(cars)} cars...")
                cars = []

        # Create remaining cars
        if cars:
            Car.objects.bulk_create(cars, ignore_conflicts=True)
            self.stdout.write(f"Created final batch of {len(cars)} cars...")

        return list(Car.objects.all())
