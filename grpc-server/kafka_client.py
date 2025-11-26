import json
from confluent_kafka import Producer

conf = {
    'bootstrap.servers': 'worker-01:30092,worker-02:30192,worker-03:30292'
}
producer = Producer(conf)

def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")
        
for i in range(10):
    message = f'Hello Kafka {i}'
    producer.produce('TEST_TOPIC', message.encode('utf-8'), callback=delivery_report)
    producer.poll(0) # Trigger delivery callback
    
producer.flush() # Wait for all messages to be delivered callback



# -------------------------------------------------

def read_json_file(filename):
    """Loads a JSON file into a Python dictionary."""
    try:
        # 'r' stands for read mode
        with open(filename, 'r') as file:
            # json.load() reads the file stream and converts JSON to a Python dictionary
            data = json.load(file)
            print("File loaded successfully.")
            return data
            
    except FileNotFoundError as e:
        print(f"Error: The file '{filename}' was not found.")
        raise e
    except json.JSONDecodeError as e:
        print(f"Error: The file '{filename}' contains invalid JSON.")
        raise e

# Produce monitoring data
# Consume command data
class KafkaClient():
    
    def __init__(self, consume_topic, produce_topic, config_path):
        self.consume_topic = consume_topic
        self.produce_topic = produce_topic
        self.config = read_json_file(config_path)
        self.producer = Producer(self.config['producer'])
        
    def produce(self, data):
        print(f"Producing data")
        value = {
            "time": data.time,
            "hostname": data.hostname,
            "metric": data.metric,
            "value": data.value
        }
        self.producer.produce(self.produce_topic, data.hostname, json.dumps(value).encode('utf-8'))
        self.producer.poll(0)
    
    def finalize(self):
        producer.flush()
    
    
    
    