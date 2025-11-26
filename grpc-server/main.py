import sys
import traceback
from grpc_server import GrpcServer

# -------------------------------------- CONFIGURATION --------------------------------------
REQUIRED_ARGS_COUNT = 1

if len(sys.argv) != REQUIRED_ARGS_COUNT + 1:
    print(f"Incorrect argument. Usage: {sys.argv[0]} <GRPC_MAX_WORKERS>")
    
GRPC_MAX_WORKERS = int(sys.argv[1])

def main():
    try:
        grpc_server = GrpcServer(GRPC_MAX_WORKERS)
        grpc_server.startServer()
        
    except Exception as e:
        print(f"Exception occured: {e}")
        print(traceback.format_exc())
    finally:
        grpc_server.finalize()

if __name__ == "__main__":
    main()