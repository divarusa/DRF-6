import random
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import CustomUser
from .services import save_confirmation_code
from .tasks import process_user_data, send_welcome_email


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    phone_number = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = CustomUser
        fields = ["email", "phone_number", "password"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = CustomUser.objects.create_user(password=password, **validated_data)

        code = str(random.randint(1000, 9999))
        save_confirmation_code(user.email, code)
        process_user_data.delay(user.id)
        send_welcome_email.delay(user.email)

        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    @staticmethod
    def _serialize_birthdate(user):
        birthdate = getattr(user, "birthdate", None)
        if birthdate is None:
            return None
        return (
            birthdate.isoformat() if hasattr(birthdate, "isoformat") else str(birthdate)
        )

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["user_id"] = user.id
        token["email"] = getattr(user, "email", None)
        token["phone_number"] = getattr(user, "phone_number", None)
        token["birthdate"] = cls._serialize_birthdate(user)
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user_id"] = self.user.id
        data["email"] = getattr(self.user, "email", None)
        data["phone_number"] = getattr(self.user, "phone_number", None)
        data["birthdate"] = self._serialize_birthdate(self.user)
        return data
