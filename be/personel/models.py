from django.db import models

from superuser.models import Branchs

# Create your models here.


class Personel(models.Model):
    firstname = models.CharField(blank=False, max_length=100)
    lastname = models.CharField(blank=False, max_length=100)
    username = models.CharField(blank=False, max_length=50, unique=True)
    birthday=models.DateField(blank=False)
    is_male=models.BooleanField(blank=False)
    phone=models.CharField(blank=False,max_length=100)
    started_at=models.DateField(blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.username)



class PersonelsOfBranchs(models.Model):
    branch=models.ForeignKey(Branchs,on_delete=models.CASCADE)
    personel=models.ForeignKey(Personel,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.branch)
        
        
def get_profile_image_filepath(self, filename):
    return f'profile/images/{self.pk}/{"profile_image.png"}'


class ChildsOfGames(models.Model):
    parent_name=models.CharField(blank=False,max_length=100)
    parent_surname=models.CharField(blank=False,max_length=100)
    phone=models.CharField(blank=False,max_length=100)
    child_name=models.CharField(blank=False,max_length=100)
    child_surname=models.CharField(blank=False,max_length=100)
    birthday = models.DateField(blank=True,null=True)
    is_male=models.BooleanField(default=False)
    price=models.FloatField(blank=False)
    started_at=models.DateTimeField(blank=False)
    ended_at=models.DateTimeField(blank=True,null=True)
    is_sent_email=models.BooleanField(blank=True,null=True)
    city=models.CharField(blank=True,max_length=100,null=True)
    branch=models.CharField(blank=True,max_length=100,null=True)
    game_name=models.CharField(blank=True,null=True,max_length=100)
    is_finished=models.BooleanField(default=False)
    profile_image = models.ImageField(blank=True,null=True,
        max_length=100, upload_to=get_profile_image_filepath, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.phone)


class Games(models.Model):
    branch=models.ForeignKey(Branchs,on_delete=models.CASCADE)
    game_name=models.CharField(blank=False,max_length=100)
    machine_type=models.CharField(blank=False,default="SOFT PLAY",max_length=100)

    def __str__(self):
        return str(self.branch)