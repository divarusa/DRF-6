from django.shortcuts import render
from rest_framework import generics
from .models import CustomUser
from .serializers import RegisterSerializer
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from users.services import google_validate_and_get_user_data

# Create your views here.


class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer


class GoogleAuthView(APIView):

    def post(self, request):
        code = request.data.get("code")
        if not code:
            return Response({"error": "Код не передан"}, status=400)

        user = google_validate_and_get_user_data(
            code=code,
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            redirect_uri=settings.GOOGLE_REDIRECT_URI,
        )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        )
