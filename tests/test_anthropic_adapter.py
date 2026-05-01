import unittest

from agent_patterns_lab.runtime import Message
from agent_patterns_lab.runtime.adapters.anthropic_model import AnthropicMessagesModel


class _Block:
    def __init__(self, text: str) -> None:
        self.text = text


class _Resp:
    def __init__(self, text: str) -> None:
        self.content = [_Block(text)]


class _StubMessages:
    def __init__(self, reply: str) -> None:
        self.reply = reply
        self.last_kwargs = None

    def create(self, **kwargs):  # type: ignore[no-untyped-def]
        self.last_kwargs = kwargs
        return _Resp(self.reply)


class _StubClient:
    def __init__(self, reply: str) -> None:
        self.messages = _StubMessages(reply)


class TestAnthropicAdapter(unittest.TestCase):
    def test_complete_extracts_system_and_converts_tool(self) -> None:
        stub = _StubClient("ok")
        model = AnthropicMessagesModel(model="stub", client=stub)

        out = model.complete(
            [
                Message(role="system", content="sys1"),
                Message(role="system", content="sys2"),
                Message(role="user", content="u"),
                Message(role="tool", name="search", content="doc"),
            ]
        )
        self.assertEqual(out, "ok")

        kwargs = stub.messages.last_kwargs
        self.assertIn("sys1", kwargs["system"])
        self.assertIn("sys2", kwargs["system"])
        msgs = kwargs["messages"]
        self.assertEqual(msgs[0]["role"], "user")
        self.assertEqual(msgs[0]["content"], "u")
        self.assertEqual(msgs[1]["role"], "user")
        self.assertIn("[tool:search]", msgs[1]["content"])


if __name__ == "__main__":
    unittest.main()

