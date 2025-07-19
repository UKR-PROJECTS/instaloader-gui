from urllib.parse import urlparse


def is_valid_instagram_url(url: str) -> bool:
    """
    Validates if a given URL is a valid Instagram Reel or Post URL.

    A URL is considered valid if:
    1. Domain is 'instagram.com' or 'www.instagram.com'
    2. Path contains '/reel/' or '/p/' followed by an ID
    3. Has a valid reel/post ID after the pattern

    Args:
        url (str): The URL string to validate.

    Returns:
        bool: True if the URL is a valid Instagram Reel/Post URL, False otherwise.
    """
    try:
        parsed = urlparse(url)
        if parsed.netloc not in ["instagram.com", "www.instagram.com"]:
            return False

        path = parsed.path

        # Check for reel URLs
        if "/reel/" in path:
            parts = path.split("/reel/", 1)
            if len(parts) < 2 or not parts[1].split("/")[0]:
                return False
            return True

        # Check for post URLs
        if "/p/" in path:
            parts = path.split("/p/", 1)
            if len(parts) < 2 or not parts[1].split("/")[0]:
                return False
            return True

        return False
    except ValueError:
        return False
    except Exception:
        return False
