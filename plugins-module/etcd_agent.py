import etcd3
import threading
import json
import socket

class EtcdAgent:
    
    def __init__(self, host, port, config_key):
        self.host = host
        self.port = port
        self.etcd = None
        self.config_key = config_key
        self.config_value = {}
        self.config_lock = threading.Lock()
        
        self.config_watcher_t: threading.Thread = None
        
        self.establish_connection()
        self.initialize_configuration()
        
    def finalize(self):
        if self.config_watcher_t:
            self.config_watcher_t.join(timeout=1)
        
    def establish_connection(self):
        try:
            self.etcd = etcd3.client(host=self.host, port=self.port)
        except Exception as e:
            print(f"Error connecting to etcd.")
            raise e
        
    def initialize_configuration(self):
        try:
            result, _ = self.etcd.get(self.config_key)
            print(f"Processing initial configuration value on key: {self.config_key}")
            if result:
                with self.config_lock:
                    print(f"Found intial config value: {result.decode('utf-8')}")
                    self.config_value = json.loads(result.decode('utf-8'))
            else:
                with self.config_lock:
                    self.config_value = {
                        "interval": 5,
                        "metrics": ['cpu', 'mem', 'disk_read', 'disk_write', 'net_in', 'net_out'],
                        "plugins": [],
                        "available-plugins": ["plugin.hello.HelloPlugin", "plugin.dedup.DeDupPlugin"],
                        "node-id": socket.gethostname()
                    }
                    print(f"Initial config value is not set. Proceeding with default value:\n{self.config_value}")
                    self.etcd.put(self.config_key, json.dumps(self.config_value).encode('utf-8'))
        except Exception as e:
            print("Error initialize agent configuration.")
            raise e
        
    def config_change_handler(self, watch_response):
        for event in watch_response.events:
            value = event.value.decode('utf-8')
            if isinstance(event, etcd3.events.PutEvent):
                if value != self.config_value:
                    with self.config_lock:
                        self.config_value = value
                        print(f'New config detected. Updated new config: {self.config_value}')
            
    def setup_config_watcher(self):
        try:
            print(f"Start watcher for key {self.config_key}")
            self.etcd.add_watch_callback(self.config_key, self.config_change_handler)
        except Exception as e:
            print("Error setup config watcher.")
            raise e
        
    def start_config_watcher(self):
        config_watcher_t = threading.Thread(target=self.setup_config_watcher, daemon=True)
        config_watcher_t.start()
        
    def get_config(self):
        with self.config_lock:
            return self.config_value
    
    def set_config(self, config_value):
        with self.config_lock:
            return config_value
        
    def get_interval(self):
        return self.config_value['interval']
    
    def get_plugins(self):
        return self.config_value['plugins']
    
    def get_metrics(self):
        return self.config_value['metrics']
    
    def get_available_plugins(self):
        return self.config_value['available-plugins']
    
    def get_node_id(self):
        return self.config_value['node-id']
    
    def set_interval(self, value):
        try:
            value = int(value)
            with self.config_lock:
                self.config_value.interval = value
        except Exception as e:
            print("Interval value must be a number.")
            raise e
        
        try:
            with self.config_lock:
                print(f"Update interval value: {value}")
                self.etcd.put(self.config_key, json.dumps(self.config_value)).encode('utf-8')
        except Exception as e:
            print("Error update config value to gRPC server")
            raise e