from docarray import DocList, BaseDoc
from docarray.documents import TextDoc
from docarray.typing import NdArray
from vectordb import HNSWVectorDB
from vectordb import InMemoryExactNNVectorDB
import numpy as np


class MyDoc(BaseDoc):
    text: str
    embedding: NdArray[128]

docs = [MyDoc(text='hey', embedding=np.random.rand(128)) for i in range(200)]
indexer = InMemoryExactNNVectorDB[MyDoc]()
indexer.index(docs=DocList[MyDoc](docs))
resp = indexer.search(docs=DocList[MyDoc](docs[0:3]))
print(f' resp {resp}')
for query in resp:
    print(f' query matches {query.matches}')
    print(f' query matches scores {query.scores}')

service = InMemoryExactNNVectorDB[MyDoc].serve()
with service:
    service.index(inputs=DocList[MyDoc](docs))
    resp = service.search(inputs=DocList[MyDoc](docs[0:3]))
    print(f' resp {resp}')
    for query in resp:
        print(f' query matches {query.matches}')
        print(f' query matches scores {query.scores}')

# indexer = HNSWVectorDB[MyDoc]()
indexer.index(docs=DocList[MyDoc](docs))
resp = indexer.search(docs=DocList[MyDoc](docs[0:3]))
print(f' resp {resp}')
for query in resp:
    print(f' query matches {query.matches}')
    print(f' query matches scores {query.scores}')

service = HNSWVectorDB[MyDoc].serve()
with service:
    service.index(inputs=DocList[MyDoc](docs))
    resp = service.search(inputs=DocList[MyDoc](docs[0:3]))
    print(f' resp {resp}')
    for query in resp:
        print(f' query matches {query.matches}')
        print(f' query matches scores {query.scores}')


from vectordb.utils.create_doc_type import create_output_doc_type

o = create_output_doc_type(MyDoc)
print(f' {o}')
