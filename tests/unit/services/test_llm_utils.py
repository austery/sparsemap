import pytest
from sparsemap.services.llm_utils import extract_json, fix_json, escape_newlines_in_strings, repair_json

class TestExtractJson:
    def test_extract_json_with_markdown_block(self):
        payload = 'Here is the json:\n```json\n{"key": "value"}\n```'
        assert extract_json(payload) == '{"key": "value"}'

    def test_extract_json_with_generic_block(self):
        payload = '```\n{"key": "value"}\n```'
        assert extract_json(payload) == '{"key": "value"}'

    def test_extract_json_plain(self):
        payload = '{"key": "value"}'
        assert extract_json(payload) == '{"key": "value"}'

    def test_extract_json_none(self):
        assert extract_json(None) == ""

class TestFixJson:
    def test_fix_json_trailing_comma_dict(self):
        payload = '{"key": "value",}'
        assert fix_json(payload) == '{"key": "value"}'

    def test_fix_json_trailing_comma_list(self):
        payload = '["value",]'
        assert fix_json(payload) == '["value"]'

    def test_fix_json_trailing_comma_nested(self):
        payload = '{"list": ["val",], "dict": {"k": "v",}}'
        # The regex might not handle nested perfectly in one go if relying on simple replace,
        # but the function uses regex for `,]` and `,}`.
        expected = '{"list": ["val"], "dict": {"k": "v"}}'
        assert fix_json(payload) == expected

class TestEscapeNewlines:
    def test_escape_newlines_in_strings(self):
        payload = '{"key": "multi\nline"}'
        expected = '{"key": "multi\\nline"}'
        assert escape_newlines_in_strings(payload) == expected

    def test_escape_newlines_no_change(self):
        payload = '{"key": "value"}'
        assert escape_newlines_in_strings(payload) == payload

class TestRepairJson:
    def test_repair_json_valid(self):
        payload = '{"key": "value"}'
        assert repair_json(payload) == {"key": "value"}

    def test_repair_json_with_comments_fix(self):
        # The current implementation doesn't strip comments but fixes trailing commas
        payload = '{"key": "value",}'
        assert repair_json(payload) == {"key": "value"}

    def test_repair_json_extract_from_text(self):
        payload = 'some text {"key": "value"} some other text'
        assert repair_json(payload) == {"key": "value"}

    def test_repair_json_unescaped_newlines(self):
        payload = '{"key": "multi\nline"}'
        assert repair_json(payload) == {"key": "multi\nline"}

    def test_repair_json_failure(self):
        payload = 'invalid json'
        with pytest.raises(ValueError, match="Unable to repair JSON"):
            repair_json(payload)

