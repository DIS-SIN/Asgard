from .base_providor import MLProvidor
from google.cloud import language #pylint: disable=no-name-in-module
from google.cloud.language import enums #pylint: disable=no-name-in-module
from google.cloud.language import types #pylint: disable=no-name-in-module
class Google(MLProvidor):
    def __init__(self, **kwargs):
        """
        Instatiate the Google Natural Language API ML Providor 
        """
        self.__client = language.LanguageServiceClient(
            **kwargs
        )