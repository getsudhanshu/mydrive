import grpc
import time
from concurrent import futures

# Import the generated code
import file_service_pb2
import file_service_pb2_grpc

CHUNK_SIZE = 1024 * 1024  # 1MB chunk size

class FileServiceServicer(file_service_pb2_grpc.FileServiceServicer):
    def UploadFile(self, request_iterator, context):
        """
        This function receives a stream of Chunk messages from the client.
        """
        print("Receiving file chunks...")
        start_time = time.time()
        file_data = b""
        
        # request_iterator is a generator that yields Chunk messages
        for chunk in request_iterator:
            file_data += chunk.content
            
        with open("received_file.bin", "wb") as f:
            f.write(file_data)
        
        end_time = time.time()
        print(f"File received and saved. Total time: {end_time - start_time:.2f} seconds.")
        
        # Send a single response back to the client
        return file_service_pb2.UploadStatus(message="File upload successful!")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    file_service_pb2_grpc.add_FileServiceServicer_to_server(FileServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("gRPC Server started on port 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()