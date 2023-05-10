from django.urls import path, include
from friendship.views import index


urlpatterns = [
    path('home/', index, name='home_url'),
]
