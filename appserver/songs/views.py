from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.contrib.postgres.search import SearchVector

from songs.models import Tracks
from songs.serializers import TrackSerializer

@api_view(['GET'])
def search_tracks(request, query_term=None, find_in=None):
    if request.method == 'GET':
        #TODO: check the status being passed back
        if query_term is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        qs = None
        if find_in is None:
            #TODO: clean up the search vector compbinable
            #TODO: add more search terms
            qs = Tracks.objects.annotate(search = SearchVector('title_en', 'categories', 'composers', 'singers', 'writers', 'actors'),).filter(search=query_term)
        elif find_in == "title_en":
            qs = Tracks.objects.filter(title_en__search=query_term)
        #TODO: support other criteria
        elif find_in == "categories":
            pass
        else:
            #TODO: what do we do here
            pass


        serializer = TrackSerializer(qs, many=True)
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)


    return Response(status=status.HTTP_400_BAD_REQUEST)

#TODO: this is a skeleton impl. find the right logic
@api_view(['GET'])
def most_popular_tracks(request, k=10):
    top_k_ids = [50798, 51624, 55082, 56561, 57529]
    if request.method == 'GET':
        qs = Tracks.objects.filter(pk__in=top_k_ids)
        serializer = TrackSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)