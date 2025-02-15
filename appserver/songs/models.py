from django.db import models

from django.contrib.postgres.fields import ArrayField

class Tracks(models.Model):
    title_en = models.CharField(max_length=1000,blank=True, null=True)
    album = models.CharField(max_length=1000,blank=True, null=True)
    release_year = models.IntegerField(blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True)
    categories = ArrayField(models.CharField(max_length=100, blank=True), null=True, size=10)
    composers = ArrayField(models.CharField(max_length=100, blank=True), null=True, size=10)
    singers = ArrayField(models.CharField(max_length=100, blank=True), null=True, size=10)
    writers = ArrayField(models.CharField(max_length=100, blank=True), null=True, size=10)
    actors = ArrayField(models.CharField(max_length=100, blank=True), null=True, size=10)
    notes = models.TextField(blank=True, null=True)
    lyrics_en = models.TextField(blank=True, null=True)
    lyrics_hi = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title_en


class Meta:
    db_table = 'tracks'
    ordering = [
                'title_en',
                'album',
                'category',
                'singers',
                'writers',
                'composers',
                ]

