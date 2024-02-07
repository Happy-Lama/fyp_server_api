from .models import TransformerData
from dashboard.models import Notifications
from django.utils import timezone

ACCEPTABLE_VOLTAGE = [220, 240]
ACCEPTABLE_REACTIVE_POWER = 0.3 #30% of the active power
ACCEPTABLE_FREQUENCY = [47, 53]


def check_thresholds(transformer : TransformerData):
    notifications = []
    if not (ACCEPTABLE_VOLTAGE[0] <= transformer.output_voltage  <= ACCEPTABLE_VOLTAGE[1]):
        notification = Notifications(
            priority='warning',
            title=f'Voltage out of range ({timezone.now()})',
            text=f'Transformer output voltage is out of acceptable range. Transformer: {transformer.devUID}, Output Voltage: {transformer.output_voltage}'
        )
        notifications.append(notification)

    if not transformer.output_reactive_power/transformer.output_power <= ACCEPTABLE_REACTIVE_POWER:
        notification = Notifications(
            priority='warning',
            title=f'Reactive power out of range ({timezone.now()})',
            text=f'Transformer output reactive power is above 30% limit. Transformer: {transformer.devUID}, Reactive Power: {transformer.output_reactive_power/transformer.output_power} of Active power'
        )
        notifications.append(notification)

    if not (ACCEPTABLE_FREQUENCY[0] <= transformer.output_frequency  <= ACCEPTABLE_FREQUENCY[1]):
        notification = Notifications(
            priority='warning',
            title=f'Frequency out of range ({timezone.now()})',
            text=f'Transformer Frequency is out of acceptable range. Transformer: {transformer.devUID}, Frequency: {transformer.output_frequency}'
        )
        notifications.append(notification)

    if notifications:
        for notification in notifications:
            notification.save()