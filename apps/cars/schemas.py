"""
Serializes the fields of the Car model for use in the API.

This module defines a Django REST Framework serializer that inherits from both
`serializers.ModelSerializer` and a custom `AbstractModelSchema` class. The serializer
converts instances of the `Car` model to and from JSON format, and
validates incoming data based on the model's fields.

Attributes:
    - `Meta`: A nested class that specifies metadata for the serializer. The `model`
      attribute specifies the model class that the serializer should be based on, and
      `fields` lists the names of all fields that should be included in the serialized
      representation.

"""

from rest_framework import serializers

from apps.cars.models import Brand, Car, CarModel, CarName, Color, Engine
from drf_base_apps.schemas import AbstractDescriptionSchema


class BrandSchema(AbstractDescriptionSchema):
    """
    Serializes the fields of the Brand model for use in the API.

    This class defines a Django REST Framework serializer that inherits from a custom
    AbstractDescriptionSchema class. The serializer converts instances of the Brand
    model to and from JSON format, and validates incoming data based on the model's fields.

    Usage example:
    serializer = BrandSchema()
    """

    class Meta:
        """Meta options for BrandSchema."""

        model = Brand
        fields = "__all__"


class BrandDetailSchema(BrandSchema):
    """
    Serializes the fields of the Brand model for use in the API.

    This class defines a Django REST Framework serializer that inherits from a custom
    AbstractDescriptionSchema class. The serializer converts instances of the Brand
    model to and from JSON format, and validates incoming data based on the model's fields.

    Usage example:
    serializer = BrandSchema()
    """

    class Meta:
        """Meta options for BrandDetailSchema."""

        model = Brand
        fields = "__all__"
        non_required_fields = "__all__"


class ColorSchema(AbstractDescriptionSchema):
    """
    Serializes the fields of the Color model for use in the API.

    This class defines a Django REST Framework serializer that inherits from a custom
    AbstractDescriptionSchema class. The serializer converts instances of the Color
    model to and from JSON format, and validates incoming data based on the model's fields.

    Usage example:
    serializer = ColorSchema()
    """

    class Meta:
        """Meta options for ColorSchema."""

        model = Color
        fields = "__all__"


class ColorDetailSchema(ColorSchema):
    """
    Serializes the fields of the Color model for use in the API.

    This class defines a Django REST Framework serializer that inherits from a custom
    AbstractDescriptionSchema class. The serializer converts instances of the Color
    model to and from JSON format, and validates incoming data based on the model's fields.

    Usage example:
    serializer = ColorSchema()
    """

    class Meta:
        """Meta options for ColorDetailSchema."""

        model = Color
        fields = "__all__"
        non_required_fields = "__all__"


class EngineSchema(AbstractDescriptionSchema):
    """
    Serializes the fields of the Engine model for use in the API.

    This class defines a Django REST Framework serializer that inherits from a custom
    AbstractDescriptionSchema class. The serializer converts instances of the Engine
    model to and from JSON format, and validates incoming data based on the model's fields.

    Usage example:
    serializer = EngineSchema()
    """

    class Meta:
        """Meta options for EngineSchema."""

        model = Engine
        fields = "__all__"


class EngineDetailSchema(EngineSchema):
    """
    Serializes the fields of the Engine model for use in the API.

    This class defines a Django REST Framework serializer that inherits from a custom
    AbstractDescriptionSchema class. The serializer converts instances of the Engine
    model to and from JSON format, and validates incoming data based on the model's fields.

    Usage example:
    serializer = EngineSchema()
    """

    class Meta:
        """Meta options for EngineDetailSchema."""

        model = Engine
        fields = "__all__"
        non_required_fields = "__all__"


class CarNameSchema(AbstractDescriptionSchema):
    """
    Serializes the fields of the CarName model for use in the API.

    This class defines a Django REST Framework serializer that inherits from a custom
    AbstractDescriptionSchema class. The serializer converts instances of the CarName
    model to and from JSON format, and validates incoming data based on the model's fields.

    Usage example:
    serializer = CarNameSchema()
    """

    brand_id = serializers.UUIDField()
    brand = BrandSchema(read_only=True)

    class Meta:
        """Meta options for CarNameSchema."""

        model = CarName
        fields = "__all__"
        read_only_fields = ("brand",)


class CarNameDetailSchema(CarNameSchema):
    """
    Serializes the fields of the CarName model for use in the API.

    This class defines a Django REST Framework serializer that inherits from a custom
    AbstractDescriptionSchema class. The serializer converts instances of the CarName
    model to and from JSON format, and validates incoming data based on the model's fields.

    Usage example:
    serializer = CarNameSchema()
    """

    brand_id = serializers.UUIDField(required=False)

    class Meta:
        """Meta options for CarNameDetailSchema."""

        model = CarName
        fields = "__all__"
        non_required_fields = "__all__"


class CarModelSchema(AbstractDescriptionSchema):
    """
    Serializes the fields of the CarModel model for use in the API.

    This class defines a Django REST Framework serializer that inherits from a custom
    AbstractDescriptionSchema class. The serializer converts instances of the CarModel
    model to and from JSON format, and validates incoming data based on the model's fields.

    Usage example:
    serializer = CarModelSchema()
    """

    class Meta:
        """Meta options for CarModelSchema."""

        model = CarModel
        fields = "__all__"


class CarModelDetailSchema(CarModelSchema):
    """
    Serializes the fields of the CarModel model for use in the API.

    This class defines a Django REST Framework serializer that inherits from a custom
    AbstractDescriptionSchema class. The serializer converts instances of the CarModel
    model to and from JSON format, and validates incoming data based on the model's fields.

    Usage example:
    serializer = CarModelSchema()
    """

    class Meta:
        """Meta options for CarModelDetailSchema."""

        model = CarModel
        fields = "__all__"
        non_required_fields = "__all__"


class CarSchema(AbstractDescriptionSchema):
    """
    Serializes the fields of the Car model for use in the API.

    This class defines a Django REST Framework serializer that inherits from a custom
    AbstractDescriptionSchema class. The serializer converts instances of the Car
    model to and from JSON format, and validates incoming data based on the model's fields.

    Usage example:
    serializer = CarSchema()
    """

    car_name_id = serializers.UUIDField()
    car_name = CarNameSchema(read_only=True)
    brand = BrandSchema(read_only=True)
    car_model_id = serializers.UUIDField()
    car_model = CarModelSchema(read_only=True)
    color_id = serializers.UUIDField()
    color = ColorSchema(read_only=True)
    engine_id = serializers.UUIDField()
    engine = EngineSchema(read_only=True)

    class Meta:
        """Meta options for CarSchema."""

        model = Car
        fields = "__all__"
        read_only_fields = ("car_name", "brand", "car_model", "color", "engine")


class CarDetailSchema(CarSchema):
    """
    Serializes the fields of the Car model for use in the API.

    This class defines a Django REST Framework serializer that inherits from a custom
    AbstractDescriptionSchema class. The serializer converts instances of the Car
    model to and from JSON format, and validates incoming data based on the model's fields.

    Usage example:
    serializer = CarSchema()
    """

    car_name_id = serializers.UUIDField(required=False)
    car_model_id = serializers.UUIDField(required=False)
    color_id = serializers.UUIDField(required=False)
    engine_id = serializers.UUIDField(required=False)

    class Meta:
        """Meta options for CarDetailSchema."""

        model = Car
        fields = "__all__"
        non_required_fields = "__all__"
