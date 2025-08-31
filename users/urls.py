from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import PaymentListView, RegisterAPIView, UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('payments/', PaymentListView.as_view(), name='payment-list'),
    path('register/', RegisterAPIView.as_view(), name='register'),           # открыт
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), # открыт
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),# открыт
    path('', include(router.urls)),
]
