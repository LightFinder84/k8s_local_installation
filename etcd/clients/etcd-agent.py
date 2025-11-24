import sys
import etcd3
import json
import socket
import threading
import time
import subprocess

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
HEARTBEAT_KEY = f'/monitor/heartbeat/{NODE_HOSTNAME}'
LEASE_TTL = 10

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
                print("Initial config value is not set. Using default value.")
                config_value = { "interval": 10 }
    except Exception as e:
        print(f"Error processing initial configuration value: {e}")
        
# --------------------------------------------------- System data ---------------------------------------------------

def get_cpu_usage():
    command = "top -bn1 | grep \"^%Cpu\" | awk '{print $2}'"
    value = subprocess.run(command, shell=True, capture_output=True, text=True).stdout.strip()
    if value == 'us,': value = '100.0'
    return value

def get_memory_usage():
    command =  "free -m | awk '/^Mem:/ { printf(\"%.2f\", $3/$2 * 100) }'"
    value = subprocess.run(command, shell=True, capture_output=True, text=True).stdout.strip()
    return value

def get_read_io():
    command = "iostat -d -k 1 2 | awk 'NR>7 {read+=$3} END {print read}'"
    value = subprocess.run(command, shell=True, capture_output=True, text=True).stdout.strip()
    return value

def get_write_io():
    command = " iostat -d -k 1 2 | awk 'NR>7 {write+=$4} END {print write}'"
    value = subprocess.run(command, shell=True, capture_output=True, text=True).stdout.strip()
    return value
        
# --------------------------------------------------- Heartbeat threading ---------------------------------------------------

def send_hearbeat_signal():
    # Create a lease for TTL management
    lease = etcd.lease(LEASE_TTL)
    print(f"Starting heartbeat thread. TTL: {LEASE_TTL}s, Lease ID: {lease.id}")
    
    # Calculate refresh interval (should be less than TTL)
    refresh_interval = LEASE_TTL / 2
    
    try:
        # Loop
        while True:
            # send hearbeat data
            heartbeat_data = json.dumps({
                'ts': int(time.time()),
                'node-id': NODE_HOSTNAME,
                'cpu': get_cpu_usage(),
                'mem': get_memory_usage(),
                'read': get_read_io(),
                'write': get_write_io()
            })
            etcd.put(HEARTBEAT_KEY, heartbeat_data, lease=lease)
            
            # refresh lease
            lease.refresh()
            
            print(f"[HEARTBEAT] Sent pulse to {HEARTBEAT_KEY}. Next in {refresh_interval:.2f}s.")
            
            # sleep
            time.sleep(refresh_interval)
            
    except Exception as e:
        print(f'Error sending heartbeat data: {e}')
    finally:
        # Revoke the lease on clean shutdown (optional, but good practice)
        if 'lease' in locals():
            lease.revoke()
        print(f'Heartbeat stopped for node {NODE_HOSTNAME}')
        
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
    
    # Start heartbeat thread
    heartbeat_t = threading.Thread(target=send_hearbeat_signal, daemon=True)
    heartbeat_t.start()
    
    # Start watcher thread
    config_watcher_t = threading.Thread(target=setup_config_watcher, daemon=True)
    config_watcher_t.start()
    
    # Main thread showing current configuration
    try:
        while True:
            with config_lock:
                print(f'Current config: {config_value}')
            time.sleep(5)
    except KeyboardInterrupt:
        pass
    
    # Graceful shutdown
    print("Application shutting down")
    heartbeat_t.join(timeout=1)
    config_watcher_t.join(timeout=1)
    print("Shutdown complete.")
    
