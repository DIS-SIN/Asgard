
# use a singleton pattern for the registry
# need to use singleton so as not to rely on global variables for concurrency
class MLRegistry:
    class __MLRegistry:
        def __init__(self):
            self.registry = {}
        def register_class(self, cls):
            self.registry[cls.__name__.lower()] = cls
        def get_class(self, name):
            return self.registry.get(name.lower())
    instance = None
    def __init__(self):
        if not MLRegistry.instance:
            MLRegistry.instance = MLRegistry.__MLRegistry()
    def __getattr__(self, name):
        return getattr(self.instance, name)

# Meta Class used to register providors
class MLProvidorMeta(type):
    def __new__(meta, name, bases, class_dict):
        cls = type.__new__(meta, name, bases, class_dict)
        registry = MLRegistry()
        registry.register_class(cls)
        return cls

class MLProvidor(object, metaclass=MLProvidorMeta):
    pass
        

    
        