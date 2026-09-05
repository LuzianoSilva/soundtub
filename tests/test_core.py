import importlib.util
import builtins
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "addon" / "globalPlugins" / "soundtub"
builtins._ = lambda text: text


def load(name):
    spec = importlib.util.spec_from_file_location(
        name, PACKAGE / (name.rsplit(".", 1)[-1] + ".py")
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


utils = load("soundtub.utils")
downloader = load("soundtub.downloader")


class CoreTests(unittest.TestCase):
    def test_url_validation(self):
        self.assertEqual(
            utils.validate_url(" https://example.com/v?id=1 "),
            "https://example.com/v?id=1",
        )
        self.assertIsNone(utils.validate_url("javascript:alert(1)"))
        self.assertIsNone(utils.validate_url("https://user:secret@example.com"))

    def test_progress(self):
        self.assertEqual(utils.parse_progress("ST_PROGRESS: 25.7%"), 25)
        self.assertEqual(utils.parse_progress("x ST_PROGRESS:100%"), 100)
        self.assertIsNone(utils.parse_progress("download started"))

    def test_playlist_item(self):
        self.assertEqual(utils.parse_playlist_item("ST_ITEM:3:12"), (3, 12))
        self.assertEqual(utils.parse_playlist_item("ST_ITEM:1:NA"), (1, None))
        self.assertIsNone(utils.parse_playlist_item("other output"))
        self.assertEqual(utils.parse_playlist_done("ST_DONE:15:16"), (15, 16))
        self.assertEqual(utils.parse_playlist_done("ST_DONE:2:NA"), (2, None))
        self.assertIsNone(utils.parse_playlist_done("ST_ITEM:2:16"))

    def test_playlist_command(self):
        worker = downloader.DownloadWorker(
            ROOT, "https://example.com/list", "MP3", ROOT, True,
            lambda value: None, lambda success, message: None,
        )
        command = worker.build_command()
        self.assertIn("--yes-playlist", command)
        self.assertNotIn("--no-playlist", command)
        self.assertTrue(any("%(playlist_title)" in value for value in command))
        self.assertTrue(any("ST_DONE" in value for value in command))

    def test_playlist_retry_only_missing_items(self):
        worker = downloader.DownloadWorker(
            ROOT, "https://example.com/list", "MP3", ROOT, True,
            lambda value: None, lambda success, message: None,
        )
        command = worker.build_command("mweb", [4, 9])
        position = command.index("--playlist-items")
        self.assertEqual(command[position + 1], "4,9")

    def test_permanent_playlist_errors_do_not_need_authorization(self):
        self.assertTrue(utils.has_permanent_content_error("ERROR: Video unavailable"))
        self.assertTrue(utils.has_permanent_content_error("ERROR: Private video"))
        self.assertFalse(utils.has_permanent_content_error("HTTP Error 403: Forbidden"))

    def test_destination(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertEqual(Path(utils.ensure_destination(folder)), Path(folder).resolve())

    def test_friendly_errors(self):
        self.assertIn("não é compatível", utils.friendly_error("ERROR: Unsupported URL"))
        self.assertNotIn("ERROR", utils.friendly_error("ERROR: something internal"))
        self.assertIn("limitou temporariamente", utils.friendly_error("HTTP Error 429: Too Many Requests"))
        self.assertIn("recusou", utils.friendly_error("HTTP Error 403: Forbidden"))
        self.assertIn("verificação anônima", utils.friendly_error("PO Token failed"))
        self.assertIn("acesso anônimo", utils.friendly_error("Sign in to confirm you're not a bot"))


if __name__ == "__main__":
    unittest.main()
