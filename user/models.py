# Create your models here.

from django.db import models
from django.contrib.auth.models import  AbstractUser


class Users(AbstractUser):
    #username=models.CharField(max_length=100, verbose_name=u"username", unique=True)
    class Meta:
        verbose_name="doctor"
        verbose_name_plural=verbose_name
