
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
        def validate_providers(self, providers):
            for provider in providers:
                if provider not in self.registry:
                    return False
            return True
    instance = None
    def __init__(self):
        if not MLRegistry.instance:
            MLRegistry.instance = MLRegistry.__MLRegistry()
    def __getattr__(self, name):
        return getattr(self.instance, name)

# Meta Class used to register providors
class MLProviderMeta(type):
    def __new__(meta, name, bases, class_dict):
        cls = type.__new__(meta, name, bases, class_dict)
        registry = MLRegistry()
        registry.register_class(cls)
        return cls

# TODO: abstract class for interface to ensure consistency of methods
class MLProvider(object, metaclass=MLProviderMeta):
    def __init__(self, **kwargs):
        self.logger =  kwargs.get("logger")
    # TODO needs to be implemented properly when application logger is sorted
    def __log_msg(self, *messages, level = None, delimeter= " ", ):
        msg = delimeter.join(messages)
        if self.logger is not None: 
            pass
        else:
            if level is not None:
                print(f"LOGGED MESSAGE: {msg}")
            else:
                print(f"{level}: {msg}")
        

    
        