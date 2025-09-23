"""
API views for managing car-related objects.

This module defines API classes that provide HTTP methods for managing Car objects models.
It is extended from an AbstractViewApi class and includes a CheckHasPermission permission class for authorization.
API's respond with JSON data and use rest_framework.schemas.openapi.AutoSchema to generate the API documents.
API classes use the Car model and schema Car to work with data.
"""

from apps.cars.models import Brand, Car, CarModel, CarName, Color, Engine
from apps.cars.schemas import (
    BrandDetailSchema,
    BrandSchema,
    CarDetailSchema,
    CarModelDetailSchema,
    CarModelSchema,
    CarNameDetailSchema,
    CarNameSchema,
    CarSchema,
    ColorDetailSchema,
    ColorSchema,
    EngineDetailSchema,
    EngineSchema,
)
from drf_base_apps.core.abstract.views import AbstractViewApi
from drf_base_apps.utils import _


class CarApi(AbstractViewApi):
    """
    Define the CarApi view class for handling HTTP methods related to Car.

    This view class extends the AbstractViewApi class, which provides a basic implementation
    for common API actions. The CarApi supports HTTP POST and GET methods, and uses the CarSchema
    serializer for input/output validation. The view requires authenticated users with appropriate
    permissions to access the API endpoints, as specified by the IsAuthenticated and CheckHasPermission
    permission classes.

    Attributes:
        http_method_names (list): A list of HTTP methods supported by this view.
        serializer_class (class): The serializer class for input/output validation.
        permission_classes (list): A list of permission classes for user authentication and authorization.
        model (class): The model class associated with this view.

        query_params (list): A list of dictionaries, each specifying a query parameter for the API.

    Examples:
        To retrieve car with a matching description:
        ```
        GET /api/v1/car/?car=car_name
        ```

    """

    http_method_names = ["get", "post"]
    serializer_class = CarSchema
    model = Car
    pagination = True
    docs = {
        "init": _(
            """Represents the entire Car.
                """
        ),
        "get": _(
            """This method handles GET requests for the view. It retrieves a specific Car object using the given
            calculation_id from the query parameters and serializes the result into JSON format before returning it as
             an HTTP response.

                Returns:
                    JsonResponse: An HTTP response containing the serialized Car data retrieved.
                """
        ),
    }


class CarDetailApi(AbstractViewApi):
    """
    Define the detail CarApi view class for handling HTTP methods related to Car.

    This view class extends the AbstractViewApi class, which provides a basic implementation
    for common API actions. The CarApi supports HTTP POST and GET methods, and uses the CarSchema
    serializer for input/output validation. The view requires authenticated users with appropriate
    permissions to access the API endpoints, as specified by the IsAuthenticated and CheckHasPermission
    permission classes.

    Attributes:
        http_method_names (list): A list of HTTP methods supported by this view.
        serializer_class (class): The serializer class for input/output validation.
        permission_classes (list): A list of permission classes for user authentication and authorization.
        model (class): The model class associated with this view.

        query_params (list): A list of dictionaries, each specifying a query parameter for the API.

    Examples:
        To retrieve car with a matching description:
        ```
        GET /api/v1/car/?car=car_name
        ```

    """

    http_method_names = ["get", "put", "delete"]
    serializer_class = CarDetailSchema
    model = Car
    pagination = False
    docs = {
        "init": _(
            """Represents the entire Car.
                """
        ),
        "get": _(
            """This method handles GET requests for the view. It retrieves a specific Car object using the given
            calculation_id from the query parameters and serializes the result into JSON format before returning it as
             an HTTP response.

                Returns:
                    JsonResponse: An HTTP response containing the serialized Car data retrieved.
                """
        ),
    }


class BrandApi(AbstractViewApi):
    """
    Define the BrandApi view class for handling HTTP methods related to Brand.

    This view class extends the AbstractViewApi class, which provides a basic implementation
    for common API actions. The BrandApi supports HTTP POST and GET methods, and uses the BrandSchema
    serializer for input/output validation. The view requires authenticated users with appropriate
    permissions to access the API endpoints, as specified by the IsAuthenticated and CheckHasPermission
    permission classes.

    Attributes:
        http_method_names (list): A list of HTTP methods supported by this view.
        serializer_class (class): The serializer class for input/output validation.
        permission_classes (list): A list of permission classes for user authentication and authorization.
        model (class): The model class associated with this view.

        query_params (list): A list of dictionaries, each specifying a query parameter for the API.

    Examples:
        To retrieve brand with a matching description:
        ```
        GET /api/v1/brand/?description=brand_name
        ```

    """

    http_method_names = ["get", "post"]
    serializer_class = BrandSchema
    model = Brand
    pagination = True

    docs = {
        "init": _(
            """Represents the entire Brand.
                """
        ),
        "get": _(
            """This method handles GET requests for the view. It retrieves a specific Brand object using the given
            description from the query parameters and serializes the result into JSON format before returning it as
             an HTTP response.

                Returns:
                    JsonResponse: An HTTP response containing the serialized Brand data retrieved.
                """
        ),
    }


class BrandDetailApi(AbstractViewApi):
    """
    Define the detail BrandApi view class for handling HTTP methods related to Brand.

    This view class extends the AbstractViewApi class, which provides a basic implementation
    for common API actions. The BrandDetailApi supports HTTP GET and PUT methods, and uses the BrandDetailSchema
    serializer for input/output validation. The view requires authenticated users with appropriate
    permissions to access the API endpoints, as specified by the IsAuthenticated and CheckHasPermission
    permission classes.

    Attributes:
        http_method_names (list): A list of HTTP methods supported by this view.
        serializer_class (class): The serializer class for input/output validation.
        permission_classes (list): A list of permission classes for user authentication and authorization.
        model (class): The model class associated with this view.

        query_params (list): A list of dictionaries, each specifying a query parameter for the API.

    Examples:
        To retrieve brand with a matching description:
        ```
        GET /api/v1/brand/?description=brand_name
        ```

    """

    http_method_names = ["get", "put"]
    serializer_class = BrandDetailSchema
    model = Brand
    pagination = False

    docs = {
        "init": _(
            """Represents the entire Brand.
                """
        ),
        "get": _(
            """This method handles GET requests for the view. It retrieves a specific Brand object using the given
            brand_id from the query parameters and serializes the result into JSON format before returning it as
             an HTTP response.

                Returns:
                    JsonResponse: An HTTP response containing the serialized Brand data retrieved.
                """
        ),
    }


class ColorApi(AbstractViewApi):
    """
    Define the ColorApi view class for handling HTTP methods related to Color.

    This view class extends the AbstractViewApi class, which provides a basic implementation
    for common API actions. The ColorApi supports HTTP POST and GET methods, and uses the ColorSchema
    serializer for input/output validation. The view requires authenticated users with appropriate
    permissions to access the API endpoints, as specified by the IsAuthenticated and CheckHasPermission
    permission classes.

    Attributes:
        http_method_names (list): A list of HTTP methods supported by this view.
        serializer_class (class): The serializer class for input/output validation.
        permission_classes (list): A list of permission classes for user authentication and authorization.
        model (class): The model class associated with this view.

        query_params (list): A list of dictionaries, each specifying a query parameter for the API.

    Examples:
        To retrieve color with a matching description:
        ```
        GET /api/v1/color/?description=color_name
        ```

    """

    http_method_names = ["get", "post"]
    serializer_class = ColorSchema
    model = Color
    pagination = True

    docs = {
        "init": _(
            """Represents the entire Color.
                """
        ),
        "get": _(
            """This method handles GET requests for the view. It retrieves a specific Color object using the given
            description from the query parameters and serializes the result into JSON format before returning it as
             an HTTP response.

                Returns:
                    JsonResponse: An HTTP response containing the serialized Color data retrieved.
                """
        ),
    }


class ColorDetailApi(AbstractViewApi):
    """
    Define the detail ColorApi view class for handling HTTP methods related to Color.

    This view class extends the AbstractViewApi class, which provides a basic implementation
    for common API actions. The ColorDetailApi supports HTTP GET and PUT methods, and uses the ColorDetailSchema
    serializer for input/output validation. The view requires authenticated users with appropriate
    permissions to access the API endpoints, as specified by the IsAuthenticated and CheckHasPermission
    permission classes.

    Attributes:
        http_method_names (list): A list of HTTP methods supported by this view.
        serializer_class (class): The serializer class for input/output validation.
        permission_classes (list): A list of permission classes for user authentication and authorization.
        model (class): The model class associated with this view.

        query_params (list): A list of dictionaries, each specifying a query parameter for the API.

    Examples:
        To retrieve color with a matching description:
        ```
        GET /api/v1/color/?description=color_name
        ```

    """

    http_method_names = ["get", "put", "delete"]
    serializer_class = ColorDetailSchema
    model = Color
    pagination = False

    docs = {
        "init": _(
            """Represents the entire Color.
                """
        ),
        "get": _(
            """This method handles GET requests for the view. It retrieves a specific Color object using the given
            color_id from the query parameters and serializes the result into JSON format before returning it as
             an HTTP response.

                Returns:
                    JsonResponse: An HTTP response containing the serialized Color data retrieved.
                """
        ),
    }


class EngineApi(AbstractViewApi):
    """
    Define the EngineApi view class for handling HTTP methods related to Engine.

    This view class extends the AbstractViewApi class, which provides a basic implementation
    for common API actions. The EngineApi supports HTTP POST and GET methods, and uses the EngineSchema
    serializer for input/output validation. The view requires authenticated users with appropriate
    permissions to access the API endpoints, as specified by the IsAuthenticated and CheckHasPermission
    permission classes.

    Attributes:
        http_method_names (list): A list of HTTP methods supported by this view.
        serializer_class (class): The serializer class for input/output validation.
        permission_classes (list): A list of permission classes for user authentication and authorization.
        model (class): The model class associated with this view.

        query_params (list): A list of dictionaries, each specifying a query parameter for the API.

    Examples:
        To retrieve engine with a matching description:
        ```
        GET /api/v1/engine/?description=engine_name
        ```

    """

    http_method_names = ["get", "post"]
    serializer_class = EngineSchema
    model = Engine
    pagination = True

    docs = {
        "init": _(
            """Represents the entire Engine.
                """
        ),
        "get": _(
            """This method handles GET requests for the view. It retrieves a specific Engine object using the given
            description from the query parameters and serializes the result into JSON format before returning it as
             an HTTP response.

                Returns:
                    JsonResponse: An HTTP response containing the serialized Engine data retrieved.
                """
        ),
    }


class EngineDetailApi(AbstractViewApi):
    """
    Define the detail EngineApi view class for handling HTTP methods related to Engine.

    This view class extends the AbstractViewApi class, which provides a basic implementation
    for common API actions. The EngineDetailApi supports HTTP GET and PUT methods, and uses the EngineDetailSchema
    serializer for input/output validation. The view requires authenticated users with appropriate
    permissions to access the API endpoints, as specified by the IsAuthenticated and CheckHasPermission
    permission classes.

    Attributes:
        http_method_names (list): A list of HTTP methods supported by this view.
        serializer_class (class): The serializer class for input/output validation.
        permission_classes (list): A list of permission classes for user authentication and authorization.
        model (class): The model class associated with this view.

        query_params (list): A list of dictionaries, each specifying a query parameter for the API.

    Examples:
        To retrieve engine with a matching description:
        ```
        GET /api/v1/engine/?description=engine_name
        ```

    """

    http_method_names = ["get", "put", "delete"]
    serializer_class = EngineDetailSchema
    model = Engine
    pagination = False

    docs = {
        "init": _(
            """Represents the entire Engine.
                """
        ),
        "get": _(
            """This method handles GET requests for the view. It retrieves a specific Engine object using the given
            engine_id from the query parameters and serializes the result into JSON format before returning it as
             an HTTP response.

                Returns:
                    JsonResponse: An HTTP response containing the serialized Engine data retrieved.
                """
        ),
    }


class CarNameApi(AbstractViewApi):
    """
    Define the CarNameApi view class for handling HTTP methods related to CarName.

    This view class extends the AbstractViewApi class, which provides a basic implementation
    for common API actions. The CarNameApi supports HTTP POST and GET methods, and uses the CarNameSchema
    serializer for input/output validation. The view requires authenticated users with appropriate
    permissions to access the API endpoints, as specified by the IsAuthenticated and CheckHasPermission
    permission classes.

    Attributes:
        http_method_names (list): A list of HTTP methods supported by this view.
        serializer_class (class): The serializer class for input/output validation.
        permission_classes (list): A list of permission classes for user authentication and authorization.
        model (class): The model class associated with this view.

        query_params (list): A list of dictionaries, each specifying a query parameter for the API.

    Examples:
        To retrieve car name with a matching description:
        ```
        GET /api/v1/car-name/?description=car_name
        ```

    """

    http_method_names = ["get", "post"]
    serializer_class = CarNameSchema
    model = CarName
    pagination = True

    docs = {
        "init": _(
            """Represents the entire CarName.
                """
        ),
        "get": _(
            """This method handles GET requests for the view. It retrieves a specific CarName object using the given
            description from the query parameters and serializes the result into JSON format before returning it as
             an HTTP response.

                Returns:
                    JsonResponse: An HTTP response containing the serialized CarName data retrieved.
                """
        ),
    }


class CarNameDetailApi(AbstractViewApi):
    """
    Define the detail CarNameApi view class for handling HTTP methods related to CarName.

    This view class extends the AbstractViewApi class, which provides a basic implementation
    for common API actions. The CarNameDetailApi supports HTTP GET and PUT methods, and uses the CarNameDetailSchema
    serializer for input/output validation. The view requires authenticated users with appropriate
    permissions to access the API endpoints, as specified by the IsAuthenticated and CheckHasPermission
    permission classes.

    Attributes:
        http_method_names (list): A list of HTTP methods supported by this view.
        serializer_class (class): The serializer class for input/output validation.
        permission_classes (list): A list of permission classes for user authentication and authorization.
        model (class): The model class associated with this view.

        query_params (list): A list of dictionaries, each specifying a query parameter for the API.

    Examples:
        To retrieve car name with a matching description:
        ```
        GET /api/v1/car-name/?description=car_name
        ```

    """

    http_method_names = ["get", "put", "delete"]
    serializer_class = CarNameDetailSchema
    model = CarName
    pagination = False

    docs = {
        "init": _(
            """Represents the entire CarName.
                """
        ),
        "get": _(
            """This method handles GET requests for the view. It retrieves a specific CarName object using the given
            car_name_id from the query parameters and serializes the result into JSON format before returning it as
             an HTTP response.

                Returns:
                    JsonResponse: An HTTP response containing the serialized CarName data retrieved.
                """
        ),
    }


class CarModelApi(AbstractViewApi):
    """
    Define the CarModelApi view class for handling HTTP methods related to CarModel.

    This view class extends the AbstractViewApi class, which provides a basic implementation
    for common API actions. The CarModelApi supports HTTP POST and GET methods, and uses the CarModelSchema
    serializer for input/output validation. The view requires authenticated users with appropriate
    permissions to access the API endpoints, as specified by the IsAuthenticated and CheckHasPermission
    permission classes.

    Attributes:
        http_method_names (list): A list of HTTP methods supported by this view.
        serializer_class (class): The serializer class for input/output validation.
        permission_classes (list): A list of permission classes for user authentication and authorization.
        model (class): The model class associated with this view.

        query_params (list): A list of dictionaries, each specifying a query parameter for the API.

    Examples:
        To retrieve car model with a matching description:
        ```
        GET /api/v1/car-model/?description=car_model
        ```

    """

    http_method_names = ["get", "post"]
    serializer_class = CarModelSchema
    model = CarModel
    pagination = True

    docs = {
        "init": _(
            """Represents the entire CarModel.
                """
        ),
        "get": _(
            """This method handles GET requests for the view. It retrieves a specific CarModel object using the given
            description from the query parameters and serializes the result into JSON format before returning it as
             an HTTP response.

                Returns:
                    JsonResponse: An HTTP response containing the serialized CarModel data retrieved.
                """
        ),
    }


class CarModelDetailApi(AbstractViewApi):
    """
    Define the detail CarModelApi view class for handling HTTP methods related to CarModel.

    This view class extends the AbstractViewApi class, which provides a basic implementation
    for common API actions. The CarModelDetailApi supports HTTP GET and PUT methods, and uses the CarModelDetailSchema
    serializer for input/output validation. The view requires authenticated users with appropriate
    permissions to access the API endpoints, as specified by the IsAuthenticated and CheckHasPermission
    permission classes.

    Attributes:
        http_method_names (list): A list of HTTP methods supported by this view.
        serializer_class (class): The serializer class for input/output validation.
        permission_classes (list): A list of permission classes for user authentication and authorization.
        model (class): The model class associated with this view.

        query_params (list): A list of dictionaries, each specifying a query parameter for the API.

    Examples:
        To retrieve car model with a matching description:
        ```
        GET /api/v1/car-model/?description=car_model
        ```

    """

    http_method_names = ["get", "put", "delete"]
    serializer_class = CarModelDetailSchema
    model = CarModel
    pagination = False

    docs = {
        "init": _(
            """Represents the entire CarModel.
                """
        ),
        "get": _(
            """This method handles GET requests for the view. It retrieves a specific CarModel object using the given
            car_model_id from the query parameters and serializes the result into JSON format before returning it as
             an HTTP response.

                Returns:
                    JsonResponse: An HTTP response containing the serialized CarModel data retrieved.
                """
        ),
    }
