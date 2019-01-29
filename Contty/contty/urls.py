from django.urls import path
from contty.views import MainView


urlpatterns = [
    path("", MainView.as_view(), name="index"),
]
