from jina import Executor


from docarray import BaseDoc
from typing import TypeVar, Generic, Type, Optional

TSchema = TypeVar('TSchema', bound=BaseDoc)


class TypedExecutor(Executor, Generic[TSchema]):
    # the BaseDoc that defines the schema of the store
    # for subclasses this is filled automatically
    _schema: Optional[Type[BaseDoc]] = None

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
