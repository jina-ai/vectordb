from jina import Deployment, Flow
from docarray import BaseDoc, DocList
from typing import TypeVar, Generic, Type, Optional, Union, List, Dict
from vectordb.db.executors.typed_executor import TypedExecutor
from vectordb.db.service import Service
from vectordb.utils.create_doc_type import create_output_doc_type

TSchema = TypeVar('TSchema', bound=BaseDoc)

REQUESTS_MAP = {'/index': 'index', '/update': 'update', '/delete': 'delete', '/search': 'search'}


class VectorDB(Generic[TSchema]):
    # the BaseDoc that defines the schema of the store
    # for subclasses this is filled automatically
    _input_schema: Optional[Type[BaseDoc]] = None
    _output_schema: Optional[Type[BaseDoc]] = None
    _executor_type: Optional[Type[TypedExecutor]] = None
    _executor_cls: Type[TypedExecutor]

    ##################################################
    # Behind-the-scenes magic                        #
    # Subclasses should not need to implement these  #
    ##################################################
    def __class_getitem__(cls, item: Type[TSchema]):
        if not isinstance(item, type):
            # do nothing
            # enables use in static contexts with type vars, e.g. as type annotation
            return Generic.__class_getitem__.__func__(cls, item)
        if not issubclass(item, BaseDoc):
            raise ValueError(
                f'{cls.__name__}[item] `item` should be a Document not a {item} '
            )

        out_item = create_output_doc_type(item)

        class VectorDBTyped(cls):  # type: ignore
            _input_schema: Type[TSchema] = item
            _output_schema: Type[TSchema] = out_item
            _executor_cls: Type[TypedExecutor] = cls._executor_type[item, out_item]

        VectorDBTyped.__name__ = f'{cls.__name__}[{item.__name__}]'
        VectorDBTyped.__qualname__ = f'{cls.__qualname__}[{item.__name__}]'

        return VectorDBTyped

    def __init__(self, *args, **kwargs):
        self._uses_with = kwargs
        kwargs['requests'] = REQUESTS_MAP
        self._executor = self._executor_cls(*args, **kwargs)

    @classmethod
    def serve(cls,
              *,
              port: Optional[Union[str, List[str]]] = 8081,
              workspace: Optional[str] = None,
              protocol: Optional[Union[str, List[str]]] = None,
              shards: Optional[int] = None,
              replicas: Optional[int] = None,
              peer_ports: Optional[Union[Dict[str, List], List]] = None,
              **kwargs):
        protocol = protocol or 'grpc'
        protocol_list = [p.lower() for p in protocol] if isinstance(protocol, list) else [protocol.lower()]
        stateful = replicas is not None and replicas > 1
        executor_cls_name = ''.join(cls._executor_cls.__name__.split('[')[0:2])
        ServedExecutor = type(f'{executor_cls_name.replace("[", "").replace("]", "")}', (cls._executor_cls,),
                              {})
        if 1 < replicas < 3:
            raise Exception(f'In order for consensus to properly work, at least 3 replicas need to be provided.')

        if peer_ports is None and stateful is True:
            peer_ports = {}
            if shards is not None:
                for shard in range(shards):
                    peer_ports[str(shard)] = [8081 + (shard + 1) * (replica + 1) for replica in range(replicas)]
            else:
                peer_ports['0'] = [8081 + (replica + 1) for replica in range(replicas)]

        if stateful is True:
            if shards is not None:
                assert len(peer_ports.keys()) == shards, 'Need to provide `peer_ports` information for each shard'
            for shard in peer_ports.keys():
                assert len(peer_ports[str(
                    shard)]) == replicas, f'For shard {shard}, need to provide ports for each replica ({replicas} replicas), got {len(peer_ports[str(shard)])} instead'

        if 'stateful' in kwargs:
            kwargs.pop('stateful')

        if 'websocket' not in protocol_list and (shards == 1 or 'http' not in protocol_list):
            ctxt_manager = Deployment(uses=ServedExecutor,
                                      port=port,
                                      protocol=protocol,
                                      shards=shards,
                                      replicas=replicas,
                                      stateful=stateful,
                                      peer_ports=peer_ports,
                                      workspace=workspace,
                                      **kwargs)
        else:
            ctxt_manager = Flow(port=port, protocol=protocol, **kwargs).add(uses=ServedExecutor,
                                                                            shards=shards,
                                                                            replicas=replicas,
                                                                            stateful=stateful,
                                                                            peer_ports=peer_ports,
                                                                            workspace=workspace)

        return Service(ctxt_manager)

    def index(self, docs: 'DocList[TSchema]', parameters: Optional[Dict] = None, **kwargs):
        params = parameters or {}
        for k, v in kwargs.items():
            params[k] = v
        return self._executor.index(docs, params)

    def update(self, docs: 'DocList[TSchema]', parameters: Optional[Dict] = None, **kwargs):
        params = parameters or {}
        for k, v in kwargs.items():
            params[k] = v
        return self._executor.update(docs, params)

    def delete(self, docs: 'DocList[TSchema]', parameters: Optional[Dict] = None, **kwargs):
        params = parameters or {}
        for k, v in kwargs.items():
            params[k] = v
        return self._executor.delete(docs, params)

    def search(self, docs: 'DocList[TSchema]', parameters: Optional[Dict] = None, **kwargs):
        params = parameters or {}
        for k, v in kwargs.items():
            params[k] = v
        return self._executor.search(docs, params)
