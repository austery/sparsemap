
try:
    from google.genai import types
    import inspect
    print("Signature of types.GenerateContentConfig:")
    try:
        print(inspect.signature(types.GenerateContentConfig))
    except Exception:
        print(dir(types.GenerateContentConfig))
        
    print("\nDocstring:")
    print(types.GenerateContentConfig.__doc__)
except ImportError:
    print("google.genai not installed")
except Exception as e:
    print(f"Error: {e}")
