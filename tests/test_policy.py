import unittest

from agent_patterns_lab.runtime import ParamBound, PolicyViolation, ToolArgsPolicy, ToolPolicy


class TestToolPolicy(unittest.TestCase):
    def test_allowlist_blocks_unknown_tool(self) -> None:
        policy = ToolPolicy(allowed_tools={"safe"})
        policy.check_tool_call("safe", {})
        with self.assertRaises(PolicyViolation):
            policy.check_tool_call("other", {})

    def test_denylist_blocks_even_if_allowed(self) -> None:
        policy = ToolPolicy(allowed_tools={"safe", "danger"}, denied_tools={"danger"})
        policy.check_tool_call("safe", {})
        with self.assertRaises(PolicyViolation):
            policy.check_tool_call("danger", {})

    def test_per_tool_required_keys_and_bounds(self) -> None:
        policy = ToolPolicy(
            per_tool={
                "add": ToolArgsPolicy(
                    required_keys={"a", "b"},
                    allowed_keys={"a", "b"},
                    allow_unknown_keys=False,
                    bounds={
                        "a": ParamBound(minimum=0, maximum=10),
                        "b": ParamBound(minimum=0, maximum=10),
                    },
                )
            }
        )

        policy.check_tool_call("add", {"a": 2, "b": 3})

        with self.assertRaises(PolicyViolation):
            policy.check_tool_call("add", {"a": 2})

        with self.assertRaises(PolicyViolation):
            policy.check_tool_call("add", {"a": -1, "b": 3})

        with self.assertRaises(PolicyViolation):
            policy.check_tool_call("add", {"a": 2, "b": 3, "c": 0})

    def test_string_pattern_and_max_len(self) -> None:
        policy = ToolPolicy(
            per_tool={
                "echo": ToolArgsPolicy(
                    bounds={
                        "text": ParamBound(max_len=3, pattern=r"[a-z]+"),
                    }
                )
            }
        )

        policy.check_tool_call("echo", {"text": "abc"})
        with self.assertRaises(PolicyViolation):
            policy.check_tool_call("echo", {"text": "abcd"})
        with self.assertRaises(PolicyViolation):
            policy.check_tool_call("echo", {"text": "ABC"})


if __name__ == "__main__":
    unittest.main()

