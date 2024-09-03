from django.db.models import Q
from django.contrib.postgres.fields import JSONField
from rest_framework.filters import BaseFilterBackend

class MultiFieldFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        filter_value = request.query_params.get('filter', None)
        if filter_value:
            queries = Q()
            for field in queryset.model._meta.get_fields():
                field_name = field.name
                if field.concrete and not field.many_to_many and not field.one_to_many:
                    field_type = field.get_internal_type()
                    if field_type in ['CharField', 'TextField', 'SlugField', 'EmailField']:
                        queries |= Q(**{f"{field_name}__icontains": filter_value})
                    elif field_type in ['IntegerField', 'FloatField', 'DecimalField']:
                        try:
                            filter_value_num = float(filter_value)
                            queries |= Q(**{f"{field_name}": filter_value_num})
                        except ValueError:
                            pass
                    elif field_type == 'JSONField':
                        queries |= Q(**{f"{field_name}__contains": filter_value})
            queryset = queryset.filter(queries)
        return queryset
