from django.db import models
from django.utils import timezone
# Create your models here.

class Notifications(models.Model):
    priority = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=timezone.now)
    text = models.CharField(max_length=255)
    title = models.CharField(max_length=255)