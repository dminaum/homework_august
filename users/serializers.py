from rest_framework import serializers
from .models import Payment
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'paid_at',
            'course',
            'amount', 'method',
            'status', 'stripe_session_id', 'checkout_url'
        ]
        read_only_fields = ['id', 'user', 'paid_at', 'status', 'stripe_session_id', 'checkout_url']


class PaymentCheckoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment

        fields = ['course', 'amount']

    def validate(self, attrs):
        course = attrs.get('course')
        if not course:
            raise serializers.ValidationError('Нужно указать курс для оплаты.')
        amount = attrs.get('amount')
        if amount is None or amount <= 0:
            raise serializers.ValidationError('Сумма должна быть больше нуля.')
        return attrs


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['username'] = user.username
        token['email'] = user.email

        return token


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ("id", "email", "password", "first_name", "last_name", "avatar", "phone", "city")

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "avatar", "phone", "city", "is_active", "is_staff")
        read_only_fields = ("id", "is_active", "is_staff")
