from confluent_kafka import Consumer, KafkaError

conf = { 
    'bootstrap.servers': 'kafka-0:9092,kafka-1:9092,kafka-2:9092',
    'group-id': 'test-group',
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(conf)
consumer.subscribe(['TEST_TOPIC'])
try:
    while True:
        msg = consumer.poll(1.0) # timeout in seconds
        if msg is None:
            continue
        if msg.error():
            print(f"Error: {msg.error()}")
            break
    print(f"Received message: {msg.value().decode('utf-8')} from {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")
except KeyboardInterrupt:
    print("Stopping consumer")
finally:
    consumer.close()