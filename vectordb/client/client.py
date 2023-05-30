
class Client:

    def __init__(self, ctxt_manager):
        self._client = ctxt_manager.client

    def index(self, *args, **kwargs):
        return self._client.index(*args, **kwargs)

    def search(self, *args, **kwargs):
        # potentially unwrap the return
        return self._client.search(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return self._client.delete(*args, **kwargs)

    def update(self, *args, **kwargs):
        return self._client.update(*args, **kwargs)

    def post(self, *args, **kwargs):
        return self._client.index(*args, **kwargs)
