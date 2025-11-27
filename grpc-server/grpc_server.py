import grpc
import threading
import queue
from grpc_stub import monitoring_pb2, monitoring_pb2_grpc
from concurrent import futures
from kafka_client import KafkaClient

class MonitorService(monitoring_pb2_grpc.MonitorServicer):

    def __init__(self, kafka_client: KafkaClient, command_queue: queue.Queue):
        self.kafka_client = kafka_client
        self.command_queue = command_queue
    
    def monitor(self, request_iterator, context):
        for request in request_iterator:
            if request.HasField('monitor_data'):
                # print(f"Time: {request.monitor_data.time}")
                # print(f"Hostname: {request.monitor_data.hostname}")
                # print(f"Metric: {request.monitor_data.metric}")
                # print(f"Value: {request.monitor_data.value}")
                
                self.kafka_client.produce(request.monitor_data)
                
                # Analyze monitoring data
                command_request = None
                command_type = monitoring_pb2.CommandRequest.CommandType.UNKNOWN
                parameter = ""
                
                try:
                    command_request = self.command_queue.get_nowait()
                except:
                    pass
                
                # send command
                if command_request:
                    print("\n=== SENDING COMMAND REQUEST ===")
                    print(command_request)
                    # print(f"Target host: {request.monitor_data.hostname}")
                    # print(f"Command type: {command_type}")
                    # print(f"Parameter: {parameter}")
                    # yield command_request
                
                
class GrpcServer():
    def __init__(self, max_workers, kafka_client: KafkaClient, command_queue: queue.Queue):
        self.max_workers = max_workers
        self.kafka_client = kafka_client
        self.server_t: threading.Thread = None
        self.kafka_t: threading.Thread = None
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=self.max_workers))
        monitoring_pb2_grpc.add_MonitorServicer_to_server(MonitorService(self.kafka_client, command_queue), self.server)
        self.server.add_insecure_port("[::]:50051")
        
    def serve(self):
        self.server.start()
        print("gRPC server running on: 50051")
        self.server.wait_for_termination()
        
    def startServer(self):
        self.kafka_t = threading.Thread(target=self.kafka_client.consume, daemon=True)
        self.kafka_t.start()
        
        self.server_t = threading.Thread(target=self.serve, daemon=True)
        self.server_t.start()
        
    def finalize(self):
        print("Shutting down GRPC server...")
        self.server.stop(5)
        self.server_t.join(timeout=1)

            

    