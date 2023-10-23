def _ignore_warnings():
    import logging
    import warnings

    logging.captureWarnings(True)
    warnings.filterwarnings(
        "ignore",
        category=DeprecationWarning,
        message="Deprecated call to `pkg_resources.declare_namespace('google')`.",
    )


_ignore_warnings()

__version__ = '0.0.21'

from vectordb.client import Client
from vectordb.db.hnsw_vectordb import HNSWVectorDB
from vectordb.db.inmemory_exact_vectordb import InMemoryExactNNVectorDB
