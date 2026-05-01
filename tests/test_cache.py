import unittest

from agent_patterns_lab.runtime import CacheMiss, InMemoryCache, cached


class TestCache(unittest.TestCase):
    def test_ttl_expiration(self) -> None:
        now = {"t": 0.0}

        def time_fn() -> float:
            return now["t"]

        cache: InMemoryCache[str] = InMemoryCache(time_fn=time_fn)
        cache.set("k", "v", ttl_s=1.0)
        self.assertEqual(cache.get("k"), "v")
        now["t"] = 2.0
        with self.assertRaises(CacheMiss):
            cache.get("k")

    def test_cached_helper(self) -> None:
        cache: InMemoryCache[int] = InMemoryCache(time_fn=lambda: 0.0)
        calls = {"n": 0}

        def compute() -> int:
            calls["n"] += 1
            return 7

        a = cached(cache, key="x", compute=compute)
        b = cached(cache, key="x", compute=compute)
        self.assertEqual(a, 7)
        self.assertEqual(b, 7)
        self.assertEqual(calls["n"], 1)


if __name__ == "__main__":
    unittest.main()

