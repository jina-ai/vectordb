from vectordb.client.client import Client
from vectordb.utils.unify_input_output import unify_input_output
from vectordb.utils.pass_parameters import pass_kwargs_as_params


class Service:

    def __init__(self, ctxt_manager, schema, address, reverse_order=False):
        self.ctxt_manager = ctxt_manager
        self._reverse_order = reverse_order
        self._client = Client[schema](address, reverse_order=reverse_order)

    def __enter__(self):
        self.ctxt_manager.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.ctxt_manager.__exit__(exc_type, exc_val, exc_tb)

    @property
    def reverse_score_order(self):
        return self._reverse_order

    def block(self):
        return self.ctxt_manager.block()

    def client(self):
        return self._client

    @pass_kwargs_as_params
    @unify_input_output
    def index(self, *args, **kwargs):
        return self._client.index(*args, **kwargs)

    @pass_kwargs_as_params
    @unify_input_output
    def search(self, *args, **kwargs):
        return self._client.search(*args, **kwargs)

    @pass_kwargs_as_params
    @unify_input_output
    def delete(self, *args, **kwargs):
        return self._client.delete(*args, **kwargs)

    @pass_kwargs_as_params
    @unify_input_output
    def update(self, *args, **kwargs):
        return self._client.update(*args, **kwargs)

    @pass_kwargs_as_params
    @unify_input_output
    def post(self, *args, **kwargs):
        return self._client.post(*args, **kwargs)
