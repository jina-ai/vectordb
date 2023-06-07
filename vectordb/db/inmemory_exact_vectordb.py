from vectordb.db.base import VectorDB
from vectordb.db.executors.inmemory_exact_indexer import InMemoryExactNNIndexer


class InMemoryExactNNVectorDB(VectorDB):
    _executor_type = InMemoryExactNNIndexer
    reverse_score_order = True
