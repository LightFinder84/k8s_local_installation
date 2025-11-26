import socket
import sys
import time
from etcd_agent import EtcdAgent
from collect import DataCollector
from grpc_agent import GrpcAgent
from plugin_manager import PluginManager

# ------------------------------------- CONFIGURATIONS -------------------------------------
REQUIRED_ARGS = 5 # script_name host port
ETCD_HOST = ""
ETCD_PORT = 0
GRPC_HOST = ""
GRPC_PORT = 0
NODE_HOSTNAME = socket.gethostname()
CONFIG_KEY = f'/config/monitor/{NODE_HOSTNAME}'

if len(sys.argv) != REQUIRED_ARGS:
    print(f"In correct argument.")
    print(f"Usage: {sys.argv[0]} <ETCD_HOST> <ETCD_PORT> <GRPC_HOST> <GRPC_PORT>")
    sys.exit(1)
    
# ------------------------------------------ CODE ------------------------------------------

def main():
    try:
        # connect to etcd
        etcd_agent = EtcdAgent(ETCD_HOST, ETCD_PORT, CONFIG_KEY)
        etcd_agent.start_config_watcher()
        # connect to grpc
        grpc_agent = GrpcAgent(GRPC_HOST, GRPC_PORT)
        grpc_agent.run_client(etcd_agent)
        
        data_collector = DataCollector()
        plugin_manager = PluginManager()
        
        while True:
            
            # collect data
            metric_data = data_collector.execute(etcd_agent.get_metrics())
            
            # apply plugin
            plugin_manager.update_plugins(etcd_agent.get_plugins)
            plugin_manager.execute(metric_data)
            
            # send data
            grpc_agent.report(metric_data)
            
            time.sleep(etcd_agent.get_interval) 
            
    except Exception as e:
        print(f"Exception occured: {e}")
        
if __name__ == "__main__":
    main()