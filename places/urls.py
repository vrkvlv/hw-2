from django.urls import path

from . import views

urlpatterns = [
    path("", views.places_list, name="places_list"),
    path("place/<int:place_id>/", views.place_detail, name="place_detail"),
]
