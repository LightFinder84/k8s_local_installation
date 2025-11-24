import etcd3
import threading
import time
import sys

# ------------------------------ Configuration ------------------------------
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
    
HEARTBEAT_PREFIX = '/monitor/heartbeat/'

try:
    etcd = etcd3.client(host=ETCD_HOST, port=ETCD_PORT)
except Exception as e:
    print(f"Error connecting to etcd: {e}")
    exit(1)
    
    
# -------------------------------- Heartbeat --------------------------------

def handle_heartbeat_event(watch_response):
    for event in watch_response.events:
        # get key & host-id
        key = event.key.decode('utf-8')
        node_id = key.split('/')[-1]
        
        if isinstance(event, etcd3.events.PutEvent):
            value = event.value.decode('utf-8')
            print(f'[+] Node {node_id} is alive -> {value}')
        elif isinstance(event, etcd3.events.DeleteEvent):
            print(f'[-] Node {node_id} is dead.')

def monitor_hearbeat():
    # attach call back on hearbeat keyprefix
    try:
        print(f"Start monitor heartbeat event on key prefix: {HEARTBEAT_PREFIX}")
        etcd.add_watch_prefix_callback(HEARTBEAT_PREFIX, handle_heartbeat_event)
    except Exception as e:
        print(f"Heartbeat monitoring stopped due to error: {e}")


if __name__ == "__main__":
    # start new thread to monitor heartbeat event
    monitor_t = threading.Thread(target=monitor_hearbeat, daemon=True)
    monitor_t.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    
    print("Shutting down server.")
    monitor_t.join(timeout=1)
    print("Shutdown server completed.")
    