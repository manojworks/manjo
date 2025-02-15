from rest_framework import serializers
from songs.models import Tracks
from utils.array_handler import StringArrayField


class TrackSerializer(serializers.ModelSerializer):

    composers = StringArrayField()
    singers = StringArrayField()
    writers = StringArrayField()

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'title_en': instance.title_en,
            'singers': instance.singers,
            'composers': instance.composers,
            'writers': instance.writers,
            'album': instance.album
        }

    class Meta:
        model = Tracks

        fields = ['id', 'title_en', 'singers', 'composers', 'writers', 'album']
