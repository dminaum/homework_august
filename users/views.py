from rest_framework import generics, filters
from .models import Payment
from .serializers import PaymentSerializer
from .filters import PaymentFilter


class PaymentListView(generics.ListAPIView):
    queryset = Payment.objects.select_related('user', 'course', 'lesson').all()
    serializer_class = PaymentSerializer
    filterset_class = PaymentFilter
    filter_backends = [filters.OrderingFilter, ]
    ordering_fields = ['paid_at', 'amount']  # можно сортировать по дате и сумме
    ordering = ['-paid_at']
