from django.contrib import admin
from data.models import TransformerData, TransformerLocationData
# Register your models here.

@admin.register(TransformerData)
class TransformerDataAdmin(admin.ModelAdmin):
    list_display = [f.name for f in TransformerData._meta.get_fields()]
    fields = [f.name for f in TransformerData._meta.get_fields() if f.name != 'id']

@admin.register(TransformerLocationData)
class TransformerLocationDataAdmin(admin.ModelAdmin):
    list_display = [f.name for f in TransformerLocationData._meta.get_fields()]
    fields = [f.name for f in TransformerLocationData._meta.get_fields()]

# admin.site.register(TransformerData, TransformerDataAdmin)
# admin.site.register(TransformerLocationData, TransformerLocationDataAdmin)
