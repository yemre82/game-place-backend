from django.contrib import admin

from superuser.models import News, Branchs

# Register your models here.
class NewsAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'short_description','description','campaign_price','image','created_at','update_at')
    search_fields = ('title', 'short_description')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(News, NewsAdmin)




class BranchsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'country','city','created_at','update_at')
    search_fields = ('name', 'city')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Branchs, BranchsAdmin)
