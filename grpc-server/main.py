import sys
import time
import traceback
from grpc_server import GrpcServer
from kafka_client import KafkaClient

# -------------------------------------- CONFIGURATION --------------------------------------
REQUIRED_ARGS_COUNT = 2

if len(sys.argv) != REQUIRED_ARGS_COUNT + 1:
    print(f"Incorrect argument. Usage: {sys.argv[0]} <GRPC_MAX_WORKERS> <KAFKA_CONFIG_FILE>")
    sys.exit(1)
    
GRPC_MAX_WORKERS = int(sys.argv[1])
KAFKA_CONFIG_FILE = str(sys.argv[2])
CONSUME_TOPIC = "ANALYSIS-COMMAND"
PRODUCE_TOPIC = "MONITOR-DATA"

def main():
    try:
        kafka_client = KafkaClient(PRODUCE_TOPIC, CONSUME_TOPIC, KAFKA_CONFIG_FILE)
        grpc_server = GrpcServer(GRPC_MAX_WORKERS, kafka_client)
        grpc_server.startServer()
        
        while True:
            time.sleep(1)
        
    except Exception as e:
        print(f"Exception occured: {e}")
        print(traceback.format_exc())
    finally:
        kafka_client.finalize()
        grpc_server.finalize()

if __name__ == "__main__":
    main()