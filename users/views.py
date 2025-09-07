from django.contrib.auth import get_user_model
from rest_framework import generics, viewsets, permissions, filters, status
from rest_framework.exceptions import PermissionDenied
from .models import Payment
from .serializers import (
    PaymentSerializer, MyTokenObtainPairSerializer,
    RegisterSerializer, UserSerializer,
    PaymentCheckoutSerializer
)
from .filters import PaymentFilter
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .stripe_checkout import kickoff_checkout


User = get_user_model()


class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("id")
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ["destroy", "create"]:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    def perform_update(self, serializer):
        instance = self.get_object()
        user = self.request.user
        if (not user.is_staff) and instance.id != user.id:
            raise PermissionDenied("Можно редактировать только свой профиль.")
        serializer.save()


class PaymentListView(generics.ListAPIView):
    queryset = Payment.objects.select_related('user', 'course', 'lesson').all()
    serializer_class = PaymentSerializer
    filterset_class = PaymentFilter
    filter_backends = [filters.OrderingFilter, ]
    ordering_fields = ['paid_at', 'amount']
    ordering = ['-paid_at']


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class PaymentCheckoutView(generics.CreateAPIView):
    serializer_class = PaymentCheckoutSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment = Payment.objects.create(
            user=request.user,
            course=serializer.validated_data['course'],
            amount=serializer.validated_data['amount'],
            method=Payment.Method.STRIPE,
            status=Payment.Status.PENDING,
        )

        session_id, url = kickoff_checkout(payment, request)
        payment.stripe_session_id = session_id
        payment.checkout_url = url
        payment.save(update_fields=['stripe_session_id', 'checkout_url'])

        output = PaymentSerializer(payment).data
        headers = self.get_success_headers(serializer.data)
        return Response(output, status=status.HTTP_201_CREATED, headers=headers)
