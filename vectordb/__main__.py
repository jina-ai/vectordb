import click

from vectordb.db.base import VectorDB
from vectordb import __version__


@click.group()
@click.version_option(__version__, '-v', '--version', prog_name='vectordb')
@click.help_option('-h', '--help')
def vectordb():
    pass


@vectordb.command(help='Deploy a vectorDB app to Jina AI Cloud')
@click.option(
    '--db',
    '--app',
    type=str,
    required=True,
    help='VectorDB to deploy, in the format "<module>:<attribute>"',
)
@click.option(
    '--protocol',
    '--protocols',
    type=str,
    default='grpc',
    help='Protocol to use to communicate with the VectorDB. It can be a single one or a list of multiple protocols to use. Options are grpc, http and websocket',
    required=False,
    show_default=True,
)
@click.option(
    '--shards',
    '-s',
    type=int,
    default=1,
    help='Number of shards to use for the deployed VectorDB',
    required=False,
    show_default=True,
)
def deploy(db, protocol, shards):
    definition_file, _, obj_name = db.partition(":")
    if not definition_file.endswith('.py'):
        definition_file = f'{definition_file}.py'
    protocol = protocol.split(',')
    VectorDB.deploy(protocol=protocol,
                    shards=shards,
                    definition_file=definition_file,
                    obj_name=obj_name)


@vectordb.command(help='Deploy a vectorDB app to Jina AI Cloud')
@click.option(
    '--db',
    '--app',
    type=str,
    required=True,
    help='VectorDB to serve, in the format "<module>:<attribute>"',
)
@click.option(
    '--port',
    '-p',
    type=str,
    default='8081',
    help='Port to use to access the VectorDB. It can be a single one or a list corresponding to the protocols',
    required=False,
    show_default=True,
)
@click.option(
    '--protocol',
    '--protocols',
    type=str,
    default='grpc',
    help='Protocol to use to communicate with the VectorDB. It can be a single one or a list of multiple protocols to use. Options are grpc, http and websocket',
    required=False,
    show_default=True,
)
@click.option(
    '--replicas',
    '-r',
    type=int,
    default=1,
    help='Number of replicas to use for the serving VectorDB',
    required=False,
    show_default=True,
)
@click.option(
    '--shards',
    '-s',
    type=int,
    default=1,
    help='Number of shards to use for the served VectorDB',
    required=False,
    show_default=True,
)
@click.option(
    '--workspace',
    '-w',
    type=str,
    default='.',
    help='Workspace for the VectorDB to persist its data',
    required=False,
    show_default=True,
)
def serve(db, port, protocol, replicas, shards, workspace):
    import importlib
    definition_file, _, obj_name = db.partition(":")
    port = port.split(',')
    if len(port) == 1:
        port = int(port[0])
    else:
        port = [int(p) for p in port]
    protocol = protocol.split(',')
    if definition_file.endswith('.py'):
        definition_file = definition_file[:-3]
    module = importlib.import_module(definition_file)
    db = getattr(module, obj_name)
    service = db.serve(protocol=protocol,
                       port=port,
                       shards=shards,
                       replicas=replicas,
                       workspace=workspace)
    with service:
        service.block()


if __name__ == '__main__':
    vectordb()
