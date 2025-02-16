from django.urls import path
from songs import views

urlpatterns = [
    path('search/<str:query_term>/<str:find_in>', views.search_tracks, name='search'),
    path('popular/<int:k>', views.most_popular_tracks, name='popular'),
    ]