import traceback
from .base_provider import MLProvider
from google.cloud import language #pylint: disable=no-name-in-module
from google.cloud.language import enums #pylint: disable=no-name-in-module
from google.cloud.language import types #pylint: disable=no-name-in-module
from google.api_core.exceptions import GoogleAPICallError, RetryError #pylint: disable=no-name-in-module
class Google(MLProvider):
    def __init__(self, **kwargs):
        """
        Instatiate the Google Natural Language API ML Providor 
        """
        super().__init__(**kwargs)
        if "logger" in kwargs:
            del kwargs["logger"]
        self.__client = language.LanguageServiceClient(
            **kwargs
        )
    def process(self, text):
        """
        Process textual data

        Parameters
        ----------
        text: str
           The textual data to be processed
        
        Returns
        -------
        dict
           The processed data
        """

        document = types.Document( #pylint: disable=no-member
            content = text,
            type = enums.Document.Type.PLAIN_TEXT
        )
        
        try:
            sentiment = self.__client.analyze_sentiment(document=document)
        except GoogleAPICallError as e:
            super().__log_msg(
                "An error occured with the Google Natural Language API Call {}". format(e),
                "Text which was to be processed {}".format(text),
                "Stack trace {}".format(traceback.format_exc()),
                delimeter="\n",
                level="ERROR"
            )
            return e
        except ValueError as e:
            super().__log_msg(
                "Bad arguments provided {}".format(e),
                "Text which was to be processed {}".format(text),
                "Stack trace {}".format(traceback.format_exc()),
                delimeter="\n",
                level="ERROR"
            )
            return e
        except Exception as e:
            super().__log_msg(
                "An unknown error has occured {}".format(e),
                "Text which was to be processed {}".format(text),
                "Stack trace {}".format(traceback.format_exc()),
                delimeter="\n",
                level="ERROR"
            )
            return e
        
        data = {}
        data["text"] = text
        data["language"] = sentiment.language
        data["sentimentScore"] = sentiment.document_sentiment.score
        data["magnitudeScore"] = sentiment.document_sentiment.magnitude
        data["provider"] = "google"
        data["sentences"] = [
            {
            "text": sentence.text.content, 
            "sentimentScore": sentence.sentiment.score,
            "magnitudeScore": sentence.sentiment.magnitude
            } for sentence in sentiment.sentences ]
        
        return data
        
        
