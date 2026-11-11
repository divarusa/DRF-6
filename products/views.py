from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import BasePermission

from .models import Product
from .serializers import ProductSerializer


class IsModerator(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "is_moderator", False)
        )


# Create your views here.


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsModerator]
