from django.contrib import admin
from .models import *

admin.site.register(User)

admin.site.register(SDictionary)
admin.site.register(KDictionary)

admin.site.register(Analyzer)

admin.site.register(Vote)

admin.site.register(Request)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'date']  # pk는 primary key에 대한 별칭


admin.site.register(Comment)
