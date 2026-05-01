import json
import tempfile
import unittest
from pathlib import Path

from agent_patterns_lab.runtime import InMemoryKV, JsonFileKV, JsonFileSessionStore, KeyNotFound, SessionNotFound


class TestMemoryKV(unittest.TestCase):
    def test_inmemory_kv_get_set_delete(self) -> None:
        kv = InMemoryKV()
        kv.set("a", 1)
        self.assertEqual(kv.get("a"), 1)
        kv.delete("a")
        with self.assertRaises(KeyNotFound):
            kv.get("a")

    def test_jsonfile_kv_persists(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "kv.json"
            kv = JsonFileKV(path=path)
            kv.set("x", {"a": 1})

            kv2 = JsonFileKV(path=path)
            self.assertEqual(kv2.get("x"), {"a": 1})


class TestSessionStore(unittest.TestCase):
    def test_save_and_load(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            store = JsonFileSessionStore(root=Path(td))
            store.save("s1", {"a": 1})
            self.assertEqual(store.load("s1"), {"a": 1})

    def test_missing_raises(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            store = JsonFileSessionStore(root=Path(td))
            with self.assertRaises(SessionNotFound):
                store.load("nope")


if __name__ == "__main__":
    unittest.main()

