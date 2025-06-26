from rest_framework import serializers

from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers

class _SingleValueMixin:
    @staticmethod
    def _flatten(data):
        if isinstance(data, (list, tuple)):
            return data[0] if data else ""
        return data


@extend_schema_field(OpenApiTypes.INT)
class SVIntegerField(_SingleValueMixin, serializers.IntegerField):
    def to_internal_value(self, data):
        data = self._flatten(data)
        if data in ("", None):
            if self.allow_null:
                return None
        return super().to_internal_value(data)


@extend_schema_field(OpenApiTypes.STR)
class SVCharField(_SingleValueMixin, serializers.CharField):
    def to_internal_value(self, data):
        return super().to_internal_value(self._flatten(data))


@extend_schema_field(OpenApiTypes.BINARY)
class SVImageField(_SingleValueMixin, serializers.ImageField):
    def to_internal_value(self, data):
        data = self._flatten(data)
        if data in ("", None):
            if self.allow_null:
                return None
        return super().to_internal_value(data)


class CompletionIn(serializers.Serializer):
    session_id = SVIntegerField(required=False, allow_null=True)
    content    = SVCharField(required=False, allow_blank=True)
    image_data = SVImageField(required=False, allow_null=True, allow_empty_file=True)

class SessionQuery(serializers.Serializer):
    page  = SVIntegerField(required=False, min_value=1, default=1)
    title = SVCharField(required=False, allow_blank=True)

class RenameIn(serializers.Serializer):
    title = SVCharField(max_length=120)

class MessagesQuery(serializers.Serializer):
    session_id = SVIntegerField()
    page       = SVIntegerField(required=False, min_value=1, default=1)
