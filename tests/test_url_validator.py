import unittest
from src.utils.url_validator import is_valid_instagram_url


class TestURLValidator(unittest.TestCase):
    """Tests for the Instagram URL validator."""

    def test_valid_reel_url(self):
        """Test valid reel URLs."""
        self.assertTrue(
            is_valid_instagram_url("https://www.instagram.com/reel/Cxyz123/")
        )
        self.assertTrue(is_valid_instagram_url("https://instagram.com/reel/Cabc456/"))
        self.assertTrue(
            is_valid_instagram_url(
                "https://www.instagram.com/reel/Cdef789/?utm_source=ig_web_copy_link"
            )
        )

    def test_valid_post_url(self):
        """Test valid post URLs."""
        self.assertTrue(is_valid_instagram_url("https://www.instagram.com/p/Dxyz123/"))
        self.assertTrue(is_valid_instagram_url("https://instagram.com/p/Dabc456/"))
        self.assertTrue(
            is_valid_instagram_url(
                "https://www.instagram.com/p/Ddef789/?utm_source=ig_web_copy_link"
            )
        )

    def test_invalid_domains(self):
        """Test invalid domains."""
        self.assertFalse(
            is_valid_instagram_url("https://www.fakeinstagram.com/reel/Cxyz123/")
        )
        self.assertFalse(is_valid_instagram_url("https://malicious.com/reel/Cxyz123/"))
        self.assertFalse(is_valid_instagram_url("https://instagram.net/reel/Cxyz123/"))

    def test_non_reel_post_urls(self):
        """Test non-reel/post Instagram URLs."""
        self.assertFalse(is_valid_instagram_url("https://www.instagram.com/"))
        self.assertFalse(is_valid_instagram_url("https://www.instagram.com/explore/"))
        self.assertFalse(is_valid_instagram_url("https://www.instagram.com/username/"))
        self.assertFalse(
            is_valid_instagram_url("https://www.instagram.com/p/")
        )  # Missing ID
        self.assertFalse(
            is_valid_instagram_url("https://www.instagram.com/reel/")
        )  # Missing ID

    def test_malformed_urls(self):
        """Test malformed URLs."""
        self.assertFalse(is_valid_instagram_url("not a url"))
        self.assertFalse(
            is_valid_instagram_url("instagram.com/reel/Cxyz123")
        )  # Missing protocol
        self.assertFalse(
            is_valid_instagram_url("https://www.instagram.com/reel/")
        )  # Missing reel ID
        self.assertFalse(is_valid_instagram_url(""))  # Empty string


if __name__ == "__main__":
    unittest.main()
