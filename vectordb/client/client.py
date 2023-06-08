from typing import TypeVar, Generic, Type, Optional, TYPE_CHECKING
from vectordb.utils.unify_input_output import unify_input_output
from vectordb.utils.pass_parameters import pass_kwargs_as_params
from vectordb.utils.create_doc_type import create_output_doc_type
from vectordb.utils.sort_matches_by_score import sort_matches_by_scores


if TYPE_CHECKING:
    from docarray import BaseDoc, DocList

TSchema = TypeVar('TSchema', bound='BaseDoc')

REQUESTS_MAP = {'/index': 'index', '/update': 'update', '/delete': 'delete', '/search': 'search'}


class Client(Generic[TSchema]):

    _input_schema: Optional[Type['BaseDoc']] = None
    _output_schema: Optional[Type['BaseDoc']] = None

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

        class ClientTyped(cls):  # type: ignore
            _input_schema: Type[TSchema] = item
            _output_schema: Type[TSchema] = out_item

        ClientTyped.__name__ = f'{cls.__name__}[{item.__name__}]'
        ClientTyped.__qualname__ = f'{cls.__qualname__}[{item.__name__}]'

        return ClientTyped

    def __init__(self, address, reverse_order=False):
        from jina import Client as jClient
        self.reverse_score_order = reverse_order
        self._client = jClient(host=address)

    @unify_input_output
    @pass_kwargs_as_params
    def index(self, *args, **kwargs):
        return self._client.index(*args, **kwargs)

    @sort_matches_by_scores
    @unify_input_output
    @pass_kwargs_as_params
    def search(self, *args, **kwargs):
        from docarray import DocList
        return self._client.search(return_type=DocList[self._output_schema], *args, **kwargs)

    @unify_input_output
    @pass_kwargs_as_params
    def delete(self, *args, **kwargs):
        return self._client.delete(*args, **kwargs)

    @unify_input_output
    @pass_kwargs_as_params
    def update(self, *args, **kwargs):
        return self._client.update(*args, **kwargs)

    @unify_input_output
    @pass_kwargs_as_params
    def post(self, *args, **kwargs):
        return self._client.index(*args, **kwargs)
