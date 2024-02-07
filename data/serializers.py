from rest_framework import serializers
from .models import TransformerData, TransformerLocationData

class TransformerDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransformerData
        fields = '__all__'
        
    def get_average_values(self, transformer_data):
        # Calculate average values
        if transformer_data:
            average_output_current = sum(data.output_current for data in transformer_data) / len(transformer_data)
            average_output_voltage = sum(data.output_voltage for data in transformer_data) / len(transformer_data)
            average_output_power = sum(data.output_power for data in transformer_data) / len(transformer_data)
            average_output_reactive_power = sum(data.output_reactive_power for data in transformer_data) / len(transformer_data)
            average_output_frequency = sum(data.output_frequency for data in transformer_data) / len(transformer_data)
            average_transformer_loading = sum(data.current_loading_percentage for data in transformer_data)/ len(transformer_data)
            return {
                'average_output_current': round(average_output_current, 2),
                'average_output_voltage': round(average_output_voltage, 2),
                'average_output_power': round(average_output_power, 2),
                'average_output_reactive_power': round(average_output_reactive_power/1000, 2),
                'average_output_frequency': round(average_output_frequency, 2),
                'average_transformer_loading': round(average_transformer_loading, 2),
            }
        
        return {}
    
class TransformerLocationDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransformerLocationData
        fields = '__all__'