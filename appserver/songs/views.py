from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.contrib.postgres.search import SearchVector
from django.db.models import Func, F

from songs.models import Tracks
from songs.serializers import TrackSerializer

@api_view(['GET'])
def search_tracks(request, query_term=None, find_in=None):
    if request.method == 'GET':
        search = SearchVector('title_en', 'categories', 'composers', 'singers', 'writers', 'actors')
        #TODO: check the status being passed back
        if query_term is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        qs = None

        if find_in == "title_en":
            qs = Tracks.objects.filter(title_en__search=query_term)
        elif find_in == "album":
            qs = Tracks.objects.filter(album__search=query_term)
        elif find_in in ("categories", 'composers', 'singers', 'writers', 'actors'):
            qs = Tracks.objects.annotate(arr_sing=Func(F(find_in), function='unnest')).annotate(search=search).filter(search=query_term)
        #TODO: handle search in en lyrics
        elif find_in == "lyrics_en":
            pass
        # TODO: handle search in hi lyrics
        elif find_in == "lyrics_hi":
            pass
        else:
            # TODO: clean up the search vector compbinable
            # TODO: add more search terms
            # qs = Tracks.objects.annotate(search).filter(search=query_term)
            qs = generate_test_queryset()


        serializer = TrackSerializer(qs, many=True)
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)


    return Response(status=status.HTTP_400_BAD_REQUEST)

#TODO: this is a skeleton impl. find the right logic
@api_view(['GET'])
def most_popular_tracks(request, k=10):
    top_k_ids = [50798, 51624, 55082, 56561, 57529]
    if request.method == 'GET':
        #TODO: Replace this when ready
        # qs = Tracks.objects.filter(pk__in=top_k_ids)
        qs = generate_test_queryset()
        serializer = TrackSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

def generate_test_queryset():
    test_ids = [-1, -2, -3]
    qs = Tracks.objects.filter(id__in=test_ids)
    return qs