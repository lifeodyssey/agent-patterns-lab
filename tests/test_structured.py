import unittest

from agent_patterns_lab.runtime import (
    JsonExtractionError,
    Message,
    MockLLM,
    SchemaValidationError,
    Tracer,
    extract_json_value,
    structured_complete,
)


class TestJsonExtraction(unittest.TestCase):
    def test_extracts_raw_json(self) -> None:
        res = extract_json_value('{"a": 1}')
        self.assertEqual(res.json_value, {"a": 1})

    def test_extracts_fenced_json(self) -> None:
        res = extract_json_value("```json\n{\"a\": 1}\n```")
        self.assertEqual(res.json_value, {"a": 1})

    def test_extracts_embedded_json(self) -> None:
        res = extract_json_value('Sure! Here: {"a": 1} Thanks.')
        self.assertEqual(res.json_value, {"a": 1})

    def test_raises_on_no_json(self) -> None:
        with self.assertRaises(JsonExtractionError):
            extract_json_value("nope")


class TestStructuredComplete(unittest.TestCase):
    def test_retries_on_schema_error(self) -> None:
        tracer = Tracer()
        model = MockLLM(['{"answer": 1}', '{"answer": "ok"}'])

        def parse(value):
            if not isinstance(value, dict):
                raise SchemaValidationError("expected object")
            if not isinstance(value.get("answer"), str):
                raise SchemaValidationError("answer must be string")
            return value["answer"]

        out = structured_complete(
            model,
            [Message(role="user", content="x")],
            parser=parse,
            schema_hint='{"answer":"<string>"}',
            tracer=tracer,
            max_retries=1,
        )
        self.assertEqual(out, "ok")
        self.assertEqual(model.remaining(), 0)
        self.assertTrue(any(e.name == "structured.failure" for e in tracer.events))
        self.assertTrue(any(e.name == "structured.success" for e in tracer.events))

    def test_raises_after_max_retries(self) -> None:
        model = MockLLM(['{"answer": 1}', '{"answer": 2}'])

        def parse(value):
            raise SchemaValidationError("always bad")

        with self.assertRaises(SchemaValidationError):
            structured_complete(
                model,
                [Message(role="user", content="x")],
                parser=parse,
                max_retries=1,
            )


if __name__ == "__main__":
    unittest.main()

