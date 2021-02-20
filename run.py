import os, sys, asyncio, signal
from dotenv import load_dotenv
from api import ConnioAPI
from arya import * # Account, App, ApiClient, DeviceProfile, Device, Broker
from mqtt import AsyncMqtt
from colors import * # HEADER, OKBLUE, OKGREEN, WARNING, FAIL, ENDC, BOLD, UNDERLINE
from time import sleep
load_dotenv()

_auth_error_text = "Please create an .env file and enter your authentication information" # For the forgetten .env file
_broker_error_text = "Please create an .env file and enter your broker information" # For the forgetten .env file

################ Names of devices or profiles to be created with API ###################
_broker_name = "Digiterra" # Broker Name
_keep_alive = 60 # Keep Alive
_app_name = "sample" # App name
_gp_name = "Gateway" # Gateway Profile Name
_cdp_name = "ConnectedDevice" # Connected Device Profile Name
_gbp_name = "Gateway-Based-Profile" # Gateway Based Profile Name
_cdbp_name = "Connected-Device-Based-Profile" # Conneted Device Based Profile Name
_property_name = "temperature" # Connected Device Based Profile Property
_prop_type = "number" # for Connected Device Temperature property
_access = "public" # for Connected Device Temperature property
_publish = "always" # for connected Device Temperature property
_gateway_method_name = "setTemperature" # Gateway Profil Based Profile Method
_connected_device_method_name = "getHistoricalValue" # Connected Device Profile Based Profile Method
_gbpb_device_name = "Gateway-Device" # Gateway Based Profile Based Device Name
_cdbpb_device_name = "Connected-Device" # Connected Device Profile Based Device Name
################ Eof Names of devices or profiles to be created with API ###################

def exception_handler(e):
    # To handle exceptions
    exc_type, exc_obj, exc_tb = sys.exc_info()
    sys.exit(FAIL + f'[-] Line {exc_tb.tb_lineno}: {exc_type} for {exc_obj}'+ ENDC)

# To subscribe
def create_account():
    try:
        global account
        success, data = api.get_account_info().values()
        if success:
            account = Account(data['name'], data['id'])
        else:
            Exception

    except Exception as e:
        exception_handler(e)

def create_app():
    try:
        # To plug devices the app data is fetch
        global app
        success, data = api.get_app(_app_name).values()
        if success:
            app = App(data['name'], data['id'])
        else:
            Exception

    except Exception as e:
        exception_handler(e)

def create_api_clients():
    try:
        # For subscribe to temperature value
        global apiClient
        in_have, clients = api.get_api_clients().values()
        if in_have:
            target_client = clients['results'][0]
            success, data = api.get_api_client_key(target_client['id']).values()
            if success:
                apiClient = ApiClient(target_client['name'], target_client['id'], data['id'], data['secret'])
            else:
                Exception
        else:
            Exception

    except Exception as e:
        exception_handler(e)

def get_gateway_profile():
    try:
        # To create a new `Gateway Based profile` `Gateway Profile` data is fetch 
        global gatewayProfile
        success, data = api.get_device_profile(_gp_name).values()
        if success:
            gatewayProfile = DeviceProfile(data['name'], data['id'])
        else:
            Exception

    except Exception as e:
        exception_handler(e)

def get_connected_device_profile():
    try:
        # To create a new `Connected Device Based` profile `Connected Device Profile` data is fetch 
        global connectedDeviceProfile
        success, data = api.get_device_profile(_cdp_name).values()
        if success:
            connectedDeviceProfile = DeviceProfile(data['name'], data['id'])
        else:
            Exception

    except Exception as e:
        exception_handler(e)

def create_gb_profile():
    try:
        # To create a new `Gateway Based Profile`
        global gatewayBasedProfile
        success, data = api.get_device_profile(_gbp_name).values()
        # if success this profile pre-created
        if success:
            # Create profile object with previously created data
            gatewayBasedProfile = DeviceProfile(data['name'], data['id'])
        else:
            # Create profile object with API
            new_profile = api.create_device_profile(_gbp_name, gatewayProfile.id)
            gatewayBasedProfile = DeviceProfile(new_profile['data']['name'], new_profile['data']['id'])
    except Exception as e:
        exception_handler(e)

def create_cdp_profile():
    try:
        # To create a new `Connected Device Based Profile`
        global connectedDeviceBasedProfile
        success, data = api.get_device_profile(_cdbp_name).values()
        # if success this profile pre-created
        if success:
            # Create profile object with previously created data
            connectedDeviceBasedProfile = DeviceProfile(data['name'], data['id'])
        else:
            # Create profile object with API
            new_profile = api.create_device_profile(_cdbp_name, connectedDeviceProfile.id)
            connectedDeviceBasedProfile = DeviceProfile(new_profile['data']['name'], new_profile['data']['id'])
    except Exception as e:
        exception_handler(e)

def create_connected_device_profile_property():
    try:
        success, data = api.get_property(_property_name, connectedDeviceBasedProfile.id).values()
        if success:
            connectedDeviceBasedProfile.property = data
        else:
            new_property = api.create_property(_property_name, connectedDeviceBasedProfile.id, _prop_type, _access, _publish)
            connectedDeviceBasedProfile.property = _property_name
    except Exception as e:
        exception_handler(e)

def create_gateway_profile_method():
    try:
        success, data = api.get_method(_gateway_method_name, gatewayBasedProfile.id).values()
        if success:
            gatewayBasedProfile.method = _gateway_method_name
        else:
            method = {
            "funcBody": """return this.setDeviceProperty("{}", "{}",""".format(cdbpbDevice.id, _property_name) + """  {
                value: value,
                time: new Date().toISOString()
            }).then(prop => prop.value);
            """,
            "script": "javascript"
            }           
            new_method = api.create_method(_gateway_method_name, gatewayBasedProfile.id, _access, method)
            gatewayBasedProfile.method = _gateway_method_name
    except Exception as e:
        exception_handler(e)

def create_connected_device_profile_method():
    try:
        success, data = api.get_method(_connected_device_method_name, connectedDeviceBasedProfile.id).values()
        if success:
            connectedDeviceProfile.method = _connected_device_method_name
        else:
            method = {
            "funcBody": """let query = {
                "aggregators": [
                {
                    "name": "sum",
                    "sampling": {
                    "value": 99,
                    "unit": "years"
                    }
                }
                ]
            };
            return this.readData("temperature", query).then(resultSet => {
                return resultSet.results[0].values[0].v;
            });
            """,
            "script": "javascript"
            }
            new_method = api.create_method(_connected_device_method_name, connectedDeviceBasedProfile.id, _access, method)
            connectedDeviceProfile.method = _connected_device_method_name
    except Exception as e:
        exception_handler(e)

# Gateway Based Profile Based Device
def create_gbpb_device():
    try:
        global gbpbDevice
        in_have, device = api.get_device(_gbpb_device_name).values()
        if in_have:
            success, device_key = api.get_device_key(device['id']).values()
            if success:
                gbpbDevice = Device(device['name'], device['id'], device_key['id'], device_key['secret'])
            else:
                raise Exception
        else:
            new_device = api.create_device(_gbpb_device_name, gatewayBasedProfile.id, app.name)
            # Because the server is not updated immediately
            sleep(2)
            success, device_key = api.get_device_key(new_device['data']['id']).values()
            if success:
                gbpbDevice = Device(new_device['data']['name'], new_device['data']['id'], device_key['id'], device_key['secret'])
            else:
                raise Exception

    except Exception as e:  
        exception_handler(e)

# Connected Device Based Profile Based Device
def create_cdbpb_device():
    try:
        global cdbpbDevice
        in_have, device = api.get_device(_cdbpb_device_name).values()
        if in_have:
            success, device_key = api.get_device_key(device['id']).values()
            if success:
                cdbpbDevice = Device(device['name'], device['id'], device_key['id'], device_key['secret'])
            else:
                raise Exception
        else:
            new_device = api.create_device(_cdbpb_device_name, connectedDeviceBasedProfile.id, app.name)
            # Because the server is not updated immediately
            sleep(2)
            success, device_key = api.get_device_key(new_device['data']['id']).values()
            if success:
                cdbpbDevice = Device(new_device['data']['name'], new_device['data']['id'], device_key['id'], device_key['secret'])
            else:
                raise Exception

    except Exception as e:  
        exception_handler(e)

def connect_to_gateway_device():
    try:
        context = {
            "context": {
                "type": "device",
                "ids": [
                f"{gbpbDevice.id}", 
                f"{cdbpbDevice.id}" 
                ]
            }
        }
        api.connect_to_device(gbpbDevice.id, cdbpbDevice.id, context)
            
    except Exception as e:
        exception_handler(e)

def create_environment():
    create_account()
    create_app()
    create_api_clients()
    get_gateway_profile()
    get_connected_device_profile()
    create_gb_profile()
    create_cdp_profile()
    create_connected_device_profile_property()
    create_connected_device_profile_method()
    create_gbpb_device()
    create_cdbpb_device()
    create_gateway_profile_method()
    connect_to_gateway_device()


def connect_via_mqtt():
    print(OKGREEN + f'[+] Starting for xx...' + ENDC)
    global loop
    loop = asyncio.get_event_loop()
    # To subscribe
    topic = {'username': account.name, 'appname': app.name, 'targetDevice': cdbpbDevice.id, 'property': _property_name}
    devices = [
        {'type': 'publish', 'name': gbpbDevice},
        {'type': 'subscribe', 'name': apiClient}
    ]
    connections = [AsyncMqtt(loop, broker, device['name'], device['type'], topic).main() for device in devices]
    loop.run_until_complete(asyncio.gather(*connections))
    loop.close()
    print(OKGREEN + f'[+] Finished xx...' + ENDC)

if __name__ == '__main__':
    apikeyId = os.environ.get("API_KEY_ID")
    apikeySecret = os.environ.get("API_KEY_SECRET")
    brokerIp = os.environ.get("BROKER_IP")
    brokerPort = os.environ.get("BROKER_PORT")

    # Check .env file
    api = ConnioAPI(apikeyId, apikeySecret) if apikeyId and apikeySecret else sys.exit(FAIL + f'[-] {_auth_error_text}' + ENDC)
    broker = Broker(_broker_name, brokerIp, int(brokerPort), _keep_alive) if brokerIp and brokerPort else sys.exit(FAIL + f'[-] {_broker_error_text}' + ENDC)
    create_environment()
    
    # To catch Ctrl + C
    def signal_handler(sig, frame):
        asyncio.sleep(5)
        success, data = api.get_historical_temperature_data(cdbpbDevice.id, _connected_device_method_name).values()
        print(OKGREEN + '[+] Total {} entry: {}'.format(_property_name, data['result']) + ENDC)
        print(OKGREEN + f'[-] Closing...' + ENDC)
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    connect_via_mqtt()
    signal.pause()


    