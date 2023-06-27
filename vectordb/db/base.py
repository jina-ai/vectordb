from typing import TypeVar, Generic, Type, Optional, Union, List, Dict, TYPE_CHECKING
from vectordb.db.executors.typed_executor import TypedExecutor
from vectordb.db.service import Service
from vectordb.utils.unify_input_output import unify_input_output
from vectordb.utils.pass_parameters import pass_kwargs_as_params
from vectordb.utils.sort_matches_by_score import sort_matches_by_scores
from vectordb.utils.push_to_hubble import push_vectordb_to_hubble

if TYPE_CHECKING:
    from jina import Deployment, Flow
    from docarray import BaseDoc, DocList

TSchema = TypeVar('TSchema', bound='BaseDoc')

REQUESTS_MAP = {'/index': 'index', '/update': 'update', '/delete': 'delete', '/search': 'search'}


class VectorDB(Generic[TSchema]):
    # the BaseDoc that defines the schema of the store
    # for subclasses this is filled automatically
    _input_schema: Optional[Type['BaseDoc']] = None
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

        class VectorDBTyped(cls):  # type: ignore
            _input_schema: Type[TSchema] = item
            _executor_cls: Type[TypedExecutor] = cls._executor_type[item]

        VectorDBTyped.__name__ = f'{cls.__name__}[{item.__name__}]'
        VectorDBTyped.__qualname__ = f'{cls.__qualname__}[{item.__name__}]'

        return VectorDBTyped

    def __init__(self, *args, **kwargs):
        self._workspace = None
        if 'work_dir' in kwargs:
            self._workspace = kwargs['work_dir']
        if 'workspace' in kwargs:
            self._workspace = kwargs['workspace']
        self._uses_with = kwargs
        kwargs['requests'] = REQUESTS_MAP
        kwargs['runtime_args'] = {'workspace': self._workspace}
        self._executor = self._executor_cls(*args, **kwargs)

    @classmethod
    def _get_jina_object(cls,
                         *,
                         to_deploy: bool = False,
                         port: Optional[Union[str, List[str]]] = 8081,
                         protocol: Optional[Union[str, List[str]]] = None,
                         workspace: Optional[str] = None,
                         shards: Optional[int] = None,
                         replicas: Optional[int] = None,
                         peer_ports: Optional[Union[Dict[str, List], List]] = None,
                         uses_with: Optional[Dict] = None,
                         definition_file: Optional[str] = None,
                         obj_name: Optional[str] = None,
                         **kwargs):
        from jina import Deployment, Flow
        is_instance = False
        uses_with = uses_with or {}
        if isinstance(cls, VectorDB):
            is_instance = True
            uses_with = uses_with.update(**cls._uses_with)

        if is_instance:
            workspace = workspace or cls._workspace
        replicas = replicas or 1
        shards = shards or 1
        protocol = protocol or 'grpc'
        protocol_list = [p.lower() for p in protocol] if isinstance(protocol, list) else [protocol.lower()]
        stateful = replicas is not None and replicas > 1
        if not to_deploy:
            executor_cls_name = ''.join(cls._executor_cls.__name__.split('[')[0:2])
            ServedExecutor = type(f'{executor_cls_name.replace("[", "").replace("]", "")}', (cls._executor_cls,),
                                  {})
            uses = ServedExecutor
        polling = {'/index': 'ANY', '/search': 'ALL', '/update': 'ALL', '/delete': 'ALL'}
        if to_deploy and replicas > 1:
            import warnings
            warnings.warn(
                'Deployment with replicas > 1 is not currently available. The deployment will have 1 replica per each '
                'shard')
            replicas = 1

        if 1 < replicas < 3:
            raise Exception(f'In order for consensus to properly work, at least 3 replicas need to be provided.')

        if peer_ports is None and stateful is True:
            peer_ports = {}
            if shards is not None:
                for shard in range(shards):
                    peer_ports[str(shard)] = []
                    for replica in range(replicas):
                        peer_ports[str(shard)].append(port + shard * replicas + replica + 1)
            else:
                peer_ports['0'] = [port + (replica + 1) for replica in range(replicas)]

        if stateful is True:
            if shards is not None:
                assert len(peer_ports.keys()) == shards, 'Need to provide `peer_ports` information for each shard'
            for shard in peer_ports.keys():
                assert len(peer_ports[str(
                    shard)]) == replicas, f'For shard {shard}, need to provide ports for each replica ({replicas} replicas), got {len(peer_ports[str(shard)])} instead'

        if 'stateful' in kwargs:
            kwargs.pop('stateful')

        use_deployment = True
        if to_deploy:
            # here we would need to push the EXECUTOR TO HUBBLE AND CHANGE THE USES
            assert definition_file is not None, 'Trying to create a Jina Object for Deployment without the file where the vectordb object/class is defined'
            assert obj_name is not None, 'Trying to create a Jina Object for Deployment without the name of the vectordb object/class to deploy'
            uses = f'{push_vectordb_to_hubble(vectordb_name=obj_name, definition_file_path=definition_file)}'
            use_deployment = False

        if 'websocket' in protocol_list:  # websocket not supported for Deployment
            use_deployment = False

        if (shards > 1 or stateful) and 'http' in protocol_list:  # http not supported for shards > 1 or stateful
            use_deployment = False

        if use_deployment:
            jina_object = Deployment(name='indexer',
                                     uses=uses,
                                     uses_with=uses_with,
                                     port=port,
                                     protocol=protocol,
                                     shards=shards,
                                     replicas=replicas,
                                     stateful=stateful,
                                     peer_ports=peer_ports,
                                     workspace=workspace,
                                     polling=polling, **kwargs)
        else:
            jina_object = Flow(port=port, protocol=protocol, **kwargs).add(name='indexer',
                                                                           uses=uses,
                                                                           uses_with=uses_with,
                                                                           shards=shards,
                                                                           replicas=replicas,
                                                                           stateful=stateful,
                                                                           peer_ports=peer_ports,
                                                                           polling=polling,
                                                                           workspace=workspace)

        return jina_object

    @classmethod
    def serve(cls,
              *,
              port: Optional[Union[str, List[str]]] = 8081,
              protocol: Optional[Union[str, List[str]]] = None,
              **kwargs):
        protocol = protocol or 'grpc'
        protocol_list = [p.lower() for p in protocol] if isinstance(protocol, list) else [protocol.lower()]
        ctxt_manager = cls._get_jina_object(to_deploy=False, port=port, protocol=protocol, **kwargs)
        port = port[0] if isinstance(port, list) else port
        return Service(ctxt_manager, address=f'{protocol_list[0]}://0.0.0.0:{port}', schema=cls._input_schema,
                       reverse_order=cls.reverse_score_order)

    @classmethod
    def deploy(cls,
               **kwargs):
        from tempfile import mkdtemp
        import os
        import yaml
        from yaml.loader import SafeLoader
        jina_obj = cls._get_jina_object(to_deploy=True, **kwargs)

        tmpdir = mkdtemp()
        jina_obj.save_config(os.path.join(tmpdir, 'flow.yml'))
        with open(os.path.join(tmpdir, 'flow.yml'), 'r') as f:
            flow_dict = yaml.load(f, SafeLoader)

        executor_jcloud_config = {'resources': {'instance': 'C5', 'autoscale': {'min': 0, 'max': 1},
                                                'storage': {'kind': 'ebs', 'size': '10G', 'retain': True}}}
        for executor in flow_dict['executors']:
            executor['jcloud'] = executor_jcloud_config

        global_jcloud_config = {
            'docarray': '0.34.0',
            'labels': {
                'app': 'vectordb',
            },
            'monitor': {
                'traces': {
                    'enable': True,
                },
                'metrics': {
                    'enable': True,
                    'host': 'http://opentelemetry-collector.monitor.svc.cluster.local',
                    'port': 4317,
                },
            },
        }
        flow_dict['jcloud'] = global_jcloud_config
        import tempfile
        from jcloud.flow import CloudFlow

        with tempfile.TemporaryDirectory() as tmpdir:
            flow_path = os.path.join(tmpdir, 'flow.yml')
            print(f' flow_path {flow_path}')
            with open(flow_path, 'w') as f:
                yaml.safe_dump(flow_dict, f, sort_keys=False)

            cloud_flow = CloudFlow(path=flow_path)

            async def _deploy():
                await cloud_flow.__aenter__()

            import asyncio
            ret = asyncio.run(_deploy())
        return ret

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
