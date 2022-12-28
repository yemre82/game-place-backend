from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from parent.models import jeton, min_withdrawal_amount
from parent.models import BalanceHistory, CustomUser, Family, Game, OTPChangePhone, OTPPhone, Bills, jetonHistory,PNRTransactions, OTPPhoneForgot

# Register your models here.

class UserAdmin(UserAdmin):
    list_display = ('id','phone', 'firstname', 'lastname',
                    'username', 'birthday', 'created_at','is_personel','balance')
    search_fields = ('phone', 'firstname')
    readonly_fields = ('id', 'created_at', 'updated_at')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(CustomUser, UserAdmin)


class jetonAdmin(admin.ModelAdmin):
    list_display = ('id','user','total', 'balance', 'created_at', 'update_at')
    search_fields = ('total', 'balance')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(jeton, jetonAdmin)



class min_withdrawal_amountAdmin(admin.ModelAdmin):
    list_display = ('id','percentage', 'min_amount', 'created_at', 'update_at')
    search_fields = ('percentage', 'min_amount')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(min_withdrawal_amount, min_withdrawal_amountAdmin)



class OTPPhoneAdmin(admin.ModelAdmin):
    list_display = ('id', 'phone', 'otp','description','is_verified','created_at','update_at')
    search_fields = ('phone', 'otp')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(OTPPhone, OTPPhoneAdmin)


class OTPPhoneForgotAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'phone', 'otp','description','is_verified','created_at','update_at')
    search_fields = ('phone', 'otp')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(OTPPhoneForgot, OTPPhoneForgotAdmin)


class OTPChangePhoneAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'phone', 'otp','description','is_verified','created_at','update_at')
    search_fields = ('phone', 'otp')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(OTPChangePhone, OTPChangePhoneAdmin)


class FamilyAdmin(admin.ModelAdmin):
    list_display = ('id','parent', 'firstname', 'lastname','birthday','is_male','is_parent','phone')
    search_fields = ('firstname', 'lastname')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Family, FamilyAdmin)



class BalanceHistoryAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'balance', 'created_at','update_at')
    search_fields = ('user', 'balance')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(BalanceHistory, BalanceHistoryAdmin)


class GameAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'gamer', 'price','started_at','ended_at')
    search_fields = ('user', 'gamer')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Game, GameAdmin)


class BillsAdmin(admin.ModelAdmin):
    list_display = ('id','firstname', 'lastname', 'invoince','price','created_at','update_at')
    search_fields = ('user', 'gamer')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Bills, BillsAdmin)


class jetonHistoryAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'balance', 'created_at','update_at')
    search_fields = ('user', 'balance')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(jetonHistory, jetonHistoryAdmin)

class PNRTransactionsAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'balance', 'transaction_type', 'transaction_guid', 'created_at','update_at')
    search_fields = ('transaction_guid', 'balance')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(PNRTransactions, PNRTransactionsAdmin)
