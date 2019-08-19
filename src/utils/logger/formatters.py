
from logging import Formatter
class SlackFormatter(Formatter):
    def __init__(self, fmt = None, datefmt=None, style="%"):
        if fmt is None and style == "%":
            fmt = (
                "LEVEL: %(levelname)s\n" +
                "TIME: %(asctime)s\n" +
                "FILENAMEL %(filename)s\n" +
                "MODULE: %(module)s\n" +
                "MESSAGES: %(message)s\n"
            )
        super().__init__(
            fmt=fmt, datefmt=datefmt, style=style
        )