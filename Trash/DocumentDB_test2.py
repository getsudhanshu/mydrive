import uuid
import datetime

# A simple in-memory dictionary to simulate a document database
database = {}

def create_new_version(filename, content, version_number=1):
    """
    Creates a new document with a unique ID for each version.
    """
    doc_id = str(uuid.uuid4())
    doc = {
        '_id': doc_id,
        'filename': filename,
        'content': content,
        'version': version_number,
        'created_at': datetime.datetime.now().isoformat()
    }
    database[doc_id] = doc
    print(f"Created new version of '{filename}' with ID: {doc_id}")
    return doc

def find_all_versions(filename):
    """
    Finds and returns all documents for a given filename.
    """
    versions = [doc for doc in database.values() if doc['filename'] == filename]
    return sorted(versions, key=lambda x: x['version'])

# --- Example Usage ---

# Upload the first version
create_new_version("my_text.txt", "Hello world", version_number=1)

# Upload the second version
create_new_version("my_text.txt", "Hello world again", version_number=2)

# Upload the third version
create_new_version("my_text.txt", "This is the final version", version_number=3)

# Find and display all versions of "my_text.txt"
all_versions = find_all_versions("my_text.txt")

print("\n--- All Versions of 'my_text.txt' ---")
for version in all_versions:
    print(f"ID: {version['_id']} | Version: {version['version']} | Content: '{version['content']}'")