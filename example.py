from docarray import DocList, BaseDoc
from docarray.typing import NdArray
from vectordb import InMemoryExactNNVectorDB, HNSWVectorDB
import random
import string
import numpy as np

class MyDoc(BaseDoc):
    text: str
    embedding: NdArray[128]


db = InMemoryExactNNVectorDB[MyDoc](workspace='./workspace')

if __name__ == '__main__':
    docs_to_index = DocList[MyDoc](
        [MyDoc(text="".join(random.choice(string.ascii_lowercase) for _ in range(5)), embedding=np.random.rand(128))
         for _ in range(2000)])
    query = docs_to_index[100:200]
    with HNSWVectorDB[MyDoc].serve(workspace='./workspace', replicas=1, shards=1,
                                            protocol='grpc') as service:
        service.index(inputs=docs_to_index)
        resp = service.search(inputs=query, limit=3)
