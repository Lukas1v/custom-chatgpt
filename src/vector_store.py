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
                    model_name=config["openai"]["embeddings_model"] #text-embedding-ada-002
                )
else:
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                api_key=os.getenv("OPENAI_API_KEY"),
                model_name=config["openai"]["embeddings_model"] #text-embedding-ada-002
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
            self.collection = self.client.create_collection(collection_name, embedding_function=openai_ef)

    def add_document(self, doc_id: str, text: str, metadata: Dict[str, Any] = None) -> None:
        self.collection.add(
            ids=[doc_id], 
            documents=[text],
            metadatas=metadata, # filter on these
        )

    def query(self, text: str, top_k: int = 1) -> List[Dict[str, Any]]:
        results = self.collection.query(
            query_texts=text, 
            n_results=top_k
            # where={"metadata_field": "is_equal_to_this"}, # optional filter
            )
        return results


if __name__=="__main__":
    vs = vectorStore("car")
    vs.add_document("1","this is a test")
    vs.add_document("2","this is a car")
    print(vs.query("car"))

