import sys
import threading
import traceback
from kafka_client import KafkaClient

# ----------------------------------- CONFIGURATION -----------------------------------
REQUIRED_ARG_COUNT = 1
if len(sys.argv) != REQUIRED_ARG_COUNT + 1:
    print(f"Invalid Arguments.\nUsage: {sys.argv[0]} <CONFIG_PATH>")
    sys.exit(1)
    
CONFIG_PATH = str(sys.argv[1])
CONSUME_TOPIC = "MONITOR-DATA"
PRODUCE_TOPIC = "ANALYSIS-COMMAND"

def main():
    try:
        kafka_client = KafkaClient(CONSUME_TOPIC, PRODUCE_TOPIC, CONFIG_PATH)
        consume_t = threading.Thread(target=kafka_client.consume, daemon=True)
        consume_t.start()
        
    except Exception as e:
        print(f"Exception occured: {e}")
        print(traceback.format_exc())
    finally:
        if kafka_client:
            kafka_client.finalize()


if __name__ == "__main__":
    main()