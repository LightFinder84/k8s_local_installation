import grpc
from grpc_stub import monitoring_pb2, monitoring_pb2_grpc
from concurrent import futures

CPU_THRESH_HOLD = 60

class MonitorService(monitoring_pb2_grpc.MonitorServicer):
    def monitor(self, request_iterator, context):
        for request in request_iterator:
            if request.HasField('monitor_data'):
                print("\n=================== RECIEVE MONITOR DATA ==============================")
                print(f"Time: {request.monitor_data.time}")
                print(f"Hostname: {request.monitor_data.hostname}")
                print(f"Metric: {request.monitor_data.metric}")
                print(f"Value: {request.monitor_data.value}")
                
                # Analyze monitoring data
                command_request = None
                command_type = monitoring_pb2.CommandRequest.CommandType.UNKNOWN
                parameter = ""
                
                # CPU
                if request.monitor_data.metric == "cpu" and float(request.monitor_data.value) >= CPU_THRESH_HOLD:
                    command_type = monitoring_pb2.CommandRequest.CommandType.GET_PROCESS_LIST
                    command_request = monitoring_pb2.CommandRequest(command_type=command_type, parameter=parameter)
                    
                
                # send command
                if command_request:
                    print("\n=================== SENDING COMMAND REQUEST ===========================")
                    print(f"Target host: {request.monitor_data.hostname}")
                    print(f"Command type: {command_type}")
                    print(f"Parameter: {parameter}")
                    yield command_request
                
            elif request.HasField('command_result'):
                print("\n=================== RECIEVE COMMAND RESULT ============================")
                print(f"Hostname: {request.command_result.hostname}")
                print(f"Original command type: {request.command_result.original_command.command_type}")
                print(f"Success: {request.command_result.success}")
                print(f"Output:\n{request.command_result.output}")
            
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=3))
    monitoring_pb2_grpc.add_MonitorServicer_to_server(MonitorService(), server)
    server.add_insecure_port("[::]:50051")
    
    server.start()
    print("gRPC server running on: 50051")
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("Shutting down...")
        
if __name__ == "__main__":
    serve()
    