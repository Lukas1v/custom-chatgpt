import chromadb
from chromadb.utils import embedding_functions
from typing import Any, Dict, List

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                api_key="YOUR_API_KEY",
                api_base="YOUR_API_BASE_PATH",
                api_type="azure",
                api_version="YOUR_API_VERSION",
                model_name="text-embedding-ada-002"
            )


class vectorStore:
    def __init__(self, collection_name: str):
        self.client = chromadb.Client()
        #check if collection already exists, delete and create new
        try:
            self.collection = self.client.delete_collection(name=collection_name)
        except ValueError: 
            pass
        finally:
            self.collection = self.client.create_collection(collection_name)

    def add_document(self, doc_id: str, text: str, metadata: Dict[str, Any] = None) -> None:
        self.collection.add(
            ids=[doc_id], # unique for each doc
            documents=[text], # we handle tokenization, embedding, and indexing automatically. You can skip that and add your own embeddings as well
            metadatas=metadata, # filter on these!
        )

    def query(self, text: str, top_k: int = 1) -> List[Dict[str, Any]]:
        results = self.collection.query(
            query_texts=text, 
            n_results=top_k
            # where={"metadata_field": "is_equal_to_this"}, # optional filter
            )
        return results


if __name__=="__main__":
    vs = vectorStore("auto")
    vs.add_document("1","dit is een test")
    vs.add_document("2","dit is een auto")
    print(vs.query("auto"))

