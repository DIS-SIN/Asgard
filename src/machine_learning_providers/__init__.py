from .providers import MLRegistry

def process_text(text, providers, logging_enabled=False):
    """
    Process text using one or more providors registered with MLRegistry

    Parameters
    ----------
    text: str
        The text to be processed
    providers: list
        A list of one or more providers as lower case strings
    logger: Logger object, optional
        An optional Logger object used to log messages
    
    Returns
    ---------
    list
       A list of dicts containing the results of the processed text
    """
    registry = MLRegistry()
    if not registry.validate_providers(providers):
        raise ValueError(
            "One or more providers are not valid {}".format(providers)
        )
    data = []
    for provider in providers:
        current_provider = registry.get_class(provider)(logging_enabled=logging_enabled)
        processed_text = current_provider.process(text)
        if processed_text is not None and not isinstance(processed_text, Exception):
            data.append(processed_text)
    return data

