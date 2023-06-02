import random
import string

from typing import TYPE_CHECKING

from vectordb.db.executors.typed_executor import TypedExecutor
from jina.serve.executors.decorators import requests, write

if TYPE_CHECKING:
    from docarray.index import HnswDocumentIndex
    from docarray import DocList


class HNSWLibIndexer(TypedExecutor):

    def __init__(self, *args, **kwargs):
        from docarray.index import HnswDocumentIndex
        super().__init__(*args, **kwargs)
        workspace = self.workspace.replace('[', '_').replace(']', '_')
        self.work_dir = f'{workspace}' if self.handle_persistence else f'{workspace}/{"".join(random.choice(string.ascii_lowercase) for _ in range(5))}'
        self._index = HnswDocumentIndex[self._input_schema](work_dir=self.work_dir)

    def index(self, docs, *args, **kwargs):
        self.logger.debug(f'Index {len(docs)}')
        self._index.index(docs)
        return docs

    @write
    @requests(on='/index')
    async def async_index(self, docs, *args, **kwargs):
        # Index does not work on a separate thread, this is why we need to call async
        self.logger.debug(f'Async Index')
        return self.index(docs)

    def search(self, docs, parameters, *args, **kwargs):
        from docarray import DocList
        self.logger.debug(f'Search')
        res = DocList[self._output_schema]()
        search_field = 'embedding'
        if parameters is not None and 'search_field' in parameters:
            search_field = parameters.pop('search_field')

        params = parameters or {}

        ret = self._index.find_batched(docs, search_field=search_field, **params)
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

    def _delete(self, docs, *args, **kwargs):
        del self._index[[doc.id for doc in docs]]
        return docs

    @write
    @requests(on='/delete')
    def delete(self, docs, *args, **kwargs):
        self.logger.debug(f'Delete')
        return self._delete(docs, *args, **kwargs)

    @write
    @requests(on='/update')
    def update(self, docs, *args, **kwargs):
        return self.index(docs, *args, **kwargs)

    def num_docs(self, **kwargs):
        return {'num_docs': self._index.num_docs()}

    def snapshot(self, snapshot_dir):
        # TODO: Maybe copy the work_dir to workspace if `handle` is False
        raise NotImplementedError('Act as not implemented')

    def restore(self, snapshot_dir):
        from docarray.index import HnswDocumentIndex
        self._index = HnswDocumentIndex[self._input_schema](work_dir=snapshot_dir, index_name='index')

    def close(self):
        pass
