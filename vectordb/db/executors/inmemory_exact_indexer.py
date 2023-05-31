from docarray.index import InMemoryExactNNIndex
from docarray import DocList
from jina.serve.executors.decorators import requests, write

from vectordb.db.executors.typed_executor import TypedExecutor


class InMemoryExactNNIndexer(TypedExecutor):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._index_file_path = f'{self.workspace}/index.bin' if self.handle_persistence else None
        self._indexer = InMemoryExactNNIndex[self._input_schema](index_file_path=self._index_file_path)

    def _index(self, docs, *args, **kwargs):
        self._indexer.index(docs)
        return docs

    @write
    @requests(on='/index')
    def index(self, docs, *args, **kwargs):
        self.logger.debug(f'Index {len(docs)}')
        return self._index(docs, *args, **kwargs)

    def _search(self, docs, *args, **kwargs):
        res = DocList[self._output_schema]()
        ret = self._indexer.find_batched(docs, search_field='embedding')
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
    def search(self, docs, *args, **kwargs):
        self.logger.debug(f'Search {len(docs)}')
        return self._search(docs, *args, **kwargs)

    def _delete(self, docs, *args, **kwargs):
        del self._indexer[[doc.id for doc in docs]]
        return docs

    @write
    @requests(on='/delete')
    def delete(self, docs, *args, **kwargs):
        self.logger.debug(f'Delete')
        return self._delete(docs, *args, **kwargs)

    @write
    @requests(on='/update')
    def update(self, docs, *args, **kwargs):
        self._delete(docs)
        return self._index(docs)

    def num_docs(self, *args, **kwargs):
        return {'num_docs': self._index.num_docs()}

    def snapshot(self, snapshot_dir):
        snapshot_file = f'{snapshot_dir}/index.bin'
        self._indexer.persist(snapshot_file)

    def restore(self, snapshot_dir):
        snapshot_file = f'{snapshot_dir}/index.bin'
        self._indexer = InMemoryExactNNIndex[self._input_schema](index_file_path=snapshot_file)

    def close(self):
        if self._index_file_path is not None:
            self._indexer.persist(self._index_file_path)
