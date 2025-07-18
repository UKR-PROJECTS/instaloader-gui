from urllib.parse import urlparse


def is_valid_instagram_url(url: str) -> bool:
    """
    Validates if a given URL is a valid Instagram Reel or Post URL.

    A URL is considered valid if its netloc (domain) is 'instagram.com' or
    'www.instagram.com' and it contains either '/reel/' or '/p/' in its path.

    Args:
        url (str): The URL string to validate.

    Returns:
        bool: True if the URL is a valid Instagram Reel/Post URL, False otherwise.
    """
    try:
        parsed = urlparse(url)
        # Check if the domain is Instagram and if it's a reel or post URL
        return parsed.netloc in ["instagram.com", "www.instagram.com"] and (
            "/reel/" in parsed.path or "/p/" in parsed.path
        )
    except ValueError:
        # urlparse can raise ValueError for malformed URLs
        return False
    except Exception:
        # Catch any other unexpected errors during parsing
        return False
