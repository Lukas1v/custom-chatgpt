import os
import toml
import chromadb
from chromadb.utils import embedding_functions
from typing import Any, Dict, List

with open("src/config.toml", "r") as file:
    config = toml.load(file)

if config["openai"]["api_type"] == "azure":
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=os.getenv("OPENAI_API_KEY"),
        api_base=os.getenv("OPENAI_ENDPOINT"),
        api_type=config["openai"]["api_type"],
        api_version=config["openai"]["api_version"],
        model_name=config["openai"]["embeddings_model"],  # text-embedding-ada-002
    )
else:
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=os.getenv("OPENAI_API_KEY"),
        model_name=config["openai"]["embeddings_model"],  # text-embedding-ada-002
    )


class vectorStore:
    def __init__(self, collection_name: str):
        self.client = chromadb.Client()  # In-memory storage (no persistence)

        # Check if collection already exists, delete and create a new one
        try:
            self.client.delete_collection(name=collection_name)
        except ValueError:
            pass  # Collection might not exist, which is fine

        self.collection = self.client.get_or_create_collection(
            name=collection_name, embedding_function=openai_ef
        )

    def add_document(self, doc_id: str, text: str, metadata: Dict[str, Any] = None) -> None:
        # Ensure metadata is None if it's empty
        metadata = metadata if metadata else None

        self.collection.add(
            ids=[doc_id],
            documents=[text],
            metadatas=[metadata] if metadata else None,  # Pass None if metadata is empty
        )

    def query(self, text: str, top_k: int = 1) -> List[Dict[str, Any]]:
        results = self.collection.query(
            query_texts=[text],  # Should be a list
            n_results=top_k,
        )
        return results

    def count_docs(self):
        return self.collection.count()


if __name__ == "__main__":
    vs = vectorStore("car")
    vs.add_document("1", "this is a laptop")
    vs.add_document("2", "this is a car")
    vs.add_document("3", "the bike is red")

    result = vs.query("automobile is red")
    if result["documents"]:
        print(result["documents"][0][0])  # Print the first document in the results
    else:
        print("No matching documents found.")
