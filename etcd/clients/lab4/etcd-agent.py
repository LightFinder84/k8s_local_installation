import sys
import etcd3
import json
import socket
import threading
import time

# --------------------------------------------------- Configuration ---------------------------------------------------
REQUIRED_ARGS = 3 # script_name host port
if len(sys.argv) != REQUIRED_ARGS:
    print(f"In correct argument.")
    print(f"Usage: {sys.argv[0]} <etcd-host> <etcd-port>")
    sys.exit(1)
    
ETCD_HOST = str(sys.argv[1])
try:
    ETCD_PORT = int(sys.argv[2])
except Exception:
    print(f"ETCD port must be a number")
    sys.exit(1)
    
NODE_HOSTNAME = socket.gethostname()
CONFIG_KEY = f'/config/monitor/{NODE_HOSTNAME}'

# --------------------------------------------------- Shared resources ---------------------------------------------------
try:
    etcd = etcd3.client(host=ETCD_HOST, port=ETCD_PORT)
except Exception as e:
    print(f"Error connecting to etcd: {e}")
    exit(1)

config_value = {}
config_lock = threading.Lock()

# --------------------------------------------------- Initial configuration ---------------------------------------------------

def initialize_configuration():
    global config_value
    try:
        result, _ = etcd.get(CONFIG_KEY)
        print(f"Processing initial configuration value on key: {CONFIG_KEY}")
        if result:
            with config_lock:
                print(f"Found intial config value: {result.decode('utf-8')}")
                config_value = json.loads(result.decode('utf-8'))
        else:
            with config_lock:
                config_value = { 
                    "plugins": [],
                    "available-plugins": []
                }
                print(f"Initial config value is not set. Proceeding with default value:\n{config_value}")
                etcd.put(CONFIG_KEY, json.dumps(config_value).encode('utf-8'))
    except Exception as e:
        print(f"Error processing initial configuration value: {e}")
        
# --------------------------------------------------- Config watcher ---------------------------------------------------

def handle_config_change(watch_response):
    global config_value
    for event in watch_response.events:
        key = event.key.decode('utf-8')
        value = event.value.decode('utf-8')
        if isinstance(event, etcd3.events.PutEvent):
            if value != config_value:
                with config_lock:
                    config_value = value
                    print(f'New config detected. Updated new config: {config_value}')

def setup_config_watcher():
    try:
        print(f"Start watcher for key {CONFIG_KEY}")
        etcd.add_watch_callback(CONFIG_KEY, handle_config_change)
    except etcd3.exceptions.WatchTimedOut:
        print(f"Config watch timed out. Reconnecting...")
        # todo
    except Exception as e:
        print(f'Error setup config watcher: {e}')
        
# ---------------------------------------------------

if __name__ == "__main__":
    # Initialize configuration
    initialize_configuration()
    
    # Start watcher thread
    config_watcher_t = threading.Thread(target=setup_config_watcher, daemon=True)
    config_watcher_t.start()
    
    # Main thread showing current configuration
    try:
        tmp_config = config_value
        while True:
            with config_lock:
                if config_value != tmp_config:
                    tmp_config = config_value
                    print(f'Current config: {config_value}')
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    
    # Graceful shutdown
    print("Application shutting down")
    config_watcher_t.join(timeout=1)
    print("Shutdown complete.")
    
