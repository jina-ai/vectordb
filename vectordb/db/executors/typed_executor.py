from jina import Executor
from jina.serve.executors import _FunctionWithSchema

from docarray import BaseDoc, DocList
from typing import TypeVar, Generic, Type, Optional

TSchema = TypeVar('TSchema', bound=BaseDoc)

methods = ['/index', '/update', '/delete', '/search']


class TypedExecutor(Executor, Generic[TSchema]):
    # the BaseDoc that defines the schema of the store
    # for subclasses this is filled automatically
    _schema: Optional[Type[BaseDoc]] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for k, v in self._requests.items():
            self._requests[k] = _FunctionWithSchema(self._requests[k].fn, DocList[self._schema], DocList[self._schema])

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

        class ExecutorTyped(cls):  # type: ignore
            _schema: Type[TSchema] = item

        ExecutorTyped.__name__ = f'{cls.__name__}[{item.__name__}]'
        ExecutorTyped.__qualname__ = f'{cls.__qualname__}[{item.__name__}]'

        return ExecutorTyped
