from vectordb.utils.unify_input_output import unify_input_output
from vectordb.utils.pass_parameters import pass_kwargs_as_params


class Client:

    def __init__(self, ctxt_manager):
        self._client = ctxt_manager.client

    @unify_input_output
    @pass_kwargs_as_params
    def index(self, *args, **kwargs):
        return self._client.index(*args, **kwargs)

    @unify_input_output
    @pass_kwargs_as_params
    def search(self, *args, **kwargs):
        # potentially unwrap the return
        return self._client.search(*args, **kwargs)

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
