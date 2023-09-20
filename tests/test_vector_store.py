
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from vector_store import vectorStore
import pytest
import chromadb

# Define test fixtures if needed
@pytest.fixture
def vector_store_instance():
    # Define the collection name
    collection_name = "test_collection"   
    return vectorStore(collection_name)
    

# Write test cases
def test_initialization(vector_store_instance):
    assert isinstance(vector_store_instance, vectorStore)
    assert isinstance(vector_store_instance.client, chromadb.api.segment.SegmentAPI)
    assert vector_store_instance.collection.name == "test_collection"

def test_add_query_document(vector_store_instance):
    # Add a document and check if it's added successfully
    doc_id = "doc_1"
    text = "This is a test document"
    metadata = {"key": "value"}
    vector_store_instance.add_document(doc_id, text, metadata)

    # Query the document to check if it was added correctly
    results = vector_store_instance.query(text)
    assert results["ids"]== [[doc_id]]
    assert results["documents"]== [[text]]


# Run the tests
if __name__ == "__main__":
    pytest.main()
