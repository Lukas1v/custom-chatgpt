
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from vector_store import vectorStore
import pytest
import chromadb

# Define test fixtures if needed
@pytest.fixture
def vector_store_instance():
    # Create an instance of the vectorStore class for testing
    return vectorStore("test_collection")

# Write test cases
def test_initialization(vector_store_instance):
    assert isinstance(vector_store_instance, vectorStore)
    print(vector_store_instance.client) #debug
    assert isinstance(vector_store_instance.client, chromadb.Client)
    # assert vector_store_instance.collection.name == "test_collection"

# def test_add_document(vector_store_instance):
#     # Add a document and check if it's added successfully
#     doc_id = "doc_1"
#     text = "This is a test document"
#     metadata = {"key": "value"}
#     vector_store_instance.add_document(doc_id, text, metadata)

#     # Query the document to check if it was added correctly
#     results = vector_store_instance.query(text)
#     assert len(results) == 1
#     assert results[0]["id"] == doc_id

# def test_query(vector_store_instance):
#     # Add a document
#     doc_id = "doc_2"
#     text = "Another test document"
#     metadata = {"key": "value"}
#     vector_store_instance.add_document(doc_id, text, metadata)

#     # Query for the added document
#     results = vector_store_instance.query(text)
#     assert len(results) == 1
#     assert results[0]["id"] == doc_id

#     # Query for a non-existent document
#     non_existent_text = "Non-existent document"
#     results = vector_store_instance.query(non_existent_text)
#     assert len(results) == 0

# Run the tests
if __name__ == "__main__":
    pytest.main()
