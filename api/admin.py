from django.contrib import admin
from .models import *


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id']


@admin.register(SDictionary)
class SDictionaryAdmin(admin.ModelAdmin):
    list_display = ['id']


@admin.register(KDictionary)
class KDictionaryAdmin(admin.ModelAdmin):
    list_display = ['id']


@admin.register(Analyzer)
class AnalyzerAdmin(admin.ModelAdmin):
    list_display = ['id']


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['id']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'date']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'date']


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'date']  # pk는 primary key에 대한 별칭