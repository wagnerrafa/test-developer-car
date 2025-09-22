"""Tests for the cars app."""

from apps.cars.models import Brand, Car, CarModel, CarName, Color, Engine
from drf_base_apps.core.abstract.tests import AbstractTest


class TestCarNameSuccess(AbstractTest):
    """
    Test class for successful car name operations.

    This class contains tests for the POST and GET methods of the car name endpoint,
    focusing on successful creation and listing of cars names.

    Attributes:
        path (str): The endpoint path being tested.
        http_method_names (list): List of HTTP methods allowed for testing.
        status_expected (dict): Expected status codes for different methods.

    Methods:
        test_api_a_post: Test method to verify the correctness of the POST request.
        test_api_b_get: Test method to verify the correctness of the GET request.

    """

    path = "car-name-list-create"
    http_method_names = ["get", "post"]
    status_expected = {"get": 200, "post": 201}

    def get_parameters(self):
        """Retorna parâmetros válidos para criação de campanha."""
        return {
            "brand_id": self.fake_model_data(Brand, 1)[0].id,
            "description": "Descrição da marca Chevrolet",
            "name": self.faker.name(),
        }


class TestCarNameAlreadyName(AbstractTest):
    """
    Test class for unsuccessful car name operations.

    This class contains tests for the POST and GET methods of the car name endpoint,
    focusing on unsuccessful creation of already car name.

    Attributes:
        path (str): The endpoint path being tested.
        http_method_names (list): List of HTTP methods allowed for testing.
        status_expected (dict): Expected status codes for different methods.

    Methods:
        test_api_a_post: Test method to verify the correctness of the POST request.

    """

    path = "car-name-list-create"
    http_method_names = ["post"]
    status_expected = {"post": 400}

    def get_parameters(self):
        """Retorna parâmetros válidos para criação de campanha."""
        parameters = {
            "brand_id": self.fake_model_data(Brand, 1)[0].id,
            "description": "Descrição da marca",
            "name": self.faker.name(),
        }

        self.fake_model_data(CarName, 1, **parameters)

        return parameters


class TestBrandSuccess(AbstractTest):
    """
    Test class for successful brand operations.

    This class contains tests for the POST and GET methods of the brand endpoint,
    focusing on successful creation and listing of brands.

    Attributes:
        path (str): The endpoint path being tested.
        http_method_names (list): List of HTTP methods allowed for testing.
        status_expected (dict): Expected status codes for different methods.

    Methods:
        test_api_a_post: Test method to verify the correctness of the POST request.
        test_api_b_get: Test method to verify the correctness of the GET request.

    """

    path = "brand-list-create"
    http_method_names = ["get", "post"]
    status_expected = {"get": 200, "post": 201}

    def get_parameters(self):
        """Retorna parâmetros válidos para criação de marca."""
        return {"description": "Descrição da marca Chevrolet", "name": self.faker.company()}


class TestBrandAlreadyName(AbstractTest):
    """
    Test class for unsuccessful brand operations.

    This class contains tests for the POST method of the brand endpoint,
    focusing on unsuccessful creation of already existing brand.

    Attributes:
        path (str): The endpoint path being tested.
        http_method_names (list): List of HTTP methods allowed for testing.
        status_expected (dict): Expected status codes for different methods.

    Methods:
        test_api_a_post: Test method to verify the correctness of the POST request.

    """

    path = "brand-list-create"
    http_method_names = ["post"]
    status_expected = {"post": 400}

    def get_parameters(self):
        """Retorna parâmetros válidos para criação de marca."""
        parameters = {"description": "Descrição da marca", "name": self.faker.company()}

        self.fake_model_data(Brand, 1, **parameters)

        return parameters


class TestBrandDetailSuccess(AbstractTest):
    """
    Test class for successful brand detail operations.

    This class contains tests for the PUT method of the brand detail endpoint,
    focusing on successful update brands.

    Attributes:
        path (str): The endpoint path being tested.
        http_method_names (list): List of HTTP methods allowed for testing.
        status_expected (dict): Expected status codes for different methods.

    Methods:
        test_api_a_put: Test method to verify the correctness of the PUT request.

    """

    path = "brand-detail-put"
    http_method_names = ["put", "get"]
    status_expected = {"put": 200, "get": 200}

    def setUp(self):
        """Set up test environment and create test brand."""
        super().setUp()
        self.test_brand = self.fake_model_data(Brand, 1)[0]
        self.parameters = {"name": self.faker.company(), "description": "Descrição atualizada"}
        self.path_parameters = {"id": self.test_brand.id}


class TestColorSuccess(AbstractTest):
    """
    Test class for successful color operations.

    This class contains tests for the POST and GET methods of the color endpoint,
    focusing on successful creation and listing of colors.

    Attributes:
        path (str): The endpoint path being tested.
        http_method_names (list): List of HTTP methods allowed for testing.
        status_expected (dict): Expected status codes for different methods.

    Methods:
        test_api_a_post: Test method to verify the correctness of the POST request.
        test_api_b_get: Test method to verify the correctness of the GET request.

    """

    path = "color-list-create"
    http_method_names = ["get", "post"]
    status_expected = {"get": 200, "post": 201}

    def get_parameters(self):
        """Retorna parâmetros válidos para criação de cor."""
        return {"description": "Descrição da cor", "name": self.faker.color_name()}


class TestColorAlreadyName(AbstractTest):
    """
    Test class for unsuccessful color operations.

    This class contains tests for the POST method of the color endpoint,
    focusing on unsuccessful creation of already existing color.

    Attributes:
        path (str): The endpoint path being tested.
        http_method_names (list): List of HTTP methods allowed for testing.
        status_expected (dict): Expected status codes for different methods.

    Methods:
        test_api_a_post: Test method to verify the correctness of the POST request.

    """

    path = "color-list-create"
    http_method_names = ["post"]
    status_expected = {"post": 400}

    def get_parameters(self):
        """Retorna parâmetros válidos para criação de cor."""
        parameters = {"description": "Descrição da cor", "name": self.faker.color_name()}

        self.fake_model_data(Color, 1, **parameters)

        return parameters


class TestColorDetailSuccess(AbstractTest):
    """
    Test class for successful color detail operations.

    This class contains tests for the PUT method of the color detail endpoint,
    focusing on successful update colors.

    Attributes:
        path (str): The endpoint path being tested.
        http_method_names (list): List of HTTP methods allowed for testing.
        status_expected (dict): Expected status codes for different methods.

    Methods:
        test_api_a_put: Test method to verify the correctness of the PUT request.

    """

    path = "color-detail-put"
    http_method_names = ["put", "get"]
    status_expected = {"put": 200, "get": 200}

    def setUp(self):
        """Set up test environment and create test color."""
        super().setUp()
        self.test_color = self.fake_model_data(Color, 1)[0]
        self.parameters = {"name": self.faker.color_name(), "description": "Descrição atualizada"}
        self.path_parameters = {"id": self.test_color.id}


class TestEngineSuccess(AbstractTest):
    """
    Test class for successful engine operations.

    This class contains tests for the POST and GET methods of the engine endpoint,
    focusing on successful creation and listing of engines.

    Attributes:
        path (str): The endpoint path being tested.
        http_method_names (list): List of HTTP methods allowed for testing.
        status_expected (dict): Expected status codes for different methods.

    Methods:
        test_api_a_post: Test method to verify the correctness of the POST request.
        test_api_b_get: Test method to verify the correctness of the GET request.

    """

    path = "engine-list-create"
    http_method_names = ["get", "post"]
    status_expected = {"get": 200, "post": 201}

    def get_parameters(self):
        """Retorna parâmetros válidos para criação de motor."""
        return {
            "description": "Descrição do motor",
            "displacement": "2.0",
            "power": 200,
            "name": f"{self.faker.random_int(min=1, max=3)}.{self.faker.random_int(min=0, max=9)}",
        }


class TestEngineAlreadyName(AbstractTest):
    """
    Test class for unsuccessful engine operations.

    This class contains tests for the POST method of the engine endpoint,
    focusing on unsuccessful creation of already existing engine.

    Attributes:
        path (str): The endpoint path being tested.
        http_method_names (list): List of HTTP methods allowed for testing.
        status_expected (dict): Expected status codes for different methods.

    Methods:
        test_api_a_post: Test method to verify the correctness of the POST request.

    """

    path = "engine-list-create"
    http_method_names = ["post"]
    status_expected = {"post": 400}

    def get_parameters(self):
        """Retorna parâmetros válidos para criação de motor."""
        parameters = {
            "description": "Descrição do motor",
            "name": f"{self.faker.random_int(min=1, max=3)}.{self.faker.random_int(min=0, max=9)}",
        }

        self.fake_model_data(Engine, 1, **parameters)

        return parameters


class TestEngineDetailSuccess(AbstractTest):
    """
    Test class for successful engine detail operations.

    This class contains tests for the PUT method of the engine detail endpoint,
    focusing on successful update engines.

    Attributes:
        path (str): The endpoint path being tested.
        http_method_names (list): List of HTTP methods allowed for testing.
        status_expected (dict): Expected status codes for different methods.

    Methods:
        test_api_a_put: Test method to verify the correctness of the PUT request.

    """

    path = "engine-detail-put"
    http_method_names = ["put", "get"]
    status_expected = {"put": 200, "get": 200}

    def setUp(self):
        """Set up test environment and create test engine."""
        super().setUp()
        self.test_engine = self.fake_model_data(Engine, 1)[0]
        self.parameters = {
            "name": f"{self.faker.random_int(min=1, max=3)}.{self.faker.random_int(min=0, max=9)}",
            "description": "Descrição atualizada",
            "displacement": "2.5",
            "power": 250,
        }
        self.path_parameters = {"id": self.test_engine.id}


class TestCarModelSuccess(AbstractTest):
    """
    Test class for successful car model operations.

    This class contains tests for the POST and GET methods of the car model endpoint,
    focusing on successful creation and listing of car models.

    Attributes:
        path (str): The endpoint path being tested.
        http_method_names (list): List of HTTP methods allowed for testing.
        status_expected (dict): Expected status codes for different methods.

    Methods:
        test_api_a_post: Test method to verify the correctness of the POST request.
        test_api_b_get: Test method to verify the correctness of the GET request.

    """

    path = "car-model-list-create"
    http_method_names = ["get", "post"]
    status_expected = {"get": 200, "post": 201}

    def get_parameters(self):
        """Retorna parâmetros válidos para criação de modelo de carro."""
        return {"description": "Descrição do modelo", "name": self.faker.word().title()}


class TestCarModelAlreadyName(AbstractTest):
    """
    Test class for unsuccessful car model operations.

    This class contains tests for the POST method of the car model endpoint,
    focusing on unsuccessful creation of already existing car model.

    Attributes:
        path (str): The endpoint path being tested.
        http_method_names (list): List of HTTP methods allowed for testing.
        status_expected (dict): Expected status codes for different methods.

    Methods:
        test_api_a_post: Test method to verify the correctness of the POST request.

    """

    path = "car-model-list-create"
    http_method_names = ["post"]
    status_expected = {"post": 400}

    def get_parameters(self):
        """Retorna parâmetros válidos para criação de modelo de carro."""
        parameters = {"description": "Descrição do modelo", "name": self.faker.word().title()}

        self.fake_model_data(CarModel, 1, **parameters)

        return parameters


class TestCarModelDetailSuccess(AbstractTest):
    """
    Test class for successful car model detail operations.

    This class contains tests for the PUT method of the car model detail endpoint,
    focusing on successful update car models.

    Attributes:
        path (str): The endpoint path being tested.
        http_method_names (list): List of HTTP methods allowed for testing.
        status_expected (dict): Expected status codes for different methods.

    Methods:
        test_api_a_put: Test method to verify the correctness of the PUT request.

    """

    path = "car-model-detail-put"
    http_method_names = ["put", "get"]
    status_expected = {"put": 200, "get": 200}

    def setUp(self):
        """Set up test environment and create test car model."""
        super().setUp()
        self.test_car_model = self.fake_model_data(CarModel, 1)[0]
        self.parameters = {"name": self.faker.word().title(), "description": "Descrição atualizada"}
        self.path_parameters = {"id": self.test_car_model.id}


class TestCarNameDetailSuccess(AbstractTest):
    """
    Test class for successful car name detail operations.

    This class contains tests for the PUT method of the car name detail endpoint,
    focusing on successful update car names.

    Attributes:
        path (str): The endpoint path being tested.
        http_method_names (list): List of HTTP methods allowed for testing.
        status_expected (dict): Expected status codes for different methods.

    Methods:
        test_api_a_put: Test method to verify the correctness of the PUT request.

    """

    path = "car-name-detail-put"
    http_method_names = ["put", "get"]
    status_expected = {"put": 200, "get": 200}

    def setUp(self):
        """Set up test environment and create test car name."""
        super().setUp()
        brand = self.fake_model_data(Brand, 1)[0]
        self.test_car_name = self.fake_model_data(CarName, 1, brand=brand)[0]
        self.parameters = {"name": self.faker.name(), "description": "Descrição atualizada", "brand_id": brand.id}
        self.path_parameters = {"id": self.test_car_name.id}


class TestCarSuccess(AbstractTest):
    """
    Test class for successful car operations.

    This class contains tests for the POST and GET methods of the car endpoint,
    focusing on successful creation and listing of cars.

    Attributes:
        path (str): The endpoint path being tested.
        http_method_names (list): List of HTTP methods allowed for testing.
        status_expected (dict): Expected status codes for different methods.

    Methods:
        test_api_a_post: Test method to verify the correctness of the POST request.
        test_api_b_get: Test method to verify the correctness of the GET request.

    """

    path = "car-list-create"
    http_method_names = ["get", "post"]
    status_expected = {"get": 200, "post": 201}

    def get_parameters(self):
        """Retorna parâmetros válidos para criação de carro."""
        brand = self.fake_model_data(Brand, 1)[0]
        color = self.fake_model_data(Color, 1)[0]
        engine = self.fake_model_data(Engine, 1)[0]
        car_name = self.fake_model_data(CarName, 1, brand=brand)[0]
        car_model = self.fake_model_data(CarModel, 1)[0]

        return {
            "car_name_id": car_name.id,
            "car_model_id": car_model.id,
            "color_id": color.id,
            "engine_id": engine.id,
            "year_manufacture": self.faker.random_int(min=2000, max=2024),
            "year_model": self.faker.random_int(min=2000, max=2024),
            "fuel_type": "gasoline",
            "transmission": "manual",
            "mileage": self.faker.random_int(min=0, max=200000),
            "doors": self.faker.random_int(min=2, max=5),
            "price": round(self.faker.random_number(digits=5) / 100, 2),
            "description": "Descrição do carro",
        }


class TestCarDetailSuccess(AbstractTest):
    """
    Test class for successful car detail operations.

    This class contains tests for the PUT method of the car detail endpoint,
    focusing on successful update cars.

    Attributes:
        path (str): The endpoint path being tested.
        http_method_names (list): List of HTTP methods allowed for testing.
        status_expected (dict): Expected status codes for different methods.

    Methods:
        test_api_a_put: Test method to verify the correctness of the PUT request.

    """

    path = "car-detail-put"
    http_method_names = ["put", "get"]
    status_expected = {"put": 200, "get": 200}

    def setUp(self):
        """Set up test environment and create test car."""
        super().setUp()
        self.test_car = self.fake_model_data(Car, 1)[0]
        self.parameters = {"name": self.faker.name()}
        self.path_parameters = {"id": self.test_car.id}
