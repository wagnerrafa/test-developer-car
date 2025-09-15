"""
Abstract base classes for Django REST Framework views and schemas.

This module provides abstract base classes and utilities for creating
DRF views with custom schemas, pagination, filtering, and caching.
It includes classes for OpenAPI schema generation, custom ordering filters,
and base API views with common functionality.
"""

import contextlib
import datetime
import inspect
import json
import logging
import os
import re
import shutil
import tempfile
import uuid
from abc import ABC
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import ClassVar
from uuid import UUID

from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.core import exceptions as django_exceptions
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.db import models, transaction
from django.http import Http404, JsonResponse
from django.template.response import ContentNotRenderedError
from django.urls import resolve
from django.utils.encoding import smart_str
from drf_yasg import openapi
from rest_framework import generics, serializers, status
from rest_framework.filters import BaseFilterBackend, OrderingFilter
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.schemas.utils import is_list_view
from rest_framework.utils import formatting

from drf_base_apps.core.abstract.exceptions import ValidationAdapterError
from drf_base_apps.core.abstract.schemas import (
    AbstractDescriptionSchema,
    CustomDictField,
    CustomSerializerMethodField,
    SerializerMethodFieldChild,
)
from drf_base_apps.schemas import ManyListField
from drf_base_apps.security.views import Security
from drf_base_apps.utils import _, secret_number
from drf_base_config.settings import ENABLE_CACHE, SANDBOX_COMMIT


def get_app_label_from_model(model) -> str:
    """
    Extract app label from Django model.

    Args:
        model: Django model instance.

    Returns:
        str: App label or verbose name.

    """
    app = model._meta.app_config.name.split(".")[0]
    try:
        return str(apps.get_app_config(app).verbose_name)
    except LookupError:
        pass
    return app


class CustomSchema(AutoSchema):
    """
    Custom schema for generating OpenAPI 3.0.0 spec for DRF views.

    Extends AutoSchema to add custom functionality for generating tags
    and descriptions in the OpenAPI schema.
    """

    date_example = "2021-08-31"
    datetime_example = "2021-08-31T19:24:56.830Z"
    email_example = "jane.doe@example.com"
    uri_example = "http://example.com"
    uuid_example = "123e4567-e89b-12d3-a456-426614174000"
    float_example = 1.23
    integer_example = 42
    binary_example = "SGVsbG8gV29ybGQ="  # "Hello World" em base64
    has_path_parameters = False

    def get_kwargs_from_path(self, url_path):
        """
        Extract named parameters from URL path.

        Args:
            url_path: URL path string.

        Returns:
            dict: Dictionary of parameter names and values.

        """
        path = Path(url_path)
        kwargs = {}

        # Itera sobre cada parte do caminho do URL
        for part in path.parts:
            # Verifica se a parte começa com "{", indicando um argumento nomeado
            if part.startswith("{") and part.endswith("}"):
                # Remove as chaves "{" e "}" para obter o nome do argumento
                arg_name = part[1:-1]
                # Adiciona o argumento nomeado ao dicionário kwargs
                kwargs[arg_name] = None  # Defina o valor inicial como None ou atribua um valor padrão desejado

        return kwargs

    def get_operation_id_base(self, path, method, action):
        """
        Get operation ID base for view.

        Returns the operation id base for a view as defined in the view
        class attribute `operation_id_base`.

        Args:
            path: API path.
            method: HTTP method.
            action: Action name.

        Returns:
            str: Operation ID base.

        """
        kwargs = "".join(self.get_kwargs_from_path(path).keys())
        name = super().get_operation_id_base(path, method, action)
        return f"{name}{kwargs}{uuid.uuid4()}"

    def get_example(self, example):
        """
        Get example value for field type.

        Args:
            example: Example type name.

        Returns:
            Any: Example value for the type.

        """
        examples = {
            "date": "2021-08-31",
            "datetime": "2021-08-31T19:24:56.830Z",
            "email": "jane.doe@example.com",
            "uri": "http://example.com",
            "uuid": "123e4567-e89b-12d3-a456-426614174000",
            "float": 0,
            "integer": 0,
            "binary": "binary",
            "string": "string",
        }

        return examples.get(example)

    def map_serializer(self, serializer):
        """
        Map serializer by adding dynamic methods to properties.

        Args:
            serializer: The serializer to map.

        Returns:
            dict: Fields with mapped dynamic methods.

        """
        fields = super().map_serializer(serializer)

        big_numbers = self.view.get_dynamic_methods()

        for big in big_numbers:

            example = {}
            dynamic_methods = big.bignumbermethod_set.all()
            for method in dynamic_methods:
                new_field = getattr(serializers, method.get_field_type_display())()
                big_field_type = self.map_field(new_field)["type"]
                example[method.name] = big_field_type

                if big_field_type in ["object", "array"]:
                    method_fields = method.get_fields()
                    new_example = {}
                    for method_field in method_fields:
                        field_schema = self.map_field(getattr(serializers, method_field.get_field_type_display())())
                        field_type = field_schema["type"]
                        format_ = field_schema.get("format")
                        if format_:
                            example_value = self.get_example(format_)
                            new_example[method_field.field] = example_value if example_value is not None else field_type
                        else:
                            example_value = self.get_example(field_type)
                            new_example[method_field.field] = example_value if example_value is not None else field_type

                    if big_field_type == "array":
                        example[method.name] = [new_example]
                    else:
                        example[method.name] = new_example

            fields["properties"][big.path] = {"example": example}
        return fields

    def get_pagination_parameters(self, path, method):
        """
        Get pagination parameters for schema.

        Args:
            path: API path.
            method: HTTP method.

        Returns:
            list: Pagination parameters.

        """
        view = self.view
        if not hasattr(view, "pagination") or not view.pagination or method != "GET":
            return []

        paginator = self.get_paginator()
        if not paginator:
            return []

        return paginator.get_schema_operation_parameters(view)

    def get_operation(self, path, method):
        """
        Get operation for HTTP method on path.

        Override get_operation method of base class to include parameter
        descriptions and handle path parameters.

        Args:
            path: API path.
            method: HTTP method.

        Returns:
            dict: Operation specification.

        """
        op = super().get_operation(path, method)
        has_path_parameters = len(self.get_kwargs_from_path(path).keys()) > 0 and not self.view.query_slug

        if method != "GET" or has_path_parameters:
            op["parameters"] = [param for param in op["parameters"] if param["in"] == "path"]

        else:
            if not self.view.pagination:
                op["parameters"] = [
                    param for param in op["parameters"] if param["name"] not in ("limit", "offset", "ordering")
                ]
            else:
                get_search_model_fields = []
                if self.view.model and self.view.search_model_fields:
                    get_search_model_fields = self.view.get_search_model_fields(self.view.model)
                op["parameters"] += self.view.default_query_params + self.view.query_params

                for search_model_field in get_search_model_fields:
                    has_parameter = False
                    for parameter in op["parameters"]:
                        field_name = parameter.get("field", parameter["name"])
                        search_field_name = search_model_field.get("field", search_model_field["name"])
                        has_parameter = field_name == search_field_name
                        if has_parameter:
                            break

                    if not has_parameter:
                        op["parameters"].append(search_model_field)

        # Crie um conjunto para rastrear os nomes de campo já encontrados
        seen_names = set()

        # Percorra a lista de parâmetros na ordem inversa
        for count in range(len(op["parameters"]) - 1, -1, -1):
            x = op["parameters"][count]
            name = x["name"]

            # Verifique se o nome do campo já foi visto
            if name in seen_names:
                # Se já foi visto, remova o campo duplicado
                del op["parameters"][count]
            else:
                # Se não foi visto, adicione-o ao conjunto de nomes vistos
                seen_names.add(name)

            if x["name"] == "ordering":
                if has_path_parameters:
                    del op["parameters"][count]
                    continue
                else:
                    op["parameters"][count]["description"] = (
                        "Campo para ordenação dos resultados. Envie uma lista com as opções "
                        "escolhidas. Use o caracter - em frente a opção para descendente e apenas a "
                        "opção para ascendente"
                    )
                    op["parameters"][count]["schema"] = {
                        "type": openapi.TYPE_ARRAY,
                        "items": {"type": openapi.TYPE_STRING, "enum": self.view.ordering_fields},
                    }

            op["parameters"][count]["description"] = str(op["parameters"][count]["description"])
            op["parameters"][count]["name"] = str(op["parameters"][count]["name"])
        return op

    def get_tags(self, path, method):
        """
        Override get_tags method of base class.

        Returns the tags for an endpoint based on the view class attributes
        `tags` or `model`.
        """
        view = self.view
        if hasattr(view, "tags") and isinstance(view.tags, (list, tuple)):
            return list(map(str, view.tags))

        if hasattr(view, "tags") and isinstance(view.tags, dict):
            return view.tags.get(method.upper())

        if hasattr(view, "model") and view.model:
            app_label = str(view.model._meta.app_config.verbose_name.split(".")[0].replace("_", " ").title())
            app_ = get_app_label_from_model(view.model).title()
            if app_.lower() == "apps":
                return [app_label]
            if app_.lower() in app_label.lower():
                return [app_]
            return [f"{app_} - {app_label}"]

        return super().get_tags(path, method)

    def map_field(self, field):
        """
        Override map_field method of base class.

        Maps a Django Rest Framework field to a dictionary representation
        as required by OpenAPI 3.0.0 spec.
        """
        if isinstance(field, CustomDictField):
            return {
                "type": "any",
            }

        elif isinstance(field, CustomSerializerMethodField):
            null_value = {"type": "string", "nullable": True, "default": None}
            return {
                "type": "object",
                "properties": {
                    "get": self.map_field(field.get) if field.get else null_value,
                    "post": self.map_field(field.post) if field.post else null_value,
                },
            }
        elif isinstance(field, SerializerMethodFieldChild):
            data = self.map_serializer(field.child)
            data["type"] = "object"
            return data
        map_field = super().map_field(field)
        return map_field

    def get_description(self, path, method):
        """
        Override get_description method of base class.

        Returns the description for an endpoint as defined in the view method's
        docstring or in the view class attribute `docs`.
        """
        view = self.view
        init = self._get_init_description()
        method_name = getattr(view, "action", method.lower())
        method_docstring = getattr(view, method_name, None).__doc__

        view_docs = getattr(view, "docs", None)

        if view_docs and not isinstance(view_docs, dict):
            raise AssertionError

        if view_docs and view.docs.get(method.lower()):
            method_docstring = view_docs.get(method.lower())
            docstring = self._get_description_section(view, method.lower(), smart_str(method_docstring))
        elif method_docstring:
            docstring = self._get_description_section(view, method.lower(), smart_str(method_docstring))
        else:
            docstring = self._get_description_section(
                view, getattr(view, "action", method.lower()), view.get_view_description()
            )

        return formatting.dedent(smart_str(init + "\n\n" + str(docstring)))

    def _get_init_description(self) -> str:
        """
        Obtém a descrição inicial para um endpoint.

        Returns:
            str: A descrição inicial do endpoint.

        """
        view_app = self.view
        if hasattr(view_app, "docs") and isinstance(view_app.docs, dict) and view_app.docs.get("init"):
            return view_app.docs.get("init")
        return view_app.__class__.__doc__ or ""

    def get_responses(self, path, method):
        """
        Obtém as respostas para um endpoint.

        Args:
            path: O caminho do endpoint.
            method: O método HTTP.

        Returns:
            dict: As respostas do endpoint.

        """
        # Start main default get_responses
        if method == "DELETE":
            return {"204": {"description": ""}}

        self.response_media_types = self.map_renderers(path, method)

        serializer = self.get_response_serializer(path, method)

        item_schema = {} if not isinstance(serializer, serializers.Serializer) else self.get_reference(serializer)

        many_view = getattr(self, "view", {})
        many_view = getattr(many_view, "many", True)

        if (is_list_view(path, method, self.view) and many_view and method == "GET") or (
            hasattr(self.view, "pagination") and self.view.pagination and method == "GET"
        ):  # Modified: Include check if is self.view.pagination and method is GET
            response_schema = {
                "type": "array",
                "items": item_schema,
            }
            paginator = self.get_paginator()
            if paginator:
                response_schema = paginator.get_paginated_response_schema(response_schema)
        else:
            response_schema = item_schema
        status_code = "201" if method == "POST" else "200"
        # end main default get_responses

        responses = {
            status_code: {
                "content": {ct: {"schema": response_schema} for ct in self.response_media_types},
                # description is a mandatory property,
                # https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.2.md#responseObject
                # TODO: put something meaningful into it
                "description": "",
            }
        }

        if hasattr(self.view, "responses"):
            custom_responses = self.view.responses

            if custom_responses:
                for code, value in custom_responses.items():
                    if not responses.get(code):
                        responses[code] = {}
                    responses[code]["content"] = {
                        "application/json": {"example": json.loads(json.dumps(value, default=str))}
                    }
                for code in responses.copy():
                    if code not in custom_responses:
                        responses.pop(code, None)
        return responses


class CustomLimitOffsetPagination(LimitOffsetPagination):
    """
    Paginação personalizada com limite e offset.

    Estende LimitOffsetPagination com configurações
    personalizadas para o sistema.
    """

    max_limit = 30

    def paginate_queryset_ids(self, queryset, request, view=None):
        """
        Pagina um queryset retornando apenas os IDs.

        Args:
            queryset: O queryset a ser paginado.
            request: A requisição HTTP.
            view: A view que está sendo paginada.

        Returns:
            list: Lista de IDs paginados.

        """
        self.limit = self.get_limit(request)
        if self.limit is None:
            return None

        self.count = self.get_count(queryset)
        self.offset = self.get_offset(request)
        self.request = request
        if self.count > self.limit and self.template is not None:
            self.display_page_controls = True

        if self.count == 0 or self.offset > self.count:
            return []

        return list(queryset.values_list("id", flat=True)[self.offset: self.offset + self.limit])


class SimpleFilterBackend(BaseFilterBackend, ABC):
    """
    Backend de filtro simples.

    Fornece funcionalidade básica de filtro para views DRF.
    """

    @staticmethod
    def get_schema_operation_parameters(view):
        """
        Retorna os parâmetros de consulta para a operação do schema.

        Args:
            view: A view obtendo os parâmetros de consulta.

        Returns:
            Query parameters.

        """
        return view.query_params


class CustomOrderingFilter(OrderingFilter):
    """
    A custom ordering filter class that extends Django REST Framework's OrderingFilter.

    Attributes:
        order_by (bool): Determines if ordering is enabled.
        ordering_fields (list): Specifies the fields that can be used for ordering.
        default_ordering_fields (list): Specifies the default fields used for ordering.
        model (Model): The Django model to be used for retrieving fields.
        map_ordering_fields (dict): Maps ordering fields to specific fields in the model. Use the key for the value
        to be displayed, and the value for the value in the field model

    Methods:
        get_ordering(request, queryset, view):
            Returns the ordering for the given request and queryset based on query parameters or default ordering.

        get_non_relation_fields():
            Returns a list of non-relational fields in the model.

        get_ordering_fields():
            Returns a list of all possible ordering fields, including default, non-relational, and mapped fields.

        get_default_ordering_fields():
            Returns the default ordering fields.

        get_map_ordering_fields(fields):
            Maps and returns the provided fields to their corresponding fields in the model.

    """

    order_by = True
    ordering_fields = []  # Specify which fields can be used for ordering
    default_ordering_fields = ["created_at", "updated_at"]  # Specify default fields for ordering
    model = None

    map_ordering_fields = {}  # Specify field mappings for ordering. Use the key for the value to be displayed,

    # and the value for the value in the field model

    def get_ordering(self, request, queryset, view):
        """
        Return the ordering for the given request and queryset.

        Args:
            request (Request): The current request instance.
            queryset (QuerySet): The queryset to be ordered.
            view (View): The view instance.

        Returns:
            list: A list of fields to order the queryset by.

        """
        params = request.query_params.getlist(self.ordering_param)
        if params:
            fields = params
            fields = self.get_map_ordering_fields(fields)

            self.ordering_fields.extend(list(self.map_ordering_fields.values()))

            ordering = self.remove_invalid_fields(queryset, fields, view, request)
            if ordering:
                return ordering

        # No ordering was included, or all the ordering fields were invalid
        return self.get_default_ordering(view)

    def get_non_relation_fields(self):
        """
        Return non-relational fields from the model.

        Returns:
            list: A list of non-relational field names.

        """
        non_relation_fields = []

        if not self.model:
            return non_relation_fields

        for field in self.model._meta.fields:
            if not isinstance(field, (models.ForeignKey, models.OneToOneField, models.ManyToManyField)):
                non_relation_fields.append(field.name)
        return list(set(non_relation_fields))

    def get_ordering_fields(self):
        """
        Return all possible ordering fields, including defaults, non-relational, and mapped fields.

        Returns:
            list: A list of all possible ordering field names.

        """
        if not self.order_by:
            return []
        ordering_fields = self.get_default_ordering_fields()
        ordering_fields.extend(self.get_non_relation_fields())
        ordering = ordering_fields + self.ordering_fields.copy() + list(self.map_ordering_fields.keys())
        ordering_hyphen = []

        for s in ordering:
            ordering_hyphen.append(f"-{s}")
        ordering.extend(ordering_hyphen)

        return ordering

    def get_default_ordering_fields(self):
        """
        Return the default ordering fields.

        Returns:
            list: A list of default ordering field names.

        """
        return ["created_at", "updated_at"]

    def get_map_ordering_fields(self, fields):
        """
        Map the provided fields to their corresponding fields in the model.

        Args:
            fields (list): A list of field names to be mapped.

        Returns:
            list: A list of mapped field names.

        """
        for count, field in enumerate(fields):
            start_hyphen = ""
            if field.startswith("-"):
                field = field.replace("-", "", 1)
                start_hyphen = "-"

            map_field = self.map_ordering_fields.get(field, None)
            if map_field:
                fields[count] = f"{start_hyphen}{map_field}"
        return fields


class AbstractViewApi(generics.GenericAPIView, CustomOrderingFilter):
    """
    Base API view class with common HTTP methods and utilities.

    Fornece métodos HTTP comuns, paginação, ordenação, cache, controle de permissões,
    e utilidades para views DRF customizadas. Deve ser estendida por views de API
    para herdar funcionalidades padrão e facilitar a implementação de endpoints REST.
    """

    def __init__(self, *args, **kwargs):
        """Initialize the AbstractViewApi with ordering fields and pagination."""
        super().__init__(*args, **kwargs)
        self.ordering_fields = self.get_ordering_fields()
        if self.pagination:
            self.pagination_class = CustomLimitOffsetPagination

    filter_backends = (SimpleFilterBackend, CustomOrderingFilter)
    query_params = []
    pagination = False
    exclude = []
    operation_id_base = None
    many = True
    responses = None
    query_slug: ClassVar[bool] = False
    model_slug: ClassVar[bool] = False
    try_it_out = True  # Run button in swagger
    custom_path = None
    default_query_params = [
        {
            "name": "created_at_min",
            "field": "created_at__gte",
            "in": "query",
            "required": False,
            "description": str(_("Created at start")),
            "schema": {"type": "date"},
        },
        {
            "name": "created_at_max",
            "field": "created_at__lte",
            "in": "query",
            "required": False,
            "description": str(_("Created at end")),
            "schema": {"type": "date"},
        },
        {
            "name": "updated_at_min",
            "field": "updated_at__gte",
            "in": "query",
            "required": False,
            "description": str(_("Updated at start")),
            "schema": {"type": "date"},
        },
        {
            "name": "updated_at_max",
            "field": "updated_at__lte",
            "in": "query",
            "required": False,
            "description": str(_("Updated at end")),
            "schema": {"type": "date"},
        },
    ]
    model = None
    search_model_fields = True
    layout_serializers = None
    schema = CustomSchema()
    cache_timeout = 60
    cache_version = "v1"
    allow_cache: bool = True
    allowed_versions = ["v1"]
    custom_objects = False  # Use for custom manager model
    model_query = None

    select_related = "__all__"

    def get_select_related(self):
        """Return the select_related configuration for the queryset."""
        if isinstance(self.select_related, str):
            if self.select_related != "__all__":
                raise ValueError("select_related deve ser uma string __all__, False, ou uma lista de fields")
            return []

        elif isinstance(self.select_related, list):
            return self.select_related

        return False

    # def get_permissions(self):
    #     """
    #     Instantiates, append CheckAPIVersion and returns the list of permissions that this view requires.
    #     """
    #     permissions = super().get_permissions()
    #
    #     # Adicione suas permissões personalizadas aqui
    #     permissions.append(CheckAPIVersion())
    #
    #     return permissions
    def get_dynamic_methods(self) -> list:
        """
        Return a list of dynamic methods to be added as properties to the serializer.

        Returns:
            List of dynamic methods.

        """
        return []

    def get_serializer_class(self):
        """
        Return the appropriate serializer class based on the HTTP request method.

        Returns:
            Serializer class.

        """
        if self.layout_serializers:
            if not self.request:
                return self.layout_serializers["default"]
            return self.layout_serializers.get(self.request.method.lower(), self.layout_serializers["default"])
        return super().get_serializer_class()

    @staticmethod
    def get_schema_operation_parameters(view):
        """
        Return the query parameters for the schema operation.

        Args:
            view: The view obtaining the query parameters.

        Returns:
            Query parameters.

        """
        return view.query_params

    @staticmethod
    def __parse_date(date_string):
        """Parse string to date."""
        return datetime.datetime.strptime(date_string, "%Y-%m-%d").date()

    @staticmethod
    def __parse_datetime(date_string):
        """Parse string to datetime."""
        return datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M")

    @staticmethod
    def __parse_uuid(uuid_str):
        """
        Valida e converte uma string para UUID.

        Args:
            uuid_str (str): String contendo o UUID a ser validado

        Returns:
            UUID: Objeto UUID válido

        Raises:
            ValidationErrorAdapter: Se o UUID for inválido

        """
        try:
            UUID(uuid_str)
            return uuid_str
        except (ValueError, AttributeError, TypeError):
            raise ValidationAdapterError(
                {"uuid": _("UUID inválido. O formato deve ser: 123e4567-e89b-12d3-a456-426614174000")}
            ) from None

    @staticmethod
    def __parse_bool(text):
        """Parse string to bool."""
        return str(text).lower() in "true"

    @staticmethod
    def __parse_year(year_str):
        """
        Parse a string representation of a year and return the corresponding integer value.

        Args:
            year_str (str): The string representation of the year.

        Returns:
            int: The parsed year value if it is valid, otherwise returns None.

        Example:
            parse_year("2022")
            2022
            parse_year("abcd")
            None
            parse_year("22")
            None

        """
        if len(year_str) == 4:
            try:
                year = int(year_str)
                if year >= 0:
                    return year
            except ValueError:
                pass

    def __get_type_by_instance(self, instance):
        """Get instance, type, parser and legend by field schema type."""
        types = {
            "string": {"type": str, "parser": str, "legend": "string"},
            "date": {"type": datetime.date, "parser": self.__parse_date, "legend": "2001-12-30"},
            "datetime": {"type": datetime.date, "parser": self.__parse_datetime, "legend": "2001-12-30 23:01"},
            "float": {"type": float, "parser": float, "legend": "01.00"},
            "array": {"type": list, "parser": list, "legend": "string"},
            "int": {"type": int, "parser": int, "legend": "1"},
            "integer": {"type": int, "parser": int, "legend": "1"},
            "uuid": {"type": "uuid", "parser": self.__parse_uuid, "legend": "123e4567-e89b-12d3-a456-426614174000"},
            "bool": {"type": bool, "parser": self.__parse_bool, "legend": "True/False"},
            "boolean": {"type": bool, "parser": self.__parse_bool, "legend": "True/False"},
            "year": {"type": int, "parser": self.__parse_year, "legend": "2023"},
        }

        return types.get(instance, {"type": str, "parser": str, "legend": "string"})

    def get_request_query_data(self):
        """Return the request query parameters."""
        return self.request.query_params

    def get_query_parameters(self):
        """Return the query parameters from the request."""
        query = {}

        get_search_model_fields = []

        if self.model and self.search_model_fields:
            get_search_model_fields = self.get_search_model_fields(self.model)

        valid_parameters = self.query_params + self.default_query_params

        for search_model_field in get_search_model_fields:
            has_parameter = False
            for parameter in valid_parameters:
                field_name = parameter.get("field", parameter["name"])
                search_field_name = search_model_field.get("field", search_model_field["name"])
                has_parameter = field_name == search_field_name
                if has_parameter:
                    break

            if not has_parameter:
                valid_parameters.append(search_model_field)

        for valid_params in valid_parameters:
            type_instance = valid_params["schema"]["type"]
            field = valid_params["field"]
            name = valid_params["name"]
            in_parameters = valid_params.get("in_parameters")
            if in_parameters is not None and not in_parameters:
                continue

            if type_instance == "array":
                value = self.get_request_query_data().getlist(name)
            else:
                value = self.get_request_query_data().get(name)
            if value:
                instance = self.__get_type_by_instance(type_instance)

                with contextlib.suppress(ValueError, KeyError):
                    value = instance["parser"](value)

                if instance["type"] == "uuid":
                    query[field] = value
                    continue

                if isinstance(value, instance["type"]):
                    query[field] = value
                else:
                    raise ValidationAdapterError(
                        {
                            name: _("Field in invalid format. It must be in the format{}").format(
                                f': {instance["legend"]}'
                            )
                        }
                    )

                if type_instance == "boolean":
                    revert = valid_params["schema"].get("revert")
                    if revert:
                        query[field] = not value
        return query

    def get_query_slug(self):
        """Return the query slug for the current request."""
        if self.query_slug:
            resolver_match = resolve(self.request.path_info)
            return resolver_match.kwargs
        return {}

    def get(self, request, *args, **kwargs):
        """Abstract method for default method GET. Override method in class for custom operation."""
        id_ = kwargs.get("id")

        if self.pagination:
            queryset = self.filter(id_, **kwargs)

            paginated_queryset = self.paginate_queryset(queryset)
            data = self.serializer(paginated_queryset, many=True)
            return self.get_paginated_response(data)

        query = self.get_query(id_=id_)
        return JsonResponse(query, safe=False)

    def filter(self, id_, **kwargs):
        """Filter the queryset based on the given parameters."""
        query = self.get_queryset()
        get_query_slug = self.get_query_slug()
        query_exclude = self.get_exclude_queryset()
        query_parameters = self.get_query_parameters()

        model_objects = self.get_model()
        if id_ or self.many is False:
            if id_:
                query["id"] = id_
            obj = (
                model_objects.exclude(**query_exclude)
                .filter(**query_parameters)
                .filter(**kwargs)
                .filter(**get_query_slug)
                .filter(**query)
                .first()
            )
            if not obj:
                raise Http404
            return obj

        select_related = self.get_select_related()

        if select_related is False:
            queryset = (
                model_objects.exclude(**query_exclude)
                .filter(**query_parameters)
                .filter(**kwargs)
                .filter(**get_query_slug)
                .filter(**query)
                .distinct()
            )
        else:
            queryset = (
                model_objects.exclude(**query_exclude)
                .filter(**query_parameters)
                .filter(**kwargs)
                .filter(**get_query_slug)
                .filter(**query)
                .select_related(*select_related)
                .distinct()
            )

        ordering = self.get_ordering(self.request, queryset, self)
        if ordering:
            return queryset.order_by(*ordering)

        return queryset

    def get_query(self, id_=None, **kwargs):
        """Validate parameters received in query params, returning query values."""
        obj = self.filter(id_, **kwargs)
        many = not (id_ or self.many is False)
        return self.serializer(obj, many)

    def serializer(self, obj, many):
        """Serialize the object using the appropriate serializer."""
        exclude = self.get_exclude_values()
        serializer = self.get_serializer_class()
        return serializer(obj, many=many, exclude=exclude, context={"request": self.request}).data

    def get_cache_key(self, request):
        """Generate a unique cache key for the current request and model."""
        app_label = self.model._meta.verbose_name.lower().replace(" ", "_")
        url = request.build_absolute_uri()
        app_name = get_app_label_from_model(self.model).replace(" ", "_")
        cache_key = make_template_fragment_key(app_label, [url])
        user_key = request.user.id
        return f"{self.cache_version}:{app_name}:{app_label}:{cache_key}:{user_key}"

    def __get_keys(self):
        """Get a list of all existing cache keys."""
        return cache.get(f"{self.cache_version}:keys", [])

    def __set_key(self, key, value, timeout: float = cache_timeout):
        """Set a new cache key with a given value and timeout."""
        keys_list = self.__get_keys()
        if key not in keys_list:
            keys_list.append(key)
            cache.set(f"{self.cache_version}:keys", keys_list)
        cache.set(key, value, timeout)

    def __delete_key(self, key):
        """Delete a cache key and remove it from the list of existing keys."""
        keys_list = self.__get_keys()
        if key in keys_list:
            keys_list.remove(key)
            cache.delete(key)
            cache.set(f"{self.cache_version}:keys", keys_list)

    def get_cache_keys_from_app(self, model):
        """Return a list of cache keys for a given app name (model label)."""
        keys = self.__get_keys()
        app_name = get_app_label_from_model(model)
        url_keys = []
        for key in keys:
            if key.startswith(f"{self.cache_version}:{app_name}"):
                url_keys.append(key)
        return url_keys

    def get_cache_keys_from_user(self):
        """Return a list of cache keys for a given user request."""
        keys = self.__get_keys()
        url_keys = []
        for key in keys:
            key_label = key.split(":")
            if str(self.request.user.id) in key_label[-1]:
                url_keys.append(key)
        return url_keys

    def get_cache_keys_from_labels(self, app_labels: list):
        """Return a list of cache keys for all apps in a given list of app labels."""
        keys = self.__get_keys()
        url_keys = []
        for key in keys:
            key_label = key.split(":")
            if key_label[2] in app_labels:
                url_keys.append(key)
        return url_keys

    def delete_cache_from_app(self, model):
        """Delete all cache keys associated with a given app/model."""
        url_keys = self.get_cache_keys_from_app(model)
        for key in url_keys:
            self.__delete_key(key)

    def delete_cache_from_user(self):
        """Delete all cache keys associated with a given request user."""
        url_keys = self.get_cache_keys_from_user()
        for key in url_keys:
            self.__delete_key(key)

    def delete_cache_from_labels(self):
        """Delete all cache keys associated with a list of app labels."""
        labels = ["project", "creditor", "calculation"]
        url_keys = self.get_cache_keys_from_labels(labels)
        for key in url_keys:
            self.__delete_key(key)

    def convert_url(self, current_url):
        """Convert URL placeholders to actual values."""
        # Define o padrão para identificar os placeholders na URL
        pattern = r"<(.*?)>"

        # Função para remover prefixos como 'uuid:', 'str:', 'int:' de dentro dos placeholders
        def remove_prefix(match):
            placeholder = match.group(1)  # Captura o conteúdo dentro dos '<>'
            if ":" in placeholder:
                return "{" + placeholder.split(":", 1)[1] + "}"
            return "{" + placeholder + "}"

        # Realiza a substituição usando a função remove_prefix
        converted_url = re.sub(pattern, remove_prefix, current_url)

        if converted_url.startswith("/") is False:
            converted_url = f"/{converted_url}"
        return converted_url.strip()

    def is_swagger_cache(self):
        """Check if the current request is from Swagger cache."""
        try:
            return str(self.request.headers._store["referer"][1]).endswith("docs/swagger/cache/")
        except (KeyError, IndexError):
            return False

    def save_example_swagger(self):
        """Save example data for Swagger documentation."""
        save_swagger = self.is_swagger_cache()

        if save_swagger:
            # Atualize ou crie o exemplo no requestBody do endpoint recebido
            current_url = self.convert_url(self.request.resolver_match.route)
            body_kwargs = self.request.resolver_match.kwargs

            swagger_path = f"{settings.STATIC_ROOT}/swagger.json"

            # Cria um diretório temporário
            with tempfile.TemporaryDirectory() as temp_dir:
                swagger_copy_path = f"{temp_dir}/swagger_copy_{secret_number(5, 6)}.json"
                shutil.copy(swagger_path, swagger_copy_path)

                if os.path.exists(swagger_path) is False:
                    raise ValueError("Acesse primeiramente a URL docs/swagger/save/")

                with open(swagger_copy_path) as f:
                    swagger_data = json.loads(f.read())

                method = self.request.method.lower()
                if current_url in swagger_data["paths"]:
                    msgs = f"URL Atualizada no swagger: {current_url}. "
                    if method in ["post", "put"]:
                        swagger_data["paths"][current_url][method]["requestBody"]["content"]["application/json"][
                            "example"
                        ] = json.loads(self.request.body)

                        msgs += "Atualizado Body. "

                    if body_kwargs:
                        for count, parameter in enumerate(swagger_data["paths"][current_url][method]["parameters"]):
                            if parameter["in"] == "path":
                                swagger_data["paths"][current_url][method]["parameters"][count]["value"] = (
                                    body_kwargs.get(parameter["name"])
                                )
                            msgs += "Atualizado Path. "

                    if method in "get":
                        for count, parameter in enumerate(swagger_data["paths"][current_url][method]["parameters"]):
                            if parameter["in"] == "query":
                                get_value = self.request.GET.get(parameter["name"])
                                if get_value:
                                    swagger_data["paths"][current_url][method]["parameters"][count]["value"] = get_value

                            msgs += "Atualizado Query. "

                    messages.add_message(self.request, messages.INFO, msgs)

                    # Salve as alterações de volta no arquivo swagger.json
                    with open(swagger_path, "w") as f:
                        f.write(json.dumps(swagger_data, indent=4, default=str))

    def dispatch(self, request, *args, **kwargs):
        """
        Override the default dispatch method to handle caching.

        If a GET request has a cached response, it returns the cached response. When a model instance is created, updated, or deleted, it deletes all cached responses for related models and app instances.

        SANDBOX_COMMIT: A boolean flag indicating whether database commits should be performed or rolled back.
        If SANDBOX_COMMIT is False and the request method is 'POST', 'PUT', or 'DELETE', the database transaction
        will be rolled back after processing the request, ensuring changes are not permanently saved.

        """
        self.save_example_swagger()

        save_swagger = self.is_swagger_cache()

        # Check if commit is False, rollback transaction
        if (save_swagger or not SANDBOX_COMMIT) and request.method.upper() in ["POST", "PUT", "DELETE"]:
            with transaction.atomic():
                response = super().dispatch(request, *args, **kwargs)
                transaction.set_rollback(True)
            return response

        if not self.model or not self.allow_cache or not ENABLE_CACHE:
            return super().dispatch(request, *args, **kwargs)
        fernet = Security()

        cache_key = self.get_cache_key(request)
        if request.method == "GET":
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                try:
                    return JsonResponse(json.loads(fernet.decrypt(cached_data).encode()), safe=False)
                except (TypeError, UnicodeError, UnicodeDecodeError, UnicodeEncodeError, ValueError) as e:
                    logging.error(e, exc_info=True)

        response = super().dispatch(request, *args, **kwargs)
        if response.status_code in [200, 201] and request.method == "GET":
            with contextlib.suppress(
                TypeError, UnicodeError, UnicodeDecodeError, UnicodeEncodeError, ValueError, ContentNotRenderedError
            ):
                self.__set_key(cache_key, fernet.encrypt(response.content.decode()))

        if request.method != "GET":
            self.delete_cache_from_app(self.model)
            self.__delete_key(cache_key)
            related_serializers = find_related_serializers(self.get_serializer_class())
            for serializer_cls in related_serializers:
                model_class = serializer_cls.Meta.model
                self.delete_cache_from_app(model_class)
        return response

    def get_request_data(self):
        """Return the request data."""
        return self.request.data

    def model_create_obj(self, new_obj: dict):
        """Create a new model object with the given data."""
        return self.model.objects.create(**new_obj)

    def get_validated_post_data(self):
        """Return the validated POST data serializer."""
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=self.get_request_data(), context={"request": self.request})
        serializer.is_valid(raise_exception=True)
        return serializer

    def get_model_slug(self):
        """Get the model slug for the view."""
        return self.get_query_slug() if self.model_slug else {}

    def create_object(self):
        """Create a new object using the serializer."""
        with transaction.atomic():
            serializer = self.get_validated_post_data()
            new_obj = serializer.validated_data
            mm_fields = []
            for field_name in serializer.fields:
                field = serializer.fields[field_name]

                if isinstance(field, (serializers.ManyRelatedField, ManyListField)):
                    values = new_obj.pop(field_name, False)
                    if isinstance(values, list):
                        mm_fields.append((field_name, values))

            try:

                new_obj.update(**self.get_model_slug())
                obj = self.model_create_obj(new_obj)
            except django_exceptions.ValidationError as e:
                from drf_base_apps.core.abstract.exceptions import ValidationAdapterError

                raise ValidationAdapterError(e.message_dict if hasattr(e, "message_dict") else str(e)) from e

            for field_name, values in mm_fields:
                attr = getattr(obj, field_name)
                attr.clear()
                attr.add(*values)
        return obj

    def post(self, request, *args, **kwargs):
        """Abstract method for default method POST. Override method in class for custom operation."""
        self.validate_data()
        obj = self.create_object()
        return self.response(obj)

    def get_status(self):
        """Return the appropriate HTTP status code for the current request method."""
        options = {
            "POST": status.HTTP_201_CREATED,
            "GET": status.HTTP_200_OK,
            "PUT": status.HTTP_200_OK,
            "DELETE": status.HTTP_200_OK,
        }
        return options.get(self.request.method.upper(), 200)

    def response(self, obj, status_=status.HTTP_201_CREATED):
        """Return a response with the serialized object."""
        if not status_:
            status_ = self.get_status()
        return JsonResponse(
            self.serializer_class(obj, many=False, context={"request": self.request}).data, status=status_, safe=False
        )

    def validate_data(self):
        """Validate the request data."""
        return True

    def put_model(self, obj, data_obj: dict):
        """Update the model object with the given data."""
        obj = obj.dict_update(**data_obj)
        return obj

    def put(self, request, *args, **kwargs):
        """
        Handle PUT requests for the view.

        Expect input data that conform to the serializer used by the view class. It updates the approved_calculation or date object of a specific comparative object using the given calculation_id from the query parameters and serializes the updated object in JSON format before returning it as an HTTP response.

        Parameters: request: The HTTP request object. args: Any additional positional arguments passed to the method.
        kwargs: Any additional keyword arguments passed to the method, with calculation_id identifying the
        comparative object to update. Returns: JsonResponse: An HTTP response containing the updated and serialized
        comparative object data.
        """
        with transaction.atomic():
            id_ = kwargs.get("id")
            self.validate_data()
            exclude = self.get_exclude_values()
            serializer = self.get_serializer_class()

            query = self.get_queryset()
            # model_objects = self.custom_objects or self.model.objects
            model_objects = self.get_model()

            obj = model_objects.filter(id=id_, **query).first()

            if not obj:
                raise Http404

            try:
                serializer = serializer(
                    data=self.get_request_data(), exclude=exclude, instance=obj, context={"request": self.request}
                )
            except ValueError:
                serializer = serializer(data=self.get_request_data(), instance=obj, context={"request": self.request})

            serializer.is_valid(raise_exception=True)
            data_obj = serializer.validated_data

            for field_name in serializer.fields:
                field = serializer.fields[field_name]
                if isinstance(field, serializers.ManyRelatedField):
                    values = data_obj.pop(field_name, False)
                    if isinstance(values, list):
                        attr = getattr(obj, field_name)
                        attr.clear()
                        attr.add(*values)
            obj = self.put_model(obj, data_obj)
        return self.response(obj, 200)

    def get_model_name(self):
        """Get the app_label for the model."""
        return self.model._meta.verbose_name.lower().replace(" ", "_")

    def delete(self, request, *args, **kwargs):
        """Abstract method for default method DELETE. Override method in class for custom operation."""
        obj_id = kwargs.get("id")
        obj = get_object_or_404(self.get_model(), id=obj_id)
        obj.delete()
        return JsonResponse(
            {"data": _(f'{self.get_model_name().replace("_", " ").title()} deleted')}, status=status.HTTP_200_OK
        )

    def get_exclude_values(self) -> list or tuple:
        """Return the exclude values for serialization."""
        return self.exclude

    def get_queryset(self):
        """Get the filter queryset."""
        return {}

    def get_exclude_queryset(self):
        """Get the filter queryset to remove."""
        return {}

    def is_put_method(self):
        """Check if the request method is PUT or PATCH."""
        return self.request.method.upper() in ("PUT", "PATCH")

    def get_model(self):
        """Get the model instance with appropriate filters."""
        # Verifica se is_active está sendo filtrado explicitamente
        query_parameters_is_active = "is_active" in self.get_query_parameters()
        get_query_slug_is_active = "is_active" in self.get_query_slug()

        if any([query_parameters_is_active, get_query_slug_is_active, self.is_put_method()]) and hasattr(
            self.model, "all_objects"
        ):
            # Usa o manager padrão (sem filtro is_active) quando is_active é filtrado explicitamente
            return self.model.all_objects

        # Usa o ActiveManager (com filtro is_active=True) por padrão
        return self.model_query if self.model_query is not None else self.custom_objects or self.model.objects

    def get_field_type(self, field):
        """
        Mapeia o tipo do campo Django para o tipo correspondente no Swagger.

        Args:
            field: O campo do modelo Django.

        Returns:
            str: O tipo do campo no formato Swagger.

        """
        field_types = {
            models.DateField: "date",
            models.DateTimeField: "datetime",
            models.IntegerField: "integer",
            models.FloatField: "float",
            models.BooleanField: "boolean",
            models.EmailField: "string",
            models.URLField: "string",
            models.UUIDField: "uuid",
            models.FileField: "string",
            models.ImageField: "string",
            models.JSONField: "object",
            models.ForeignKey: "uuid",
            models.OneToOneField: "integer",
            models.ManyToManyField: "array",
        }

        for field_class, swagger_type in field_types.items():
            if isinstance(field, field_class):
                if isinstance(field, models.ForeignKey):
                    # Verifica se o campo relacionado é do tipo UUID
                    if isinstance(field.remote_field.model._meta.pk, models.UUIDField):
                        return "uuid"  # UUID é representado como string no Swagger
                    return "integer"  # Chave estrangeira padrão é inteiro
                return swagger_type
        return "string"

    def get_search_model_fields(self, model):
        """
        Return a list of field names for a given Django model, excluding sensitive and file-related fields.

        Args:
            model: The Django model for which to retrieve field names.

        Returns:
            list: A list of objects containing field information for the provided model, following the default_query_params pattern.

        """
        fields = []
        text_sensitive = [
            "password",
            "last_login",
            "is_superuser",
            "token",
            "user_permissions",
            "auth_token",
            "logentry__id",
            "id",
            "created_at",
            "updated_at",
            "create_user",
            "update_user",
        ]

        def valid_field(fi):
            if fi.name in text_sensitive:
                return False
            if fi.is_relation and not fi.many_to_one:
                return False
            return not isinstance(fi, models.FileField)

        for field in model._meta.get_fields():
            if valid_field(field):
                field_name = field.name
                if isinstance(field, (models.ManyToManyField, models.ImageField)):
                    continue
                if isinstance(field, (models.ForeignKey, models.OneToOneField)):
                    field_name = f"{field.name}_id"
                field_type = self.get_field_type(field)

                filter_query_name = f"{field_name}__icontains" if field_type == "string" else field_name
                field_info = {
                    "name": field_name,
                    "field": filter_query_name,
                    "in": "query",
                    "required": False,
                    "description": str(field.verbose_name),
                    "schema": {"type": field_type},
                }
                fields.append(field_info)

        return fields


def get_model_serializer_subclasses():
    """
    Return a list of subclasses of DRF serializers.

    Returns: A list of model serializer subclasses schemas.

    """
    # Get all Schemas
    model_serializer_subclasses = []
    for app in apps.get_app_configs():
        schema_path = os.path.join(app.path, "schemas.py")
        if os.path.exists(schema_path):
            spec = spec_from_file_location(f"{app.name}.schemas", schema_path)
            module = module_from_spec(spec)
            spec.loader.exec_module(module)
            members = inspect.getmembers(module)
            for _member_name, member in members:
                if inspect.isclass(member) and (
                    issubclass(member, serializers.ModelSerializer) or issubclass(member, AbstractDescriptionSchema)
                ):
                    model_serializer_subclasses.append(member)

    return model_serializer_subclasses


def find_related_serializers(schema, checked_serializers=None):
    """
    Find all model serializer subclasses and their related serializers by schema.

    model_serializer_subclasses - list of model serializer subclasses found in schemas.py files in each app's
    directory. find_related_serializers - recursively finds related serializers for a given schema by searching the
    fields of each model serializer subclass. @param schema: The schema class to search for related serializers by.
    @return: A list of model serializer classes that are related to the given schema class.
    """
    related_serializer_schemas = []
    if checked_serializers is None:
        checked_serializers = set()
    checked_serializers.add(schema)

    def append_srl(srl):
        if srl not in related_serializer_schemas:
            related_serializer_schemas.append(srl)

    for serializer_cls in get_model_serializer_subclasses():
        try:
            for _field_name, field in serializer_cls().get_fields().items():
                if str(field.__class__.__name__).endswith("Schema"):
                    if field.__class__.__name__ == schema.__name__:
                        append_srl(serializer_cls)
                elif isinstance(field, serializers.ListSerializer):
                    if field.child.__class__.__name__ == schema.__name__:
                        append_srl(serializer_cls)
                elif isinstance(field, serializers.Serializer) and field.__class__ == schema.__name__:
                    append_srl(serializer_cls)
        except (ValueError, AssertionError):
            pass

    for serializer_cls in related_serializer_schemas:
        if serializer_cls not in checked_serializers:
            related_serializer_schemas.extend(find_related_serializers(serializer_cls, checked_serializers))
    return related_serializer_schemas
