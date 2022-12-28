from urllib import request
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.


class MyUserManager(BaseUserManager):
    def create_user(self, phone, password=None):
        if not phone:
            raise ValueError("Users must have an email address")

        user = self.model(
            phone=phone
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None):
        user = self.create_user(
            phone=phone
        )
        user.set_password(password)
        user.is_admin = True
        user.is_staff = True
        user.save(using=self._db)
        return user
# Create your models here.


class CustomUser(AbstractBaseUser):
    phone = models.CharField(blank=True, null=True, max_length=20,unique=True)
    firstname = models.CharField(blank=False, max_length=30)
    lastname = models.CharField(blank=False, max_length=30)
    username = models.CharField(blank=True, max_length=100, unique=True)
    birthday = models.DateField(blank=True,null=True)
    created_at = models.DateTimeField(
        verbose_name="created at", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="update at", auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_personel = models.BooleanField(default=False)
    balance = models.FloatField(default=0)
    member_id=models.CharField(blank=False,max_length=10)
    email=models.EmailField(blank=True,null=True)
    objects = MyUserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    def __str__(self):
        return str(self.phone)
        
    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True


class OTPPhone(models.Model):
    phone = models.CharField(blank=False, max_length=100)
    otp = models.CharField(blank=False, max_length=10)
    description = models.CharField(blank=False, max_length=100)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.phone)


class OTPChangePhone(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    phone = models.CharField(blank=False, max_length=100)
    otp = models.CharField(blank=False, max_length=10)
    description = models.CharField(blank=False, max_length=100)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user)
        
        
class OTPPhoneForgot(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    phone = models.CharField(blank=False, max_length=100)
    otp = models.CharField(blank=False, max_length=10)
    description = models.CharField(blank=False, max_length=100)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.phone)


def get_profile_image_filepath(self, filename):
    return f'family/images/{self.pk}/{"profile_image.png"}'


def get_default_profile_image():
    return "codingwithmitch/no-pp.png"


class Family(models.Model):
    parent = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    firstname = models.CharField(blank=False, max_length=100)
    lastname = models.CharField(blank=False, max_length=100)
    birthday = models.DateField(blank=False)
    is_male = models.BooleanField(blank=False)
    is_parent = models.BooleanField(default=False)
    profile_image = models.ImageField(
        max_length=1000, upload_to=get_profile_image_filepath, null=True, blank=True, default=None)
    phone = models.CharField(blank=True, null=True, max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.parent)


class BalanceHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    balance = models.FloatField(blank=False)
    adding_balance=models.BooleanField(blank=False)
    is_gift=models.BooleanField(blank=False,default=False)
    city=models.CharField(blank=True,max_length=100,null=True)
    branch=models.CharField(blank=True,max_length=100,null=True)
    game_name=models.CharField(blank=True,null=True,max_length=100)
    is_pnr=models.BooleanField(blank=False,default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user)


class Game(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    gamer=models.ForeignKey(Family,on_delete=models.CASCADE)
    price=models.FloatField(blank=False)
    started_at=models.DateTimeField(blank=False)
    ended_at=models.DateTimeField(blank=True,null=True)
    is_finished=models.BooleanField(default=False)
    city=models.CharField(blank=True,max_length=100,null=True)
    branch=models.CharField(blank=True,max_length=100,null=True)
    game_name=models.CharField(blank=True,null=True,max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user)
        
        
class OTPGetChild(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    phone = models.CharField(blank=False, max_length=100)
    otp = models.CharField(blank=False, max_length=10)
    description = models.CharField(blank=False, max_length=100)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.phone)
        
        
class Bills(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    firstname = models.CharField(blank=False, max_length=100,default="")
    lastname = models.CharField(blank=False, max_length=100,default="")
    phone = models.CharField(blank=False, max_length=100,default="")
    email = models.CharField(blank=False, max_length=100,default="")
    title = models.CharField(blank=False, max_length=100,default="")
    national_id = models.CharField(blank=False, max_length=100,default="")
    guid = models.CharField(blank=False, max_length=100,default="")
    invoice_date= models.DateTimeField(blank=True,null=True)
    product_list=models.CharField(blank=False, max_length=100,default="")
    invoince = models.CharField(blank=False, max_length=100,default="")
    totp=models.CharField(blank=False, max_length=100,default="")
    price=models.FloatField(blank=False,default=0) 
    is_approve=models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.invoince)


class jeton(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    total=models.FloatField(blank=False,default=0)
    balance = models.FloatField(blank=False,default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.total)
        

class jetonHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    balance = models.FloatField(blank=False)
    adding_balance=models.BooleanField(blank=False)
    city=models.CharField(blank=True,max_length=100,null=True)
    branch=models.CharField(blank=True,max_length=100,null=True)
    game_name=models.CharField(blank=True,null=True,max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user)


class min_withdrawal_amount(models.Model):
    percentage=models.FloatField(blank=False)
    min_amount=models.FloatField(blank=False)
    tl_to_jeton=models.IntegerField(blank=False,default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.percentage) 
        
class PNRTransactions(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    balance = models.FloatField(blank=False)
    transaction_guid=models.CharField(blank=False, max_length=100,default="")
    otp=models.CharField(blank=False, max_length=100,default="")
    transaction_type=models.CharField(blank=False, max_length=100,default="")
    is_used=models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.user) 
