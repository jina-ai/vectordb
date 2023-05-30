from typing import Optional

from docarray.index import InMemoryExactNNIndex
from docarray import DocList
from jina.serve.executors.decorators import requests, write

from vectordb.db.executors.typed_executor import TypedExecutor


class InMemoryExactNNIndexer(TypedExecutor):

    def __init__(self, index_file_path: Optional[str] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._index_file_path = f'{self.workspace}/index.bin'
        self._index = InMemoryExactNNIndex[self._input_schema](index_file_path=index_file_path)

    @write
    @requests(on='/index')
    def index(self, docs, *args, **kwargs):
        self.logger.debug(f'Index {len(docs)}')
        self._index.index(docs)

    @requests(on='/search')
    def search(self, docs, *args, **kwargs):
        self.logger.debug(f'Search {len(docs)}')
        res = DocList[self._output_schema]()
        ret = self._index.find_batched(docs, search_field='embedding')
        matched_documents = ret.documents
        matched_scores = ret.scores
        assert len(docs) == len(matched_documents) == len(matched_scores)
        print(f' matched_scores {matched_scores}')

        for query, matches, scores in zip(docs, matched_documents, matched_scores):
            output_doc = self._output_schema(**query.dict())
            output_doc.matches = matches
            output_doc.scores = scores.tolist()
            res.append(output_doc)
        return res

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
