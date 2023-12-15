from django.contrib import admin
from .models import Game, Movie, TVShow, UserContent

# Register your models here.
admin.site.register(Game)
admin.site.register(Movie)
admin.site.register(TVShow)
admin.site.register(UserContent)