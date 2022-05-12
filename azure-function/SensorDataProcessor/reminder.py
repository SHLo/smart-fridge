from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import CloudToDeviceMethod, CloudToDeviceMethodResult
import os

IOTHUB_CONN_STR = os.environ['IOTHUB_CONN_STR']
RPI_DEVICE_ID_1 = os.environ['RPI_DEVICE_ID_1']
RPI_DEVICE_ID_2 = os.environ['RPI_DEVICE_ID_2']

module_id = 'Mouth'
method_name = 'speak'


registry_manager = IoTHubRegistryManager(IOTHUB_CONN_STR)

def remind(position):
    payload = {'text': f'food in {position} has become stale'}

    deviceMethod = CloudToDeviceMethod(
        method_name=method_name, payload=payload)

    for device_id in (RPI_DEVICE_ID_1, RPI_DEVICE_ID_2):
        try:
            response = registry_manager.invoke_device_module_method(
                device_id, module_id, deviceMethod)
        
        except:
            pass
