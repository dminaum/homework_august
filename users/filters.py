import django_filters
from .models import Payment


class PaymentFilter(django_filters.FilterSet):
    course = django_filters.NumberFilter(field_name='course__id', lookup_expr='exact')
    lesson = django_filters.NumberFilter(field_name='lesson__id', lookup_expr='exact')
    method = django_filters.ChoiceFilter(field_name='method', choices=Payment.Method.choices)

    class Meta:
        model = Payment
        fields = ['course', 'lesson', 'method']
