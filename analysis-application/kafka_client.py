import json
from confluent_kafka import Producer, Consumer
from analysis import Analysis


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
        self.analysis = Analysis()
        
    def consume(self):
        while True:
            msg = self.consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"Error consuming data: {msg.error()}")
                break
            
            data = json.loads(msg.value().decode('utf-8'))
            print(f"[ANALYSIS]\nReceived monitor data from topic {self.consume_topic}. Source Agent: {data['hostname']}")
            
            command = self.analysis.run(data=data)
            if not command is None:
                self.produce(command)
            
    def produce(self, command):
        print(f"[ANALYSIS]\nSending command to topic {self.produce_topic}. Target Agent: {command['hostname']}")
        self.producer.produce(self.produce_topic, value=json.dumps(command).encode('utf-8'), key=command['hostname'])
        self.producer.poll(0)
    
    def finalize(self):
        self.producer.flush()
        self.consumer.close()
    
    
    
    