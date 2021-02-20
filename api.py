import requests, json, sys
from colors import *

class ConnioAPI:

    _API_URL = "http://31.3.0.227:8081/v3/"
    _ENDPOINTS = {
        "create_device_profile": {
            "endpoint": "deviceprofiles",
            "success_message": "Device profile has been created"
        },
        "create_property": {
            "endpoint": "properties",
            "success_message": "Property has been created"
        },
        "create_method": {
            "endpoint": "methods",
            "success_message": "Method has been created"
        },
        "create_device": {
            "endpoint": "devices",
            "success_message": "Device has been created"
        },
        "get_app": {
            "endpoint": "apps/",
            "success_message": "App fetched successfully"
        },
        "get_device_profile": {
            "endpoint": "deviceprofiles/",
            "success_message": "Device Profile fetched successfully"
        },
        "list_properties": {
            "endpoint": "properties",
            "success_message": "Property fetched successfully"
        },
        "list_methods": {
            "endpoint": "methods",
            "success_message": "Method fetched successfully"
        },
        "get_device": {
            "endpoint": "devices/",
            "success_message": "Device fetched successfully"
        },
        "get_device_key": {
            "endpoint": "devices/",
            "success_message": "Device Key fetched successfully"
        },
        "check_connection": {
            "endpoint": "devices/",
            "success_message": "Devices were linked"
        },
        "get_historical_temperature_data": {
            "endpoint": "data/devices/",
            "success_message": "Historical Data fetched successfully"
        },
        "get_api_clients": {
            "endpoint": "apiclients",
            "success_message": "API Clients fetched successfully"
        },
        "get_api_client_key": {
            "endpoint": "apiclients/",
            "success_message": "API Clinet key fetched successfully"
        },
        "get_account_info": {
            "endpoint": "accounts/_this_",
            "success_message": "Account info fetched successfully"
        }
    }

    def __init__(self, apikeyId, apikeySecret):
        self.s = requests.Session()
        self.s.headers.update({
            "Content-Type": "application/json",
        })
        self.s.auth = (apikeyId, apikeySecret)
        print(OKBLUE + BOLD + '[+] Authentication was set' + ENDC)

    def check_status(self, response, request, name):
        json_data = json.loads(response.text)
        if response.status_code >= 200 and response.status_code <=399:
            print(OKGREEN + f'[+] {name}: ' + self._ENDPOINTS[request]['success_message'] + ENDC)
            return {"success": True, "data": json_data}
        else:
            print(FAIL + f'[-] {name}: ' + json_data[0]['code'] + ENDC)
            return {"success": False, "data": json_data[0]}

    def url_builder(self, request):
        return self._API_URL + self._ENDPOINTS[request]['endpoint']

    def create_device_profile(self, name, baseProfile):
        print(HEADER + f'[*] {name} is creating...' + ENDC)
        request = 'create_device_profile'
        data = {"name": name, "baseProfile": baseProfile}
        response = self.s.post(self.url_builder(request), json=data)
        return self.check_status(response, request, name)

    def create_property(self, name, ownerId, propType, access, publish):
        print(HEADER + f'[*] {name} is creating...' + ENDC)
        request = 'create_property'
        data = {"name": name, "ownerId": ownerId, "type": propType, "access": access, "publish": publish}
        response = self.s.post(self.url_builder(request), json=data)
        return self.check_status(response, request, name)

    def create_method(self, name, ownerId, access, methodlmpl):
        print(HEADER + f'[*] {name} is creating...' + ENDC)
        request = 'create_method'
        data = {"name": name, "ownerId": ownerId, "access": access, "methodImpl": methodlmpl}
        response = self.s.post(self.url_builder(request), json=data)
        return self.check_status(response, request, name)

    def create_device(self, name, profile, apps):
        print(HEADER + f'[*] {name} is creating...' + ENDC)
        request = 'create_device'
        data = {"name": name, "profile": profile, "apps": [apps]}
        response = self.s.post(self.url_builder(request), json=data)
        return self.check_status(response, request, name)
    
    def get_app(self, name):
        print(HEADER + f'[*] {name} app is being fetched...' + ENDC)
        request = 'get_app'
        response = self.s.get(self.url_builder(request) + name)
        return self.check_status(response, request, name)

    def get_device_profile(self, name):
        print(HEADER + f'[*] {name} device profile is being fetched...' + ENDC)
        request = 'get_device_profile'
        response = self.s.get(self.url_builder(request) + name)
        return self.check_status(response, request, name)

    def get_property(self, name, ownerId):
        # I had to do this because I couldn't search property by name 
        print(HEADER + f'[*] {ownerId} properties are being fetched...' + ENDC)
        request = 'list_properties'
        query = f"?ownerId={ownerId}"
        response = self.s.get(self.url_builder(request) + query)
        success, properties = self.check_status(response, request, ownerId).values()
        if success:
            in_have = next((True for property in properties['results'] if property['name'] == name), False)
            return {'success': in_have, 'data': name}
        else:
            return {'success': success, 'data': properties} 

    def get_method(self, name, ownerId):
        # I had to do this because I couldn't search method by name 
        print(HEADER + f'[*] {ownerId} methods are being fetched...' + ENDC)
        request = 'list_methods'
        query = f"?ownerId={ownerId}"
        response = self.s.get(self.url_builder(request) + query)
        success, methods = self.check_status(response, request, ownerId).values()
        if success:
            in_have = next((True for method in methods['results'] if method['name'] == name), False)
            return {'success': in_have, 'data': name}
        else:
            return {'success': success, 'data': methods} 

    def get_device(self, name):
        print(HEADER + f'[*] {name} device is being fetched...' + ENDC)
        request = 'get_device'
        response = self.s.get(self.url_builder(request) + name)
        return self.check_status(response, request, name)

    def get_device_key(self, id):
        print(HEADER + f'[*] {id} device key is being fetched...' + ENDC)
        request = 'get_device_key'
        url = "{}/apikey".format(id)
        response = self.s.get(self.url_builder(request) + url)
        return self.check_status(response, request, id)

    def connect_to_device(self, gatewayDeviceId, connectedDeviceId, context):
        print(HEADER + f'[*] {gatewayDeviceId} and {connectedDeviceId} connection is checking...' + ENDC)
        request = 'check_connection'
        response = self.s.put(self.url_builder(request) + f"{gatewayDeviceId}/apikey", json=context)
        return self.check_status(response, request, connectedDeviceId)

    def get_historical_temperature_data(self, deviceId, method):
        print(HEADER + f'[*] {deviceId} => {method} historical data being fetched...' + ENDC)
        request = 'get_historical_temperature_data'
        data = {"value": ""}
        response = self.s.post(self.url_builder(request) + f"{deviceId}/methods/{method}", json=data)
        return self.check_status(response, request, method)

    def get_api_clients(self):
        print(HEADER + f'[*] API Clients being fetched...' + ENDC)
        request = 'get_api_clients'
        response = self.s.get(self.url_builder(request))
        return self.check_status(response, request, "API")

    def get_api_client_key(self, apiClientId):
        print(HEADER + f'[*] {apiClientId}: API Client key being fetched...' + ENDC)
        request = 'get_api_client_key'
        response = self.s.get(self.url_builder(request) + f"{apiClientId}/apikey")
        return self.check_status(response, request, apiClientId)

    def get_account_info(self):
        print(HEADER + f'[*] Account info being fetched...' + ENDC)
        request = 'get_account_info'
        response = self.s.get(self.url_builder(request))
        return self.check_status(response, request, "ACCOUNT")