import etcd3
import json
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
CONFIG_PREFIX = '/config/monitor/'
DEFAULT_CONFIG = { "interval": 10 }

try:
    etcd = etcd3.client(host=ETCD_HOST, port=ETCD_PORT)
except Exception as e:
    print(f"Error connecting to etcd: {e}")
    exit(1)
    
    
# -------------------------------- Heartbeat --------------------------------

def get_nodes_list():
    results = etcd.get_prefix(HEARTBEAT_PREFIX)
    nodes = [json.loads(result)['node-id'] for result, _ in results]
    return nodes

def config_controller_main():
    print("\n--- Configuration Controller Active ---")
    print("Commands:")
    print("    list    - List all currently active monitoring agents.")
    print("    set <hostname> <interval> - Push a new interval setting on the agent.")
    print("    quit    - Exit the application")
    
    try:
        while True:
            command = input("etcd-server > ").strip()
            parts = command.split()
            
            if not parts:
                continue
            
            action = parts[0].lower()
            
            if action == 'quit':
                break
            elif action == 'list':
                nodes = get_nodes_list()
                if nodes:
                    print(f"Active Nodes: {', '.join(nodes)}")
                else:
                    print("No active nodes found.")
            elif action == 'set':
                node_id = parts[1]
                try:
                    interval = int(parts[2])
                    config_key = CONFIG_PREFIX + node_id
                    
                    new_config = DEFAULT_CONFIG.copy()
                    new_config['interval'] = interval
                    
                    etcd.put(config_key, json.dumps(new_config))
                    
                    print(f"Successfully sent new config to {node_id} at {config_key}. Interval set to {interval}s")
                    print("(The agent's watcher should update immediately.)")
                except ValueError:
                    print("Error: Interval must be an integer.")
            else:
                print("Invalid command or fortmat. Use 'set <hostname> <interval>' or 'list'.")
            
    except KeyboardInterrupt:
        pass
    
    print("Configuration Controller shutting down.")



if __name__ == "__main__":
    config_controller_main()
    