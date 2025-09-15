"""
Serializers for abstract models in the API.

This module defines Django REST Framework serializers that inherit from both
`serializers.ModelSerializer` and a custom `AbstractModelSchema` class. The serializers
convert instances of abstract models to and from JSON format, and validate incoming
data based on the model's fields.

Attributes:
    - `Meta`: A nested class that specifies metadata for the serializer. The `model`
      attribute specifies the model class that the serializer should be based on, and
      `fields` lists the names of all fields that should be included in the serialized
      representation.

Usage example:
serializer = StatementSchema()

"""

from rest_framework import renderers, serializers
from rest_framework.fields import DictField

from drf_base_apps.models import AbstractDescription


class CustomDictField(DictField):
    """Custom dictionary field for serialization."""

    pass


class CustomSerializerMethodField(serializers.SerializerMethodField):
    """Custom serializer method field with GET/POST support."""

    def __init__(self, get=None, post=None, **kwargs):
        """Initialize the custom serializer method field."""
        self.get = get
        self.post = post
        super().__init__(**kwargs)

    def to_representation(self, value):
        """Convert the field to its representation."""
        return {"get": self.get if self.get else None, "post": self.post if self.post else None}

    class Meta:
        """Meta options for CustomSerializerMethodField."""

        fields = "__all__"


class SerializerMethodFieldChild(serializers.SerializerMethodField):
    """Serializer method field with child support."""

    def __init__(self, child, **kwargs):
        """Initialize the serializer method field with child."""
        self.child = child
        super().__init__(**kwargs)


class AbstractModelSchema(serializers.Serializer):
    """Serializer for AbstractModel fields."""

    renderer_classes = [renderers.JSONRenderer]
    id = serializers.UUIDField(read_only=True)
    create_user = serializers.CharField(read_only=True)
    update_user = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(allow_null=True, read_only=True)

    class Meta:
        """Meta options for AbstractModelSchema."""

        fields = "__all__"

    def __init__(self, *args, **kwargs):
        """Initialize the abstract model schema."""
        fields = kwargs.pop("exclude", None)
        include_fields = kwargs.pop("fields", None)
        super().__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            set(self.fields)
            for field_name in allowed:
                try:
                    self.fields.pop(field_name)
                except KeyError:
                    continue

        if include_fields is not None:
            allowed = set(include_fields) & set(self.fields.keys())
            self.fields = {field_name: self.fields[field_name] for field_name in allowed}


class AbstractDescriptionSchema(serializers.ModelSerializer, AbstractModelSchema):
    """Use serializers.ModelSerializer and AbstractModelSchema to serialize the project fields of the AbstractDescription model."""

    non_required_fields = []

    class Meta:
        """Meta options for AbstractDescriptionSchema."""

        model = AbstractDescription
        fields = "__all__"
        non_required_fields = []

    def get_extra_kwargs(self):
        """Get extra keyword arguments for the serializer."""
        extra_kwargs = super().get_extra_kwargs()
        for field_name in self.non_required_fields:
            if field_name not in extra_kwargs:
                extra_kwargs[field_name] = {"required": False}
            else:
                extra_kwargs[field_name]["required"] = False
        return extra_kwargs
