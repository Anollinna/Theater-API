from django.contrib import admin
from theater.models import Genre, Actor, Play

@admin.register(Play)
class PlayAdmin(admin.ModelAdmin):
    filter_horizontal = ("genres", "actors")
admin.site.register(Genre)
admin.site.register(Actor)
