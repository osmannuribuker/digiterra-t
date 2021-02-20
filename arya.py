class Account:
    def __init__(self, name, id):
        self.name = name
        self.id = id

class App:
    def __init__(self, name, id):
        self.name = name
        self.id = id

class ApiClient:
    def __init__(self, name, id, apiKeyId, apiKeySecret):
        self.name = name
        self.id = id
        self.apiKeyId = apiKeyId
        self.apiKeySecret = apiKeySecret
        
class DeviceProfile:
    def __init__(self, name, id, property=None, method=None):
        self.name = name
        self.id = id
        self.property = property
        self.method = method

class Device:
    def __init__(self, name, id, apiKeyId, apiKeySecret):
        self.name = name
        self.id = id
        self.apiKeyId = apiKeyId
        self.apiKeySecret = apiKeySecret

class Broker:
    def __init__(self, name, ip, port, keepAlive):
        self.name = name
        self.ip = ip
        self.port = port
        self.keepAlive = keepAlive