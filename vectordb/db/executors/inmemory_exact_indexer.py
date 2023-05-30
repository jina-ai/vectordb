from typing import Optional

from docarray.index import InMemoryExactNNIndex
from jina.serve.executors.decorators import requests, write

from vectordb.db.executors.typed_executor import TypedExecutor


class InMemoryExactNNIndexer(TypedExecutor):

    def __init__(self, index_file_path: Optional[str] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._index_file_path = f'{self.workspace}/index.bin'
        self._index = InMemoryExactNNIndex[self._schema](index_file_path=index_file_path)

    @write
    @requests(on='/index')
    def index(self, docs, *args, **kwargs):
        self.logger.debug(f'Index')
        self._index.index(docs)

    @requests(on='/search')
    def search(self, docs, *args, **kwargs):
        self.logger.debug(f'Search')
        return self._index.find_batched(docs)[0]

    @write
    @requests(on='/update')
    def update(self, docs, *args, **kwargs):
        self.logger.debug(f'Update')
        self.delete(docs)
        self.index(docs)

    @write
    @requests(on='/delete')
    def delete(self, docs, *args, **kwargs):
        self.logger.debug(f'Delete')
        del self._index[[doc.id for doc in docs]]

    def num_docs(self, *args, **kwargs):
        return {'num_docs': self._index.num_docs()}

    def close(self):
        self._index.persist(self._index_file_path)
