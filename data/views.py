from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .models import TransformerData, TransformerLocationData
from .serializers import TransformerDataSerializer, TransformerLocationDataSerializer
from django.utils import timezone
from django.db.models import Avg, Max
from dashboard.models import Notifications
from . import threshold_checks
# from corsheaders.decorators import cors_headers


@csrf_exempt
def index(request):
    if request.method == 'POST':
        try:
            # Extract JSON data from the request
            print("request.POST",request.POST)
            
            data = json.loads(request.body.decode('utf-8'))
            print("Decoded Data", data)
            received_data = data.get('data', {})
            print("Received Data:", received_data)
            
            # check if transformer is registered
            transformer_location_data = TransformerLocationData.objects.values(('devUID'))
            print(transformer_location_data)
            
            for location in transformer_location_data:   
                            
                if received_data['devUID'] == location['devUID']: 
                    nominal_power_rating = TransformerLocationData.objects.get(devUID=location['devUID']).nominal_power_rating  
                    transformer_data = TransformerData(
                        devUID=received_data['devUID'],
                        output_current=received_data['output_current'],
                        output_voltage=received_data['output_voltage'],
                        output_power=received_data['output_power'],
                        output_reactive_power=received_data['output_reactive_power'],
                        output_frequency=received_data['output_frequency'],
                        timestamp=timezone.now(),
                        nominal_power_rating=nominal_power_rating,
                    )
                    
                    transformer_data.save()
                    
                    threshold_checks.check_thresholds(transformer_data)

                    return JsonResponse({'message': 'Data received successfully'})
            return JsonResponse({'message': 'Unregistered Transformer'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        finally:
            print(request.POST)
    return JsonResponse({'error': 'Unsupported method'}, status=405)


def get_latest_transformer_data(request):
    
    transformer_location_data = TransformerLocationData.objects.all()
    
    # get only transformer data for the registered ones
    transformer_data = TransformerData.objects.filter(devUID__in=transformer_location_data.values('devUID'))
    
    
    #query for the latest data for each devUID
    latest_data_per_dev_UID = transformer_data.values('devUID').annotate(latest_timestamp=Max('timestamp')).order_by()

    #retrieve the actual data based on the latest timestamp
    latest_data = TransformerData.objects.filter(
        devUID__in=latest_data_per_dev_UID.values('devUID'),
        timestamp__in=latest_data_per_dev_UID.values('latest_timestamp')
    )

    serializer = TransformerDataSerializer(latest_data, many=True) 
    location_data  = TransformerLocationDataSerializer(transformer_location_data, many=True)   
    # print(serializer.data)
    
    return JsonResponse({
        'transformer_data': serializer.data,
        'transformer_location_data': location_data.data
    })  
    
@csrf_exempt      
def register(request):
    if request.method == 'POST':
        request_data = request.POST
        transformer = TransformerLocationData(
            devUID=request_data['devUID'],
            latitude=request_data['latitude'],
            longitude=request_data['longitude'],
            nominal_power_rating=request_data['nominal_power_rating']
        )
        
        transformer.save()

        notification = Notifications(
            title="Transformer Added",
            priority="info",
            text=f"Transformer at (Latitude: {transformer.latitude}, Longitude: {transformer.longitude}) has been successfully registered\nTransformer devUID: {transformer.devUID}",
            timestamp=timezone.now()
        )
        notification.save()

        return JsonResponse({'message': 'Transformer Registered'}, status=200)
    else:
        return JsonResponse({'message': 'Method Not Allowed'}, status=405)

# @cors_headers()
# def get_average_values(request):
#     transformer_location_data = TransformerLocationData.objects.all()
    
#     # get only transformer data for the registered ones
#     transformer_data = TransformerData.objects.filter(devUID__in=transformer_location_data.values('devUID'))
     
#     # average values of the transformer parameters
#     average_values = TransformerDataSerializer().get_average_values(transformer_data)
    
#     # moving average values for the transformer parameters
#     # Calculate moving average over the last 24 hours with a window of 15 minutes
#     twenty_four_hours_ago = timezone.now() - timezone.timedelta(hours=24*7)
#     moving_average_queryset = TransformerData.objects.filter(timestamp__gte=twenty_four_hours_ago, devUID__in=transformer_location_data.values('devUID'))

            
#     # Calculate moving average with a window of 15 minutes
#     moving_average_values = []
#     fifteen_minutes_delta = timezone.timedelta(minutes=15)
#     current_timestamp = twenty_four_hours_ago

#     while current_timestamp <= timezone.now():
#         # Filter data within the current 15-minute window
#         window_start = current_timestamp - fifteen_minutes_delta
#         window_end = current_timestamp
#         window_data = moving_average_queryset.filter(timestamp__gte=window_start, timestamp__lt=window_end)

#         # Calculate average values for the current window
#         if window_data.exists():
#             window_average_values = window_data.aggregate(
#                 Avg('output_current'),
#                 Avg('output_voltage'),
#                 Avg('output_power'),
#                 Avg('output_reactive_power'),
#                 Avg('output_frequency'),
#                 Avg('current_loading_percentage')
#             )
#             moving_average_values.append({
#                 'timestamp': current_timestamp,
#                 'average_values': window_average_values,
#             })

#         # Move to the next 15-minute window
#         current_timestamp += fifteen_minutes_delta
#     return JsonResponse({
#         'average_values': average_values,
#         'moving_average_values': moving_average_values,
#         })

# from django.db.models import Avg

def get_average_values(request):
    transformer_location_data = TransformerLocationData.objects.all()

    # Get only transformer data for the registered ones
    transformer_data = TransformerData.objects.filter(
        devUID__in=transformer_location_data.values('devUID')
    )

    # Average values of the transformer parameters
    average_values = transformer_data.aggregate(
        Avg('output_current'),
        Avg('output_voltage'),
        Avg('output_power'),
        Avg('output_reactive_power'),
        Avg('output_frequency'),
        Avg('current_loading_percentage')
    )

    # Calculate moving average values for the transformer parameters
    twenty_four_hours_ago = timezone.now() - timezone.timedelta(hours=24)
    moving_average_queryset = TransformerData.objects.filter(
        timestamp__gte=twenty_four_hours_ago,
        devUID__in=transformer_location_data.values('devUID')
    )

    moving_average_values = []
    fifteen_minutes_delta = timezone.timedelta(minutes=15)
    current_timestamp = twenty_four_hours_ago

    while current_timestamp <= timezone.now():
        window_start = current_timestamp - fifteen_minutes_delta
        window_end = current_timestamp

        window_data = moving_average_queryset.filter(
            timestamp__range=(window_start, window_end)
        ).aggregate(
            Avg('output_current'),
            Avg('output_voltage'),
            Avg('output_power'),
            Avg('output_reactive_power'),
            Avg('output_frequency'),
            Avg('current_loading_percentage')
        )

        moving_average_values.append({
            'timestamp': current_timestamp,
            'average_values': window_data
        })

        current_timestamp += fifteen_minutes_delta

    return JsonResponse({
        'average_values': average_values,
        'moving_average_values': moving_average_values,
    })


