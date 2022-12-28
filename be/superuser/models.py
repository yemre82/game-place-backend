from django.db import models


# Create your models here.


def get_news_image_filepath(self, filename):
    return f'profile/images/{self.pk}/{"profile_image.png"}'


def get_default_news_image():
    return "codingwithmitch/no-pp.png"


class News(models.Model):
    title = models.CharField(blank=False, max_length=100)
    short_description = models.CharField(blank=False, max_length=100)
    description = models.CharField(blank=False, max_length=400)
    image = models.ImageField(
        max_length=100, upload_to=get_news_image_filepath, null=True, blank=True, default=get_default_news_image)
    is_campaign=models.BooleanField(default=False)
    campaign_price=models.FloatField(blank=False,default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Branchs(models.Model):
    country = models.CharField(blank=False, max_length=100, default="Turkiye")
    city = models.CharField(blank=False, max_length=100)
    name = models.CharField(blank=False, max_length=100)
    location = models.CharField(blank=False,max_length=200,default="")
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

