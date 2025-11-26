import time
import queue
import grpc
import socket
import threading
from grpc_stub import monitoring_pb2, monitoring_pb2_grpc
from etcd_agent import EtcdAgent

# send data to grpc server
# receive command from grpc server
class GrpcAgent:
    def __init__(self, grpc_host, grpc_port):
        self.grpc_host = grpc_host
        self.grpc_port = grpc_port
        self.monitor_data_queue = queue.Queue()
        self.command_response_queue = queue.Queue()
        self.thread: threading.Thread = None
        
    def request_iterator_generator(self):
        while True:
            try:
                command_response = self.command_response_queue.get_nowait()
                yield command_response
            except queue.Empty:
                pass
            
            try:
                monitor_data = self.monitor_data_queue.get_nowait()
                yield monitor_data
            except queue.Empty:
                pass
            
            time.sleep(0.1)
        
    def report(self, data):
        self.monitor_data_queue.put(data)
            
    def run_client(self, etcd_agent: EtcdAgent):
        with grpc.insecure_channel(f"{self.grpc_host}:{self.grpc_port}") as channel:
            stub = monitoring_pb2_grpc.MonitorStub(channel)
            try:
                command_response_queue: queue.Queue = queue.Queue()
                monitor_data_queue: queue.Queue = queue.Queue()
                
                command_stream = stub.monitor(self.request_iterator_generator())
                for command in command_stream:
                    
                    # command handler
                    if command.command_type == monitoring_pb2.CommandRequest.CommandType.UNKNOWN:
                        pass # do not send response
                    
                    elif command.command_type == monitoring_pb2.CommandRequest.CommandType.SET_INTERVAL:
                        interval_value = command.parameter
                        output, success = None, True
                        try:
                            etcd_agent.set_interval(interval_value)
                        except Exception as e:
                            success = False
                            output = str(e)
                        command_response_queue.put(
                            monitoring_pb2.CommandResult(hostname=socket.gethostname(), original_command=command, output=output, success=success)
                        )
                    
            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.UNAVAILABLE:
                    print(e.details())
                    print(f"Failed to connect to server at {self.grpc_host}. Is the server running?")
                else:
                    print(f"RPC failed: {e}")
                    print(e.details())
    
    def start_agent(self, etcd_agent):
        self.thread = threading.Thread(target=self.run_client, args=[etcd_agent], daemon=True)
        self.thread.start()
        
    def finalize(self):
        if self.thread:
            self.thread.join(timeout=1)