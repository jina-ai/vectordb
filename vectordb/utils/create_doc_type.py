from typing import Type, List, TYPE_CHECKING

if TYPE_CHECKING:
    from docarray import BaseDoc


def create_output_doc_type(input_doc_type: Type['BaseDoc']):
    """
    Given a Document type, dynamically generate a new `BaseDoc` that will include nested matches of input doc type as matches and a list of floats as scores of those matches
    :param input_doc_type: The document type
    :return: The created output type
    """
    from docarray import BaseDoc, DocList
    from pydantic import create_model
    return create_model(
        input_doc_type.__name__ + 'WithMatchesAndScores',
        __base__=input_doc_type,
        # NOTE: With pydantic>=2, __validators__ does not exist
        __validators__=getattr(input_doc_type, "__validators__", None),
        matches=(DocList[input_doc_type], []),
        scores=(List[float], [])
    )
