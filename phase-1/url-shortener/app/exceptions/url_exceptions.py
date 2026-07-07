class URLShortenerError(Exception):
    """Base exception for URL Shortener."""

class AliasAlreadyExistsError(URLShortenerError):

    def __init__(self, alias: str):
        self.alias = alias
        super().__init__(f"Custom alias '{alias}' already exists.")


class URLNotFoundError(URLShortenerError):

    def __init__(self, short_code: str):
        self.short_code = short_code
        super().__init__(f"Short URL '{short_code}' not found.")