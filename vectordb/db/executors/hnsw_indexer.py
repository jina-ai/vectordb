from docarray.index import HnswDocumentIndex
from jina.serve.executors.decorators import requests, write

from vectordb.db.executors.typed_executor import TypedExecutor


class HNSWLibIndexer(TypedExecutor):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        db_config = HnswDocumentIndex.DBConfig
        db_config.work_dir = self.workspace
        db_config.index_name = 'index'
        self._index = HnswDocumentIndex[self._schema](work_dir=self.workspace, index_name='index')

    def index(self, docs, *args, **kwargs):
        self._index.index(docs)

    @write
    @requests(on='/index')
    async def async_index(self, docs, *args, **kwargs):
        # Index does not work on a separate thread, this is why we need to call async
        self.logger.debug(f'Index')
        self.index(docs)

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

    def num_docs(self, **kwargs):
        return {'num_docs': self._index.num_docs()}
