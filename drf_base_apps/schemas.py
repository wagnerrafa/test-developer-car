"""
Serializes the fields of the `AbstractModelSchema` model for use in the API.

This module defines a Django REST Framework serializer that inherits from both
`serializers.ModelSerializer` and a custom `AbstractModelSchema` class. The serializer
converts instances of the `AbstractModelSchema` model to and from JSON format, and
validates incoming data based on the model's fields.

Attributes:
    - `Meta`: A nested class that specifies metadata for the serializer. The `model`
      attribute specifies the model class that the serializer should be based on, and
      `fields` lists the names of all fields that should be included in the serialized
      representation.

"""

import copy

from rest_framework import serializers

from drf_base_apps.core.abstract.schemas import AbstractModelSchema
from drf_base_apps.models import AbstractDescription


class AbstractDescriptionSchema(serializers.ModelSerializer, AbstractModelSchema):
    """
    Utilize serializers.ModelSerializer and AbstractModelSchema to serialize the project fields of the AbstractDescription model.

    This serializer automatically adds display fields for choice fields. For example, if a model has a 'status' field
    with choices, it will automatically add a 'status_display' field that uses the get_status_display() method.

    Attributes:
        model (Model): The model class to be serialized.
        fields (list): A list of field names to be included in the serialization process.
        non_required_fields (list): A list of fields that are not required.

    Methods:
        get_fields(self): Get serializer fields with automatic addition of display fields for choice fields.
        get_extra_kwargs(self): Return extra keyword arguments for the serializer fields, setting read-only or
        non-required options based on 'read_only_fields' and 'non_required_fields' defined in the Meta class.

    """

    class Meta:
        """Meta options for AbstractDescriptionSchema."""

        model = AbstractDescription
        fields = "__all__"
        non_required_fields = []

    def get_fields(self):
        """
        Get serializer fields with automatic addition of display fields for choice fields.

        This method automatically detects fields that are choices and adds corresponding
        display fields (e.g., status_display for status field) that use the get_*_display()
        method from Django models.

        Returns:
            dict: Dictionary of serializer fields including the automatically added display fields.

        """
        fields = super().get_fields()

        # Get the model class
        model = self.Meta.model

        # Check if model has choices fields
        for field in model._meta.get_fields():
            # Check if field has choices (CharField, IntegerField, etc. with choices)
            if hasattr(field, "choices") and field.choices:
                field_name = field.name
                display_field_name = f"{field_name}_display"

                # Only add if the display field doesn't already exist
                if display_field_name not in fields:
                    # Create a CharField that calls get_*_display()
                    display_field = serializers.CharField(source=f"get_{field_name}_display", read_only=True)
                    fields[display_field_name] = display_field

        return fields

    def get_extra_kwargs(self):
        """
        Return extra keyword arguments for serializer fields.

        This method checks 'read_only_fields' and 'non_required_fields' defined in the Meta class and sets
        the fields as read-only or non-required accordingly.

        Returns:
            extra_kwargs (dict): Extra keyword arguments for serializer fields.

        """
        read_only_fields = getattr(self.Meta, "read_only_fields", None)
        exclude_read_only_fields = getattr(self.Meta, "exclude_read_only_fields", [])

        if read_only_fields and read_only_fields == "__all__":
            fields = self.Meta.model._meta.get_fields()
            extra_kwargs = copy.deepcopy(getattr(self.Meta, "extra_kwargs", {}))

            for field in fields:
                field_name = field.name
                kwargs = extra_kwargs.get(field_name, {})
                kwargs["read_only"] = True
                extra_kwargs[field_name] = kwargs

        elif exclude_read_only_fields:
            if not isinstance(exclude_read_only_fields, (list, tuple)):
                raise TypeError(
                    f"The `exclude_read_only_fields` option must be a list or tuple. "
                    f"Got {type(exclude_read_only_fields).__name__}."
                )

            fields = self.Meta.model._meta.get_fields()
            extra_kwargs = copy.deepcopy(getattr(self.Meta, "extra_kwargs", {}))

            for field in fields:
                field_name = field.name

                if field_name in exclude_read_only_fields:
                    continue

                kwargs = extra_kwargs.get(field_name, {})
                kwargs["read_only"] = True
                extra_kwargs[field_name] = kwargs

        else:
            extra_kwargs = super().get_extra_kwargs()

        non_required_fields = copy.deepcopy(getattr(self.Meta, "non_required_fields", []))
        if non_required_fields == "__all__":
            fields = self.Meta.model._meta.get_fields()
            fields = [field.name for field in fields]
        else:
            fields = non_required_fields
        for field_name in fields:
            if field_name not in extra_kwargs:
                extra_kwargs[field_name] = {"required": False}
            else:
                extra_kwargs[field_name]["required"] = False
        return extra_kwargs


class AbstractChoicesSerializer(serializers.Serializer):
    """
    Create fields for objects that have an ID and legend associated with them.

    The id field must be a CharField, while the legend field needs to be a CharField of maximum length of 1.
    """

    id = serializers.CharField()
    legend = serializers.CharField(max_length=1)

    def to_representation(self, choice):
        """Convert the choice tuple to a dictionary representation."""
        return {"id": choice[0], "legend": choice[1]}


class AbstractUpdateModelSchema(serializers.ModelSerializer, AbstractModelSchema):
    """Serializer for AbstractModel fields."""

    def get_fields(self):
        """Get the serializer fields with PUT method handling."""
        fields = super().get_fields()
        request = self.context.get("request", None)
        if request and getattr(request, "method", None) == "PUT":
            for key in fields:
                fields[key].required = False
        return fields

    class Meta:
        """Meta options for AbstractUpdateModelSchema."""

        model = AbstractDescription
        fields = "__all__"


class AbstractStatusSchema(AbstractDescriptionSchema):
    """Schema for models with status fields."""

    status_display = serializers.CharField(source="get_status_display", read_only=True)


class HealthSchema(serializers.Serializer):
    """Schema for health check responses."""

    status = serializers.CharField()


class ManyListField(serializers.ListField):
    """Schema for list id of items."""

    def __init__(self, **kwargs):
        """Initialize the ManyListField with UUID child field."""
        super().__init__(child=serializers.UUIDField(), **kwargs)
