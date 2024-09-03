from django.shortcuts import render

# Create your views here.
from rest_framework import (viewsets, mixins, status)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Csirt
from csirt import serializers
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from .filters import MultiFieldFilterBackend
from django_filters.rest_framework import DjangoFilterBackend
# Create filter for one or all the field of Csirt


# Create your views here.

@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'filter',
                OpenApiTypes.STR,
                description='Filter by any field in the Csirt model'
            ),
        ]
    )
)
class CsirtViewSet(viewsets.ModelViewSet):
    """View fro manager csirt APIs"""

    serializer_class = serializers.CsirtDetailSerializer
    queryset = Csirt.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = (MultiFieldFilterBackend,)


    def get_queryset(self):
        """Retrieve csirts for authenticated user"""
        queryset = self.queryset
        return queryset.filter(user=self.request.user).order_by('-id').distinct()

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action =='list':
            return serializers.CsirtDetailSerializer
        elif self.action =='upload_image':
            return serializers.CsirtImageSerializer
        
        return self.serializer_class
    
    def perform_create(self, serializer):
        """Create a new csirt"""
        serializer.save(user=self.request.user)



    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to recipe"""
        recipe = self.get_object()
        serializer=self.get_serializer(recipe, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


   

