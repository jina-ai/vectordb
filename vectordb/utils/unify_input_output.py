import inspect


INPUTS = 'inputs'
DOCS = 'docs'


def unify_input_output(func):
    """Method to ensure the input docs are passed internally as a list, and that the return docs are returned as
    single if needed. It also makes sure that it unifies `docs` and `inputs` usage"""

    func_args = inspect.getfullargspec(func).args

    expected_key = DOCS if DOCS in func_args else INPUTS

    def wrapper(*args, **kwargs):
        from docarray import DocList, BaseDoc
        return_single = False
        present_key = None
        if DOCS in kwargs:
            present_key = DOCS
            docs = kwargs[DOCS]
        elif INPUTS in kwargs:
            present_key = INPUTS
            docs = kwargs[INPUTS]
        else:
            docs = args[1]

        new_args = args
        if isinstance(docs, BaseDoc):
            return_single = True
            docs = DocList.__class_getitem__(docs.__class__)([docs])
            if present_key is None:
                new_args = (args[0], docs)
            else:
                kwargs[expected_key] = docs
        elif present_key is not None and expected_key != present_key:
            kwargs[expected_key] = docs

        ret = func(*new_args, **kwargs)
        if return_single:
            return ret[0]
        else:
            return ret

    return wrapper
