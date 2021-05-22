from django.db.models import Q
from django.db.models.sql.query import get_order_dir

from rest_framework import serializers


class NextPrevSerializerMixin(serializers.Serializer):
    next_previous_serializer_class = None

    previous = serializers.SerializerMethodField()
    next = serializers.SerializerMethodField()

    def get_previous(self, obj):
        return self._next_or_previous(obj, is_next=False)

    def get_next(self, obj):
        return self._next_or_previous(obj, is_next=True)

    def _get_next_previous_queryset(self, obj):
        raise NotImplementedError

    def _next_or_previous(self, obj, is_next):
        order_filter = Q()
        filters = dict()

        # Constructs something like: `A < a or A == a and B < b or A == a and B == b and C < c ... `
        for field in self.Meta.model._meta.ordering:
            field, direction = get_order_dir(field)
            value = getattr(obj, field)
            suffix = 'gt' if is_next == (direction == 'ASC') else 'lt'
            order_filter |= Q(**{**filters, f"{field}__{suffix}": value})
            filters[field] = value

        qs = self._get_next_previous_queryset(obj)
        qs = qs.exclude(pk=obj.pk).filter(order_filter)

        next_or_prev_obj = qs.first() if is_next else qs.last()

        return (self.next_previous_serializer_class(next_or_prev_obj).data
                if next_or_prev_obj else None)
