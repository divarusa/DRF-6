from django.urls import path
from .views import GoogleAuthView, RegisterView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("google/", GoogleAuthView.as_view(), name="google-auth"),
]
