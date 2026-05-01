import unittest

from agent_patterns_lab.runtime import Message
from agent_patterns_lab.runtime.adapters.openai_model import OpenAIChatModel


class _StubResp:
    def __init__(self, text: str) -> None:
        self.choices = [_StubChoice(text)]


class _StubChoice:
    def __init__(self, text: str) -> None:
        self.message = _StubMsg(text)


class _StubMsg:
    def __init__(self, text: str) -> None:
        self.content = text


class _StubCompletions:
    def __init__(self, reply: str) -> None:
        self.reply = reply
        self.last_kwargs = None

    def create(self, **kwargs):  # type: ignore[no-untyped-def]
        self.last_kwargs = kwargs
        return _StubResp(self.reply)


class _StubChat:
    def __init__(self, completions: _StubCompletions) -> None:
        self.completions = completions


class _StubClient:
    def __init__(self, reply: str) -> None:
        self._completions = _StubCompletions(reply)
        self.chat = _StubChat(self._completions)


class TestOpenAIAdapter(unittest.TestCase):
    def test_complete_converts_tool_messages(self) -> None:
        stub = _StubClient("ok")
        model = OpenAIChatModel(model="stub", client=stub)

        out = model.complete(
            [
                Message(role="system", content="sys"),
                Message(role="user", content="u"),
                Message(role="tool", name="add", content="4"),
            ]
        )
        self.assertEqual(out, "ok")

        payload = stub._completions.last_kwargs["messages"]
        self.assertEqual(payload[0]["role"], "system")
        self.assertEqual(payload[1]["role"], "user")
        # Tool message is converted to a user message
        self.assertEqual(payload[2]["role"], "user")
        self.assertIn("[tool:add]", payload[2]["content"])


if __name__ == "__main__":
    unittest.main()

