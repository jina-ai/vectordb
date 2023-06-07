from vectordb.db.base import VectorDB
from vectordb.db.executors.hnsw_indexer import HNSWLibIndexer


class HNSWVectorDB(VectorDB):
    _executor_type = HNSWLibIndexer
    reverse_score_order = False
