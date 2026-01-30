"""LLM utility functions"""
import json
import re


def extract_json(payload: str) -> str:
    """
    Extract JSON from LLM response, removing markdown code blocks if present

    Args:
        payload: Raw LLM response

    Returns:
        Cleaned JSON string
    """
    if "```json" in payload:
        return payload.split("```json")[1].split("```")[0].strip()
    if "```" in payload:
        parts = payload.split("```")
        if len(parts) >= 3:
            return parts[1].strip().lstrip("json").strip()
    return payload.strip()


def fix_json(payload: str) -> str:
    """
    Fix common JSON formatting issues

    Args:
        payload: JSON string with potential issues

    Returns:
        Fixed JSON string
    """
    # Remove trailing commas before closing brackets/braces
    payload = re.sub(r',(\s*[}\]])', r'\1', payload)
    
    # Try basic fixes first
    payload = payload.replace(",]", "]").replace(",}", "}")
    
    return payload


def repair_json(payload: str) -> dict:
    """
    Aggressively repair malformed JSON

    Args:
        payload: Potentially malformed JSON string

    Returns:
        Parsed JSON dict

    Raises:
        ValueError: If JSON cannot be repaired
    """
    # Try direct parse
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        pass

    # Try with basic fixes
    try:
        fixed = fix_json(payload)
        return json.loads(fixed)
    except json.JSONDecodeError as e:
        print(f"⚠️  JSON parse error: {e.msg} at line {e.lineno}, col {e.colno}")

    # Try extracting first complete JSON object
    json_match = re.search(r'\{.*\}', payload, re.DOTALL)
    if json_match:
        try:
            extracted = json_match.group(0)
            fixed = fix_json(extracted)
            return json.loads(fixed)
        except json.JSONDecodeError:
            pass

    # Last resort: return minimal structure
    raise ValueError(f"Unable to repair JSON after multiple attempts")
