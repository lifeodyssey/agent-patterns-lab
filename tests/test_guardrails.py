import unittest

from agent_patterns_lab.runtime import (
    BannedRegexTripwire,
    GuardrailViolation,
    Guardrails,
    MaxChars,
    ToolDenylist,
    TripwireTriggered,
)


class TestGuardrails(unittest.TestCase):
    def test_max_chars_blocks(self) -> None:
        rails = Guardrails(output_text=[MaxChars(max_chars=3)])
        rails.check_output("abc")
        with self.assertRaises(GuardrailViolation):
            rails.check_output("abcd")

    def test_tripwire_triggers(self) -> None:
        rails = Guardrails(output_text=[BannedRegexTripwire(patterns=[r"secret"])])
        with self.assertRaises(TripwireTriggered):
            rails.check_output("this contains SECRET")

    def test_tool_denylist_blocks(self) -> None:
        rails = Guardrails(tool_call=[ToolDenylist(denied={"rm"})])
        rails.check_tool_call("echo", {"x": 1})
        with self.assertRaises(GuardrailViolation):
            rails.check_tool_call("rm", {})


if __name__ == "__main__":
    unittest.main()

