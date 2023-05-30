from docarray.index import HnswDocumentIndex
from docarray import DocList
from jina.serve.executors.decorators import requests, write

from vectordb.db.executors.typed_executor import TypedExecutor


class HNSWLibIndexer(TypedExecutor):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        db_config = HnswDocumentIndex.DBConfig
        db_config.work_dir = self.workspace
        db_config.index_name = 'index'
        self._index = HnswDocumentIndex[self._input_schema](work_dir=self.workspace, index_name='index')

    def index(self, docs, *args, **kwargs):
        self.logger.debug(f'Index')
        self._index.index(docs)

    @write
    @requests(on='/index')
    async def async_index(self, docs, *args, **kwargs):
        # Index does not work on a separate thread, this is why we need to call async
        self.logger.debug(f'Async Index')
        self.index(docs)

    def search(self, docs, *args, **kwargs):
        self.logger.debug(f'Search')
        res = DocList[self._output_schema]()
        ret = self._index.find_batched(docs, search_field='embedding')
        matched_documents = ret.documents
        matched_scores = ret.scores
        assert len(docs) == len(matched_documents) == len(matched_scores)

        for query, matches, scores in zip(docs, matched_documents, matched_scores):
            output_doc = self._output_schema(**query.dict())
            output_doc.matches = matches
            output_doc.scores = scores.tolist()
            res.append(output_doc)
        return res

    @requests(on='/search')
    async def async_search(self, docs, *args, **kwargs):
        return self.search(docs, *args, **kwargs)

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

    def snapshot(self, snapshot_dir):
        snapshot_file = f'{snapshot_dir}/index.bin'
        self._index.persist(snapshot_file)

    def restore(self, snapshot_dir):
        self._index = HnswDocumentIndex[self._input_schema](work_dir=snapshot_dir, index_name='index')

    def close(self):
        if self._index_file_path is not None:
            self._index.persist(self._index_file_path)
