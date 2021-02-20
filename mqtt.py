import json, asyncio, random
import paho.mqtt.client as mqtt
from colors import *

class Session:
    def __init__(self, loop, client):
        self.loop = loop
        self.client = client
        self.client.on_socket_open = self.on_socket_open
        self.client.on_socket_close = self.on_socket_close
        self.client.on_socket_register_write = self.on_socket_register_write
        self.client.on_socket_unregister_write = self.on_socket_unregister_write

    def on_socket_open(self, client, userdata, sock):
        print(OKGREEN + f'[+] Socked opened: ' + str(sock) + ENDC)
        def cb():
            print(OKBLUE + '[*] Socket is readable, calling loop_read...' + ENDC)
            client.loop_read()
        self.loop.add_reader(sock, cb)
        print(HEADER + f'[*] Async task is creating...' + ENDC)
        self.misc = self.loop.create_task(self.misc_loop())
    
    def on_socket_close(self, client, userdata, sock):
        print(OKGREEN + f'[-] Socket closed: ' + str(sock) + ENDC)
        self.loop.remove_reader(sock)
        print(OKGREEN + f'[-] Async task closing... ' + str(self.misc) + ENDC)
        self.misc.cancel()

    def on_socket_register_write(self, client, userdata, sock):
        print(OKBLUE + f'[*] Watching socket for writability.' + ENDC)
        def cb():
            print(OKBLUE + '[*] Socket is writable, calling loop_write...' + ENDC)
            client.loop_write()
        self.loop.add_writer(sock, cb)
    
    def on_socket_unregister_write(self, client, userdata, sock):
        print(OKGREEN + f'[-] Stop watching socket for writability.' + ENDC)
        self.loop.remove_writer(sock)

    async def misc_loop(self):
        print(OKGREEN + f'[+] misc_loop started: ' + str(self.misc) + ENDC)
        while self.client.loop_misc() == mqtt.MQTT_ERR_SUCCESS:
            try:
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                break
        print(OKBLUE + '[+] misc_loop finished' + str(self.misc) + ENDC)

class AsyncMqtt:
    def __init__(self, loop, broker, device, type, topic):
        self.loop = loop
        self.broker = broker
        self.device = device
        self.publish_topic = "connio/data/out/devices/{}/methods/json".format(device.id)
        self.subscribe_topic = f"{topic['username']}/apps/{topic['appname']}/devices/{topic['targetDevice']}/properties/{topic['property']}"
        self.type = type
        self.property = topic['property']

    def on_connect(self, client, userdata, flags, rc):
        print(OKGREEN + f'[+] Connected to device: ' + self.device.name + ENDC)
        if self.type == 'subscribe':
            client.subscribe(self.subscribe_topic)
            print(OKGREEN + f'[+] {self.subscribe_topic} is subscribing... ' + ENDC)

    def on_message(self, client, userdata, msg):
        if not self.got_message:
            print(FAIL + f'[-] Got unexpected message: '+ str(msg) + ENDC)
        else:
            self.got_message.set_result(msg.payload)
    
    def on_disconnect(self, client, userdata, rc):
        self.disconnected.set_result(rc)
    
    async def main(self):
        self.disconnected = self.loop.create_future()
        self.got_message = None

        self.client = mqtt.Client(client_id=self.device.id)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

        session = Session(self.loop, self.client)
        self.client.username_pw_set(username=self.device.apiKeyId, password=self.device.apiKeySecret)

        print(OKBLUE + f'[*] Connecting to {self.broker.name} => {self.device.name} ...' + ENDC) 
        self.client.connect(self.broker.ip, self.broker.port, self.broker.keepAlive)

        while True:
            print(WARNING + BOLD + '''
            [!] Press CTRL + C to close qmtt and view all historical data
             - Please wait at least 1 publish for getHistoricalValue - [!]
            '''+ ENDC)
            if self.type == 'publish':
                await asyncio.sleep(5)
                feed = {'dps': [  
                    { 'method': 'setTemperature', 'value': random.randint(10, 50) }
                ]}        
                data = json.dumps(feed)
                print(OKGREEN + f'[+] Publising: '+ data + ENDC)
                self.client.publish(self.publish_topic, data, qos=1)
            else:
                await asyncio.sleep(5)
                self.got_message = self.loop.create_future()
                msg = await self.got_message
                print(OKGREEN + BOLD + '[+] Subscribe result for {} value: '.format(self.property)+ str(msg, 'utf-8') + ENDC)
                self.got_message = None


        self.client.disconnect()
        print(OKGREEN + '[-] Disconnected: {}'.format(await self.disconnected) + ENDC)

