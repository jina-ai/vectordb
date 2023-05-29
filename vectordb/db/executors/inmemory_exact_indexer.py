from vectordb.db.executors.typed_executor import TypedExecutor
from jina import requests
from jina.serve.executors.decorators import write
from docarray.index import InMemoryExactNNIndex


class InMemoryExactNNIndexer(TypedExecutor):

    def __init__(self, *args, **kwargs):
        print(f' InMemoryExactNNIndexer with {self._schema} and {kwargs}')
        super().__init__(*args, **kwargs)
        self.logger.debug(f' InMemoryExactNNIndexer with {self._schema}')
        self._index = InMemoryExactNNIndex[self._schema](**kwargs)
        self.logger.debug(f'self._index {self._index}')

    #@write
    @requests(on='/index')
    def index(self, docs, parameters, **kwargs):
        pass

    #@write
    @requests(on='/update')
    def update(self, docs, parameters, **kwargs):
        pass

    #@write
    @requests(on='/delete')
    def delete(self, docs, parameters, **kwargs):
        pass

    @requests(on='/delete')
    def search(self, docs, parameters, **kwargs):
        pass
