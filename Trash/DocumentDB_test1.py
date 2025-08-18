import uuid
import random

# A simple in-memory dictionary to simulate a document database
database = {}

def create_initial_document(filename, content):
    """Creates a new document with a unique _id."""
    doc_id = str(uuid.uuid4())
    doc = {
        '_id': doc_id,
        '_rev': f"1-{str(uuid.uuid4())}", # Simulate a revision ID
        'filename': filename,
        'content': content
    }
    database[doc_id] = doc
    print(f"Created initial document with ID: {doc_id} and REV: {doc['_rev']}")
    return doc

def update_document(doc_id, current_rev, new_content):
    """
    Simulates updating a document.
    Returns True on success, False on conflict.
    """
    if doc_id not in database:
        print(f"Error: Document with ID {doc_id} not found.")
        return False

    current_doc = database[doc_id]
    
    # Scenario 1: Overwrite (no _rev provided or it's incorrect)
    if current_rev is None or current_rev != current_doc['_rev']:
        print("\n--- Scenario 1: Overwriting document (conflict or no rev)")
        print(f"Attempting to update document with ID {doc_id} but provided wrong or no REV.")
        
        # In a real DB, this would be a conflict, but here we'll just overwrite
        current_doc['content'] = new_content
        current_doc['_rev'] = f"{int(current_doc['_rev'].split('-')[0]) + 1}-{str(uuid.uuid4())}"
        
        print(f"Successfully overwrote document. New REV: {current_doc['_rev']}")
        return True

    # Scenario 2: Update with new version
    else:
        print("\n--- Scenario 2: Adding a new version")
        print(f"Attempting to update document with ID {doc_id} with correct REV.")
        
        current_doc['content'] = new_content
        current_doc['_rev'] = f"{int(current_doc['_rev'].split('-')[0]) + 1}-{str(uuid.uuid4())}"
        
        print(f"Successfully updated document. New REV: {current_doc['_rev']}")
        return True

# --- Example Usage ---

# 1. Create a base document
initial_doc = create_initial_document("my_text.txt", "Hello world")

# 2. Demonstrate Scenario 1: Overwriting the document (wrong rev)
update_document(initial_doc['_id'], "wrong-rev-id", "Hello world again - overwriting old content")

# 3. Demonstrate Scenario 2: Adding a new version (correct rev)
latest_doc_rev = database[initial_doc['_id']]['_rev']
update_document(initial_doc['_id'], latest_doc_rev, "This is the newest version")

print("\n--- Final Database State ---")
print(database)