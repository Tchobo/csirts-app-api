from django.shortcuts import render

# Create your views here.
from rest_framework import (viewsets, mixins, status)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly

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
        tags=['csirt'],
        summary='List CSIRTs',
        description=(
            'Return every CSIRT in the directory. Public endpoint — no token '
            'required. Use the `filter` query parameter to search across '
            'name, country, website, and description in a single call.'
        ),
        parameters=[
            OpenApiParameter(
                'filter',
                OpenApiTypes.STR,
                description=(
                    'Case-insensitive substring match against name, country, '
                    'website, and description. Example: `?filter=kenya`.'
                ),
            ),
        ],
    ),
    retrieve=extend_schema(
        tags=['csirt'],
        summary='Retrieve a CSIRT',
        description=(
            'Return the full detail of a single CSIRT, including its long '
            'description and image URL. Public endpoint — no token required.'
        ),
    ),
    create=extend_schema(
        tags=['csirt'],
        summary='Create a CSIRT',
        description=(
            'Register a new CSIRT in the directory. Requires token '
            'authentication — reserved for platform administrators. '
            'The `location` field must be a JSON object with numeric '
            '`latitude` and `longitude` keys.'
        ),
    ),
    update=extend_schema(
        tags=['csirt'],
        summary='Update a CSIRT (full)',
        description='Replace all fields of a CSIRT. Requires token authentication.',
    ),
    partial_update=extend_schema(
        tags=['csirt'],
        summary='Update a CSIRT (partial)',
        description='Update a subset of fields. Requires token authentication.',
    ),
    destroy=extend_schema(
        tags=['csirt'],
        summary='Delete a CSIRT',
        description='Remove a CSIRT from the directory. Requires token authentication.',
    ),
    upload_image=extend_schema(
        tags=['csirt'],
        summary='Upload a CSIRT logo/image',
        description=(
            'Attach an image to an existing CSIRT (multipart/form-data). '
            'Requires token authentication.'
        ),
    ),
)
class CsirtViewSet(viewsets.ModelViewSet):
    """Manage CSIRTs — list, retrieve, create, update, delete, upload image."""

    serializer_class = serializers.CsirtDetailSerializer
    queryset = Csirt.objects.all()
    authentication_classes = [TokenAuthentication]
    # Public read (GET list/retrieve) so the map + basic CSIRT metadata is
    # available to guests. Any write action (create/update/delete/upload_image)
    # still requires a valid token — enforced by IsAuthenticatedOrReadOnly.
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = (MultiFieldFilterBackend,)


    def get_queryset(self):
        """Retrieve csirts for authenticated user"""
        queryset = self.queryset
        return queryset

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action =='retrieve':
            return serializers.CsirtDetailSerializer
        elif self.action =='upload_image':
            return serializers.CsirtImageSerializer
        
        return self.serializer_class
    
    def perform_create(self, serializer):
        """Create a new csirt"""
        serializer.save(user=self.request.user)


    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image"""
        recipe = self.get_object()
        serializer=self.get_serializer(recipe, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


   

