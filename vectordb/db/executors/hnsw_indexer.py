from vectordb.db.executors.typed_executor import TypedExecutor
from jina import requests
from jina.serve.executors.decorators import write
from docarray.index import HnswDocumentIndex


class HNSWLibIndexer(TypedExecutor):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._index = HnswDocumentIndex[self._schema]()
        self.logger.debug(f'self._index {self._index} and {self.requests}')

    @write
    @requests(on='/index')
    def index(self, docs, parameters, **kwargs):
        pass

    @write
    @requests(on='/update')
    def update(self, docs, parameters, **kwargs):
        pass

    @write
    @requests(on='/delete')
    def delete(self, docs, parameters, **kwargs):
        pass

    @requests(on='/delete')
    def search(self, docs, parameters, **kwargs):
        pass
