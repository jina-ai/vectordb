INPUTS = 'inputs'
DOCS = 'docs'
RETURN_TYPE = 'return_type'


def pass_kwargs_as_params(func):
    """Method to ensure that kwargs are passed as parameters to underlying Executor method"""

    def wrapper(*args, **kwargs):
        parameters = None
        if 'parameters' in kwargs:
            parameters = kwargs.pop('parameters')

        params = parameters or {}
        for k, v in kwargs.items():
            if k not in {INPUTS, DOCS, RETURN_TYPE}:
                params[k] = kwargs[k]
        if len(params.keys()) > 0:
            for k in params.keys():
                if k in kwargs:
                    kwargs.pop(k)
            kwargs['parameters'] = params

        return func(*args, **kwargs)

    return wrapper
