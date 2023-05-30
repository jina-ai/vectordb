

class Service:

    def __init__(self, ctxt_manager):
        self.ctxt_manager = ctxt_manager

    def __enter__(self):
        return self.ctxt_manager.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.ctxt_manager.__exit__(exc_type, exc_val, exc_tb)

    def block(self):
        return self.ctxt_manager.block()

    def client(self):
        return self.ctxt_manager

    def index(self, *args, **kwargs):
        return self.ctxt_manager.index(*args, **kwargs)

    def search(self, *args, **kwargs):
        return self.ctxt_manager.search(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.ctxt_manager.delete(*args, **kwargs)

    def update(self, *args, **kwargs):
        return self.ctxt_manager.update(*args, **kwargs)

    def post(self, *args, **kwargs):
        return self.ctxt_manager.index(*args, **kwargs)