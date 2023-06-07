from typing import TypeVar, Generic, Type, Optional, Union, List, Dict, TYPE_CHECKING
from vectordb.db.executors.typed_executor import TypedExecutor
from vectordb.db.service import Service
from vectordb.utils.create_doc_type import create_output_doc_type
from vectordb.utils.unify_input_output import unify_input_output
from vectordb.utils.pass_parameters import pass_kwargs_as_params
from vectordb.utils.sort_matches_by_score import sort_matches_by_scores

if TYPE_CHECKING:
    from jina import Deployment, Flow
    from docarray import BaseDoc, DocList

TSchema = TypeVar('TSchema', bound='BaseDoc')

REQUESTS_MAP = {'/index': 'index', '/update': 'update', '/delete': 'delete', '/search': 'search'}


class VectorDB(Generic[TSchema]):
    # the BaseDoc that defines the schema of the store
    # for subclasses this is filled automatically
    _input_schema: Optional[Type['BaseDoc']] = None
    _output_schema: Optional[Type['BaseDoc']] = None
    _executor_type: Optional[Type[TypedExecutor]] = None
    _executor_cls: Type[TypedExecutor]

    ##################################################
    # Behind-the-scenes magic                        #
    # Subclasses should not need to implement these  #
    ##################################################
    def __class_getitem__(cls, item: Type[TSchema]):
        from docarray import BaseDoc
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
        if 'work_dir' in kwargs:
            self._workspace = kwargs['work_dir']
        if 'workspace' in kwargs:
            self._workspace = kwargs['workspace']
        self._uses_with = kwargs
        kwargs['requests'] = REQUESTS_MAP
        kwargs['runtime_args'] = {'workspace': self._workspace}
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
        from jina import Deployment, Flow
        protocol = protocol or 'grpc'
        protocol_list = [p.lower() for p in protocol] if isinstance(protocol, list) else [protocol.lower()]
        stateful = replicas is not None and replicas > 1
        executor_cls_name = ''.join(cls._executor_cls.__name__.split('[')[0:2])
        ServedExecutor = type(f'{executor_cls_name.replace("[", "").replace("]", "")}', (cls._executor_cls,),
                              {})
        polling = {'/index': 'ANY', '/search': 'ALL', '/update': 'ALL', '/delete': 'ALL'}
        if 1 < replicas < 3:
            raise Exception(f'In order for consensus to properly work, at least 3 replicas need to be provided.')

        if peer_ports is None and stateful is True:
            peer_ports = {}
            if shards is not None:
                for shard in range(shards):
                    peer_ports[str(shard)] = []
                    for replica in range(replicas):
                        peer_ports[str(shard)].append(8081 + shard * replicas + replica + 1)
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

        use_deployment = True

        if 'websocket' in protocol_list:  # websocket not supported for Deployment
            use_deployment = False

        if (shards > 1 or stateful) and 'http' in protocol_list:  # http not supported for shards > 1 or stateful
            use_deployment = False

        if use_deployment:
            ctxt_manager = Deployment(uses=ServedExecutor,
                                      port=port,
                                      protocol=protocol,
                                      shards=shards,
                                      replicas=replicas,
                                      stateful=stateful,
                                      peer_ports=peer_ports,
                                      workspace=workspace,
                                      polling=polling,
                                      **kwargs)
        else:
            ctxt_manager = Flow(port=port, protocol=protocol, **kwargs).add(uses=ServedExecutor,
                                                                            shards=shards,
                                                                            replicas=replicas,
                                                                            stateful=stateful,
                                                                            peer_ports=peer_ports,
                                                                            polling=polling,
                                                                            workspace=workspace)

        return Service(ctxt_manager, address=f'{protocol_list[0]}://0.0.0.0:{port}', schema=cls._input_schema, reverse_order=cls.reverse_score_order)

    @pass_kwargs_as_params
    @unify_input_output
    def index(self, docs: 'DocList[TSchema]', parameters: Optional[Dict] = None, **kwargs):
        return self._executor.index(docs, parameters)

    @pass_kwargs_as_params
    @unify_input_output
    def update(self, docs: 'DocList[TSchema]', parameters: Optional[Dict] = None, **kwargs):
        return self._executor.update(docs, parameters)

    @pass_kwargs_as_params
    @unify_input_output
    def delete(self, docs: 'DocList[TSchema]', parameters: Optional[Dict] = None, **kwargs):
        return self._executor.delete(docs, parameters)

    @sort_matches_by_scores
    @pass_kwargs_as_params
    @unify_input_output
    def search(self, docs: 'DocList[TSchema]', parameters: Optional[Dict] = None, **kwargs):
        return self._executor.search(docs, parameters)

    def persist(self):
        return self._executor.close()
