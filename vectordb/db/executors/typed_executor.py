from jina import Executor
from jina.serve.executors import _FunctionWithSchema

from docarray import BaseDoc, DocList
from typing import TypeVar, Generic, Type, Optional, Tuple

InputSchema = TypeVar('InputSchema', bound=BaseDoc)
OutputSchema = TypeVar('OutputSchema', bound=BaseDoc)

methods = ['/index', '/update', '/delete', '/search']


class TypedExecutor(Executor, Generic[InputSchema, OutputSchema]):
    # the BaseDoc that defines the schema of the store
    # for subclasses this is filled automatically
    _input_schema: Optional[Type[BaseDoc]] = None
    _output_schema: Optional[Type[BaseDoc]] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._num_replicas = getattr(self.runtime_args, 'replicas')
        for k, v in self._requests.items():
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
    def __class_getitem__(cls, item: Tuple[Type[InputSchema], Type[OutputSchema]]):
        input_schema, output_schema = item
        if not issubclass(input_schema, BaseDoc):
            raise ValueError(
                f'{cls.__name__}[item, ...] `item` should be a Document not a {input_schema} '
            )
        if not issubclass(output_schema, BaseDoc):
            raise ValueError(
                f'{cls.__name__}[..., item] `item` should be a Document not a {output_schema} '
            )

        class ExecutorTyped(cls):  # type: ignore
            _input_schema: Type[InputSchema] = input_schema
            _output_schema: Type[OutputSchema] = output_schema

        ExecutorTyped.__name__ = f'{cls.__name__}[{input_schema.__name__}][{output_schema.__name__}]'
        ExecutorTyped.__qualname__ = f'{cls.__qualname__}[{input_schema.__name__}][{output_schema.__name__}]'

        return ExecutorTyped
