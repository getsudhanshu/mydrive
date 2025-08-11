import grpc
from flask import Flask, render_template_string, request, redirect, url_for

# Import the generated code
import file_service_pb2
import file_service_pb2_grpc

app = Flask(__name__)
CHUNK_SIZE = 1024 * 1024  # 1MB chunk size

@app.route('/')
def index():
    return render_template_string("""
        <!doctype html>
        <title>gRPC File Uploader</title>
        <h1>Upload File to gRPC Server</h1>
        <form method=post enctype=multipart/form-data action="{{ url_for('upload') }}">
          <input type=file name=file>
          <input type=submit value=Upload>
        </form>
    """)

def generate_chunks(file_obj):
    """
    A generator that reads a file and yields Chunk messages.
    This is what makes gRPC streaming so efficient!
    """
    while True:
        chunk_data = file_obj.read(CHUNK_SIZE)
        if not chunk_data:
            break
        yield file_service_pb2.Chunk(content=chunk_data)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if not file:
        return "No file selected!"

    try:
        # Create a channel to the gRPC server
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = file_service_pb2_grpc.FileServiceStub(channel)
            
            # This is the magic! We call the gRPC method with a generator.
            # gRPC will stream the chunks to the server in the background.
            response = stub.UploadFile(generate_chunks(file))
            
            return f"gRPC Server Response: {response.message}"
    except grpc.RpcError as e:
        return f"Error connecting to gRPC server: {e}"

if __name__ == '__main__':
    app.run(port=8080, debug=True)