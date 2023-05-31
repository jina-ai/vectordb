import pytest
import random
import string
from docarray import DocList, BaseDoc
from docarray.typing import NdArray
from vectordb import InMemoryExactNNVectorDB
import numpy as np


class MyDoc(BaseDoc):
    text: str
    embedding: NdArray[128]


@pytest.fixture()
def docs_to_index():
    return DocList[MyDoc](
        [MyDoc(text="".join(random.choice(string.ascii_lowercase) for _ in range(5)), embedding=np.random.rand(128))
         for _ in range(2000)])


@pytest.mark.parametrize('call_method', ['docs', 'inputs', 'positional'])
def test_inmemory_vectordb_batch(docs_to_index, call_method):
    query = docs_to_index[:100]
    indexer = InMemoryExactNNVectorDB[MyDoc]()
    if call_method == 'docs':
        indexer.index(docs=docs_to_index)
        resp = indexer.search(docs=query)
    elif call_method == 'inputs':
        indexer.index(inputs=docs_to_index)
        resp = indexer.search(inputs=query)
    elif call_method == 'positional':
        indexer.index(docs_to_index)
        resp = indexer.search(query)
    assert len(resp) == len(query)
    for res in resp:
        assert len(res.matches) == 10
        assert res.id == res.matches[0].id
        assert res.text == res.matches[0].text
        assert res.scores[0] > 0.99 # some precision issues, should be 1


@pytest.mark.parametrize('call_method', ['docs', 'inputs', 'positional'])
def test_inmemory_vectordb_single_query(docs_to_index, call_method):
    query = docs_to_index[100]
    indexer = InMemoryExactNNVectorDB[MyDoc]()
    if call_method == 'docs':
        indexer.index(docs=docs_to_index)
        resp = indexer.search(docs=query)
    elif call_method == 'inputs':
        indexer.index(inputs=docs_to_index)
        resp = indexer.search(inputs=query)
    elif call_method == 'positional':
        indexer.index(docs_to_index)
        resp = indexer.search(query)
    assert len(resp.matches) == 10
    assert resp.id == resp.matches[0].id
    assert resp.text == resp.matches[0].text
    assert resp.scores[0] > 0.99 # some precision issues, should be 1
