from rest_framework import status

from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.contrib.postgres.search import SearchVector
from django.db.models import Func, F

from songs.models import Tracks
from songs.serializers import TrackSerializer
from utils.custom_pagination import CustomPagination

@api_view(['GET'])
def search_tracks(request, query_term=None, find_in=None):
    if request.method == 'GET':
        # print(query_term)
        # print(find_in)
        search = SearchVector('title_en', 'album', 'categories', 'composers', 'singers', 'writers', 'actors', 'lyrics_en', 'lyrics_hi')
        #TODO: send back relevant status
        if query_term is None or find_in is None:
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
            qs = Tracks.objects.filter(lyrics_en__search=query_term)
        # TODO: handle search in hi lyrics
        elif find_in == "lyrics_hi":
            pass
        elif find_in == "all":
            qs = Tracks.objects.annotate(search=search).filter(search=query_term)
            # if none of the filter is applicable, return most popular tracks
        else:
            return most_popular_tracks(request)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(qs, request)
        result_serialized = TrackSerializer(result_page, many=True)

        return paginator.get_paginated_response(result_serialized.data)


    #return Response(status=status.HTTP_400_BAD_REQUEST)

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


