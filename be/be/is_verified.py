from parent.models import OTPPhone
from django.core.exceptions import ObjectDoesNotExist


def is_verified(data):
    phone_obj=OTPPhone.objects.filter(phone=data,is_verified=True)
    if len(phone_obj)<1:
        return False
    return True