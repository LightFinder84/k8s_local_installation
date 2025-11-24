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
    
CONFIG_PREFIX = '/config/monitor/'

try:
    etcd = etcd3.client(host=ETCD_HOST, port=ETCD_PORT)
except Exception as e:
    print(f"Error connecting to etcd: {e}")
    sys.exit(1)
    
    
# -------------------------------- Heartbeat --------------------------------

def get_nodes_list():
    results = etcd.get_prefix(CONFIG_PREFIX)
    nodes = [json.loads(result)['node-id'] for result, _ in results]
    return nodes

def config_controller_main():
    print("\n--- Configuration Controller Active ---")
    print("Commands:")
    print("    hosts                        - List all currently active monitoring agents.")
    print("    plugins <hostname>           - List plugins on an agent.")
    print("    add <hostname> <plugin>      - Add plugin to agent.")
    print("    remove <hostname> <plugin>   - Remove plugin from agent.")
    print("    quit                         - Exit the application.")
    
    try:
        while True:
            command = input("etcd-server > ").strip()
            parts = command.split()
            
            if not parts:
                continue
            
            action = parts[0].lower()
            
            if action == 'quit':
                break
            elif action == 'hosts':
                nodes = get_nodes_list()
                if nodes:
                    print("Active nodes:")
                    for node in nodes:
                        print(f"    {node}")
                else:
                    print("No active nodes found.")
            elif action == 'plugins':
                hostname = parts[1]
                # get config from host
                config_key = CONFIG_PREFIX + hostname
                result, _ = etcd.get(config_key)
                if result:
                    config_value = json.loads(result.value.decode('utf-8'))
                    print(f"Running plugins: {config_value['plugins']}")
                    print(f"Available plugins: {config_value['available-plugins']}")
                else:
                    print(f"Config not found for host {hostname}. Make sure the hostname is correct.")
            elif action == 'add':
                hostname = parts[1]
                plugin = parts[2]
                config_key = CONFIG_PREFIX + hostname
                result, _ = etcd.get(config_key)
                if result:
                    config_value = json.loads(result.value.decode('utf-8'))
                    if plugin not in config_value['available-plugins']:
                        print(f"Plugin {plugin} is not available on agent {hostname}.")
                    elif plugin in config_value['plugins']:
                        print(f"Plugin {plugin} is already running on agent {hostname}.")
                    else:
                        print(f"Apllying plugin {plugin} on host {hostname}.")
                        config_value['plugins'].append(plugin)
                        etcd.put(config_key, json.dumps(config_value).encode('utf-8'))
                else:
                    print(f"Config not found for host {hostname}. Make sure the hostname is correct.")
            elif action == 'remove':
                hostname = parts[1]
                plugin = parts[2]
                config_key = CONFIG_PREFIX + hostname
                result, _ = etcd.get(config_key)
                if result:
                    config_value = json.loads(result.value.decode('utf-8'))
                    if plugin not in config_value['plugins']:
                        print(f"Plugin {plugin} is not running on agent {hostname}.")
                    else:
                        print(f"Removing plugin {plugin} on host {hostname}.")
                        config_value['plugins'].remove(plugin)
                        etcd.put(config_key, json.dumps(config_value).encode('utf-8'))
                else:
                    print(f"Config not found for host {hostname}. Make sure the hostname is correct.")
            else:
                print("Invalid command or fortmat. Use 'set <hostname> <interval>' or 'list'.")
            
    except KeyboardInterrupt:
        pass
    
    print("Configuration Controller shutting down.")



if __name__ == "__main__":
    config_controller_main()
    