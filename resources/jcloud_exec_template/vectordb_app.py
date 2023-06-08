from docarray import DocList, BaseDoc
from docarray.typing import NdArray
from vectordb import InMemoryExactNNVectorDB


class MyDoc(BaseDoc):
    text: str
    embedding: NdArray[128]


db = InMemoryExactNNVectorDB[MyDoc]
