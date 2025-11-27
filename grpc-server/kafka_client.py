import json
from confluent_kafka import Producer, Consumer, KafkaError


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
        # Subscribe to the consume topic so poll() will return messages
        try:
            self.consumer.subscribe([self.consume_topic])
            print(f"Subscribed consumer to topic: {self.consume_topic}")
        except Exception as e:
            print(f"Failed to subscribe consumer to topic {self.consume_topic}: {e}")
        
    def consume(self):
        print(f"Start consuming command at topic {self.consume_topic}")
        while True:
            msg = self.consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                # Ignore EOF notifications -- continue polling
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                print(f"Error consuming data: {msg.error()}")
                # continue rather than break so consumer keeps running
                continue

            # Safely decode key and value
            try:
                key = msg.key().decode('utf-8') if msg.key() is not None else None
            except Exception:
                key = msg.key()

            try:
                value = msg.value().decode('utf-8') if msg.value() is not None else None
            except Exception:
                value = msg.value()

            print(f"Received command for {key}")
        
    def produce(self, data):
        print(f"Producing data")
        value = {
            "time": data.time,
            "hostname": data.hostname,
            "metric": data.metric,
            "value": data.value
        }
        # Use delivery callback to get confirmation/errors
        try:
            self.producer.produce(
                self.produce_topic,
                value=json.dumps(value).encode('utf-8'),
                key=str(data.hostname),
                callback=self.delivery_report
            )
            # trigger delivery callbacks
            self.producer.poll(0)
        except BufferError as e:
            print(f"Local producer queue is full ({e}); try again")
        except Exception as e:
            print(f"Failed to produce message: {e}")

    def delivery_report(self, err, msg):
        if err is not None:
            print(f"Delivery failed for message {msg.key()}: {err}")
        else:
            print(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")
    
    def finalize(self):
        self.producer.flush()
        self.consumer.close()
    
    
    
    