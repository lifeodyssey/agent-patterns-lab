import unittest

from agent_patterns_lab.runtime import (
    ApprovalDenied,
    HITLController,
    NeedsApproval,
    ScriptedApprovalsExhausted,
    ScriptedApprover,
)


class TestHITL(unittest.TestCase):
    def test_check_requires_approval_then_can_resume(self) -> None:
        hitl = HITLController(require_approval_for_tools={"deploy"})

        with self.assertRaises(NeedsApproval) as ctx:
            hitl.check("deploy", {"env": "prod"})

        req = ctx.exception.request
        hitl.approve(req)
        # Retry the exact same call: should pass without raising.
        hitl.check("deploy", {"env": "prod"})

    def test_deny_cached(self) -> None:
        hitl = HITLController(require_approval_for_tools={"danger"})
        with self.assertRaises(NeedsApproval) as ctx:
            hitl.check("danger", {"x": 1})
        req = ctx.exception.request
        hitl.deny(req)
        with self.assertRaises(ApprovalDenied):
            hitl.check("danger", {"x": 1})

    def test_scripted_approver_exhausts(self) -> None:
        approver = ScriptedApprover([True])
        hitl = HITLController(require_approval_for_tools={"x"})
        with self.assertRaises(NeedsApproval) as ctx:
            hitl.check("x", {})
        req = ctx.exception.request
        self.assertTrue(approver.decide(req))
        with self.assertRaises(ScriptedApprovalsExhausted):
            approver.decide(req)


if __name__ == "__main__":
    unittest.main()

