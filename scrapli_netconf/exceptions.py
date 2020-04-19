"""scrapli_netconf.exceptions"""
from scrapli.exceptions import ScrapliException


class CouldNotExchangeCapabilities(ScrapliException):
    """Exception for failure of capabilities exchange"""
