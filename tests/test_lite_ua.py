import unittest
from unittest.mock import patch

from lite_tools.tools.core.lite_ua import (
    generate_ua, get_ua, get_versions, judge_ua,
    reset_ua_cache, validate_versions_data
)


class TestLiteUA(unittest.TestCase):
    def test_get_ua_default_returns_string(self):
        ua = get_ua()
        self.assertIsInstance(ua, str)
        self.assertIn("Mozilla/5.0", ua)

    def test_generate_ua_return_meta(self):
        meta = generate_ua(platform="win", browser="chrome", return_meta=True)
        self.assertEqual(meta["platform"], "win")
        self.assertEqual(meta["browser"], "chrome")
        self.assertIn("Chrome/", meta["ua"])
        self.assertTrue(meta["version"])
        self.assertIn(meta["version"], meta["ua"])

    def test_alias_arguments_work(self):
        meta = get_ua("windows", "googlechrome", return_meta=True)
        self.assertEqual(meta["platform"], "win")
        self.assertEqual(meta["browser"], "chrome")
        self.assertIn("Chrome/", meta["ua"])

    def test_strict_invalid_combo_raises(self):
        with self.assertRaises(ValueError):
            generate_ua(platform="android", browser="safari", strict=True)

    def test_version_pool_is_normalized(self):
        versions = get_versions()
        self.assertIn("chromium", versions)
        self.assertIn("chromium_mobile", versions)
        self.assertIn("chromium_desktop", versions)
        self.assertIn("firefox", versions)
        self.assertIn("safari", versions)
        self.assertTrue(all(isinstance(item, str) for item in versions["chromium"]))

    def test_judge_ua_static_template(self):
        ua, version = judge_ua("ie", "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko", return_version=True)
        self.assertEqual(version, "")
        self.assertIn("Trident/7.0", ua)

    def test_validate_versions_data(self):
        self.assertTrue(validate_versions_data({"chromium": ["1"], "firefox": ["2"], "safari": ["3"]}))
        self.assertFalse(validate_versions_data({"chromium": [], "firefox": ["2"], "safari": ["3"]}))

    def test_mobile_template_uses_mobile_pool(self):
        reset_ua_cache()
        fake_versions = {
            "chromium": ["100.0.0.0"],
            "firefox": ["101"],
            "safari": ["16.0"],
            "chromium_desktop": ["200.0.0.0"],
            "chromium_mobile": ["300.0.0.0"],
            "safari_desktop": ["14.0"],
            "safari_mobile": ["15.0"],
        }
        with patch("lite_tools.tools.core.lite_ua.get_versions", return_value=fake_versions):
            meta = generate_ua(platform="iphone", browser="chrome", return_meta=True)
        self.assertEqual(meta["version"], "300.0.0.0")
        self.assertIn("CriOS/300.0.0.0", meta["ua"])


if __name__ == "__main__":
    unittest.main()
