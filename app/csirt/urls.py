"""Url mappings for recipe app"""


from django.urls import (
 path, 
    include,
)

from rest_framework.routers import DefaultRouter

from csirt import views

router = DefaultRouter()
router.register('csirt', views.CsirtViewSet)

app_name = 'csirt'

urlpatterns = [
    path('', include(router.urls)),

]