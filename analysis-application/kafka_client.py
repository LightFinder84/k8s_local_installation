import json
from confluent_kafka import Producer, Consumer


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
        self.consumer = Consumer(self.config['consumer'])
        self.consumer.subscribe([self.consume_topic])
        
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
        
    def consume(self):
        while True:
            msg = self.consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"Error consuming data: {msg.error()}")
                break
            print(f"Received message: {msg.key().decode('utf-8')} from {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")
    
    def finalize(self):
        self.producer.flush()
        self.consumer.close()
    
    
    
    