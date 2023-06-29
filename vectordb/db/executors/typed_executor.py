from jina import Executor
from jina.serve.executors import _FunctionWithSchema
from jina.serve.executors import __dry_run_endpoint__

from typing import TypeVar, Generic, Type, Optional, TYPE_CHECKING
from vectordb.utils.create_doc_type import create_output_doc_type


if TYPE_CHECKING:
    from docarray import BaseDoc, DocList

TSchema = TypeVar('TSchema', bound='BaseDoc')

InputSchema = TypeVar('InputSchema', bound='BaseDoc')
OutputSchema = TypeVar('OutputSchema', bound='BaseDoc')

methods = ['/index', '/update', '/delete', '/search']


class TypedExecutor(Executor, Generic[InputSchema, OutputSchema]):
    # the BaseDoc that defines the schema of the store
    # for subclasses this is filled automatically
    _input_schema: Optional[Type['BaseDoc']] = None
    _output_schema: Optional[Type['BaseDoc']] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from docarray import DocList
        self._num_replicas = getattr(self.runtime_args, 'replicas', 1)
        for k, v in self._requests.items():
            if k != __dry_run_endpoint__:
                if k != '/search':
                    self._requests[k] = _FunctionWithSchema(self._requests[k].fn, DocList[self._input_schema],
                                                            DocList[self._input_schema])
                else:
                    self._requests[k] = _FunctionWithSchema(self._requests[k].fn, DocList[self._input_schema],
                                                            DocList[self._output_schema])

    @property
    def handle_persistence(self):
        return self._num_replicas == 1

    ##################################################
    # Behind-the-scenes magic                        #
    # Subclasses should not need to implement these  #
    ##################################################
    def __class_getitem__(cls, item: Type[InputSchema]):

        from docarray import BaseDoc
        if not isinstance(item, type):
            # do nothing
            # enables use in static contexts with type vars, e.g. as type annotation
            return Generic.__class_getitem__.__func__(cls, item)
        if not issubclass(item, BaseDoc):
            raise ValueError(
                f'{cls.__name__}[item] `item` should be a Document not a {item} '
            )

        input_schema = item
        output_schema = create_output_doc_type(input_schema)

        class ExecutorTyped(cls):  # type: ignore
            _input_schema: Type[InputSchema] = input_schema
            _output_schema: Type[OutputSchema] = output_schema

        ExecutorTyped.__name__ = f'{cls.__name__}[{input_schema.__name__}][{output_schema.__name__}]'
        ExecutorTyped.__qualname__ = f'{cls.__qualname__}[{input_schema.__name__}][{output_schema.__name__}]'

        return ExecutorTyped
