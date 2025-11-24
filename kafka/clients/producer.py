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