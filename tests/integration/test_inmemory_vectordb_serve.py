import multiprocessing
import pytest
import random
import string
import time
import numpy as np

from docarray import DocList, BaseDoc
from docarray.typing import NdArray
from vectordb import InMemoryExactNNVectorDB
from jina.helper import random_port


class MyDoc(BaseDoc):
    text: str
    embedding: NdArray[128]


@pytest.fixture()
def docs_to_index():
    return DocList[MyDoc](
        [MyDoc(text="".join(random.choice(string.ascii_lowercase) for _ in range(5)), embedding=np.random.rand(128))
         for _ in range(2000)])


@pytest.mark.timeout(180)
@pytest.mark.parametrize('shards', [1, 2])
@pytest.mark.parametrize('replicas', [1, 3])
@pytest.mark.parametrize('protocol', ['grpc', 'http', 'websocket'])
def test_inmemory_vectordb_batch(docs_to_index, replicas, shards, protocol, tmpdir):
    query = docs_to_index[:10]
    port = random_port()
    with InMemoryExactNNVectorDB[MyDoc].serve(workspace=str(tmpdir), replicas=replicas, shards=shards, port=port,
                                              protocol=protocol, timeout_ready=10000) as db:
        db.index(inputs=docs_to_index)
        if replicas > 1:
            time.sleep(2)
        resp = db.search(inputs=query)
        assert len(resp) == len(query)
        for res in resp:
            assert len(res.matches) == 10 * shards
            assert res.id == res.matches[0].id
            assert res.text == res.matches[0].text
            assert res.scores[0] > 0.99  # some precision issues, should be 1.0


@pytest.mark.timeout(270)
@pytest.mark.parametrize('limit', [1, 10, 2000, 2500])
@pytest.mark.parametrize('shards', [1, 2])
@pytest.mark.parametrize('replicas', [1, 3])
@pytest.mark.parametrize('protocol', ['grpc', 'http', 'websocket'])
def test_inmemory_vectordb_single_query(docs_to_index, limit, replicas, shards, protocol, tmpdir):
    query = docs_to_index[100]
    port = random_port()
    with InMemoryExactNNVectorDB[MyDoc].serve(workspace=str(tmpdir), replicas=replicas, shards=shards, port=port,
                                              protocol=protocol, timeout_ready=10000) as db:
        db.index(inputs=docs_to_index)
        if replicas > 1:
            time.sleep(2)
        resp = db.search(inputs=query, limit=limit)
        assert len(resp.matches) == min(limit * shards, len(docs_to_index))
        assert resp.id == resp.matches[0].id
        assert resp.text == resp.matches[0].text
        assert resp.scores[0] > 0.99  # some precision issues, should be 1.0


@pytest.mark.timeout(180)
@pytest.mark.parametrize('shards', [1, 2])
@pytest.mark.parametrize('replicas', [1, 3])
@pytest.mark.parametrize('protocol', ['grpc', 'http', 'websocket'])
def test_inmemory_vectordb_delete(docs_to_index, replicas, shards, protocol, tmpdir):
    query = docs_to_index[0]
    port = random_port()
    delete = MyDoc(id=query.id, text='', embedding=np.random.rand(128))
    with InMemoryExactNNVectorDB[MyDoc].serve(workspace=str(tmpdir), replicas=replicas, shards=shards, port=port,
                                              protocol=protocol, timeout_ready=10000) as db:
        db.index(inputs=docs_to_index)
        if replicas > 1:
            time.sleep(2)
        resp = db.search(inputs=query)

        assert len(resp.matches) == 10 * shards
        assert resp.id == resp.matches[0].id
        assert resp.text == resp.matches[0].text
        assert resp.scores[0] > 0.99  # some precision issues, should be 0.0

        db.delete(inputs=delete)
        if replicas > 1:
            time.sleep(2)
        resp = db.search(inputs=query)

        assert len(resp.matches) == 10 * shards
        assert resp.id != resp.matches[0].id
        assert resp.text != resp.matches[0].text


@pytest.mark.timeout(180)
@pytest.mark.parametrize('shards', [1, 2])
@pytest.mark.parametrize('replicas', [1, 3])
@pytest.mark.parametrize('protocol', ['grpc', 'http', 'websocket'])
def test_inmemory_vectordb_udpate_text(docs_to_index, replicas, shards, protocol, tmpdir):
    query = docs_to_index[0]
    port = random_port()
    update = MyDoc(id=query.id, text=query.text + '_changed', embedding=query.embedding)
    with InMemoryExactNNVectorDB[MyDoc].serve(workspace=str(tmpdir), replicas=replicas, shards=shards, port=port,
                                              protocol=protocol, timeout_ready=10000) as db:
        db.index(inputs=docs_to_index)
        if replicas > 1:
            time.sleep(2)
        resp = db.search(inputs=query)
        assert len(resp.matches) == 10 * shards
        assert resp.id == resp.matches[0].id
        assert resp.text == resp.matches[0].text
        assert resp.scores[0] > 0.99  # some precision issues, should be 0.0

        db.update(update)
        if replicas > 1:
            time.sleep(2)
        resp = db.search(inputs=query)
        assert len(resp.matches) == 10 * shards
        assert resp.scores[0] > 0.99
        assert resp.id == resp.matches[0].id
        assert resp.matches[0].text == resp.text + '_changed'


@pytest.mark.timeout(180)
@pytest.mark.parametrize('shards', [1, 2])
@pytest.mark.parametrize('replicas', [1, 3])
@pytest.mark.parametrize('protocol', ['grpc', 'http', 'websocket'])
def test_inmemory_vectordb_restore(docs_to_index, replicas, shards, protocol, tmpdir):
    query = docs_to_index[:100]
    port = random_port()

    with InMemoryExactNNVectorDB[MyDoc].serve(workspace=str(tmpdir), replicas=replicas, shards=shards, port=port,
                                              protocol=protocol, timeout_ready=10000) as db:
        db.index(docs=docs_to_index)
        if replicas > 1:
            time.sleep(2)
        resp = db.search(docs=query)
        assert len(resp) == len(query)
        for res in resp:
            assert len(res.matches) == 10 * shards
            assert res.id == res.matches[0].id
            assert res.text == res.matches[0].text
            assert res.scores[0] > 0.99  # some precision issues, should be 1

    with InMemoryExactNNVectorDB[MyDoc].serve(workspace=str(tmpdir), replicas=replicas, shards=shards, port=port,
                                              protocol=protocol, timeout_ready=10000) as new_db:
        time.sleep(2)
        resp = new_db.search(docs=query)
        assert len(resp) == len(query)
        for res in resp:
            assert len(res.matches) == 10 * shards
            assert res.id == res.matches[0].id
            assert res.text == res.matches[0].text
            assert res.scores[0] > 0.99  # some precision issues, should be 1
