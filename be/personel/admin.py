from django.contrib import admin

from personel.models import Games, ChildsOfGames, Personel

# Register your models here.
class GamesAdmin(admin.ModelAdmin):
    list_display = ('id', 'branch', 'game_name','machine_type')
    search_fields = ('branch', 'game_name')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Games, GamesAdmin)




class ChildsOfGamesAdmin(admin.ModelAdmin):
    list_display = ('id', 'parent_name', 'parent_surname','phone', 'child_name','child_surname')
    search_fields = ('parent_name', 'parent_surname', 'phone', 'child_name','child_surname')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(ChildsOfGames, ChildsOfGamesAdmin)



class PersonelAdmin(admin.ModelAdmin):
    list_display = ('id', 'firstname', 'lastname','username', 'birthday','is_male','phone')
    search_fields = ('firstname', 'lastname')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Personel, PersonelAdmin)