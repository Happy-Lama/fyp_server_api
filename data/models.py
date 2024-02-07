from django.db import models
from django.utils import timezone

# Create your models here.
class TransformerData(models.Model):
    devUID = models.CharField(max_length=255)
    output_current = models.FloatField(default=0)
    output_voltage = models.FloatField(default=0)
    output_power = models.FloatField(default=0)
    output_reactive_power = models.FloatField(default=0)
    output_frequency = models.FloatField(default=0)
    timestamp = models.DateTimeField(default=timezone.now)
    nominal_power_rating = models.PositiveIntegerField(default=100)
    current_loading_percentage = models.FloatField(default=0)
    

    def calculate_transformer_loading(self):
        return (
            (self.output_power / (self.nominal_power_rating * 1000)) * 100
            if self.nominal_power_rating != 0
            else 0
        )
    
    def save(self, *args, **kwargs):
        # Set the default value before saving
        if self.current_loading_percentage == 0:
            self.current_loading_percentage = self.calculate_transformer_loading()

        super().save(*args, **kwargs)
    
class TransformerLocationData(models.Model):
    devUID = models.CharField(max_length=255, primary_key=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    nominal_power_rating = models.PositiveBigIntegerField(default=100)
    operational = models.BooleanField(default=True)