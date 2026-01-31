
try:
    from google.genai import types
    import inspect
    print("Signature of types.HttpOptions:")
    # It might be a TypedDict or Pydantic model or dataclass
    try:
        print(inspect.signature(types.HttpOptions))
    except Exception:
        print("Cannot get signature, trying dir:")
        print(dir(types.HttpOptions))
        
    print("\nDocstring:")
    print(types.HttpOptions.__doc__)
except ImportError:
    print("google.genai not installed")
except Exception as e:
    print(f"Error: {e}")
