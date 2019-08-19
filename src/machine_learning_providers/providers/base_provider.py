
# use a singleton pattern for the registry
# need to use singleton so as not to rely on global variables for concurrency
import logging

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
        logging_enabled =  kwargs.get("logging_enabled")
        if logging_enabled == True:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = None
    # TODO needs to be implemented properly when application logger is sorted
    def __log_msg(self, *messages, level="NOTSET", delimeter= " "):
        levels = {
            "CRITICAL": logging.CRITICAL,
            "ERROR": logging.ERROR,
            "WARNING": logging.WARNING,
            "INFO": logging.INFO,
            "DEBUG": logging.DEBUG,
            "NOTSET": logging.NOTSET
        }
        msg = delimeter.join(messages)
        if self.logger is not None:
            if level not in levels:
                raise ValueError(
                    f"level {level} is not valid must be one of {list(levels.keys())}"
                )
            self.logger.log(
                levels[level],
                msg
            )
        else:
            if level is not None:
                print(f"LOGGED MESSAGE: {msg}")
            else:
                print(f"{level}: {msg}")
        

    
        