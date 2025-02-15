from django.urls import path, include

urlpatterns = [
    path('api/songs/', include('songs.urls')),
    ]