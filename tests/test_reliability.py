import unittest

from agent_patterns_lab.runtime import (
    CircuitBreaker,
    CircuitOpenError,
    FallbackExhausted,
    RetryExceeded,
    fallback_chain,
    retry,
)


class TestRetry(unittest.TestCase):
    def test_retry_eventually_succeeds(self) -> None:
        calls = {"n": 0}

        def fn() -> str:
            calls["n"] += 1
            if calls["n"] < 3:
                raise ValueError("no")
            return "ok"

        out = retry(fn, attempts=5, backoff_s=0)
        self.assertEqual(out, "ok")
        self.assertEqual(calls["n"], 3)

    def test_retry_exceeded(self) -> None:
        def fn() -> str:
            raise ValueError("no")

        with self.assertRaises(RetryExceeded):
            retry(fn, attempts=2, backoff_s=0)


class TestFallback(unittest.TestCase):
    def test_fallback_chain(self) -> None:
        out = fallback_chain([lambda: 1 / 0, lambda: "ok"])
        self.assertEqual(out, "ok")

    def test_fallback_exhausted(self) -> None:
        with self.assertRaises(FallbackExhausted):
            fallback_chain([lambda: 1 / 0])


class TestCircuitBreaker(unittest.TestCase):
    def test_opens_after_threshold(self) -> None:
        now = {"t": 0.0}

        def time_fn() -> float:
            return now["t"]

        cb = CircuitBreaker(failure_threshold=2, reset_timeout_s=10.0, time_fn=time_fn)

        def boom() -> str:
            raise ValueError("x")

        with self.assertRaises(ValueError):
            cb.call(boom)
        with self.assertRaises(ValueError):
            cb.call(boom)
        with self.assertRaises(CircuitOpenError):
            cb.call(lambda: "ok")

        now["t"] = 20.0  # half-open
        self.assertEqual(cb.call(lambda: "ok"), "ok")


if __name__ == "__main__":
    unittest.main()

