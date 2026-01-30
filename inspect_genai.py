
try:
    from google import genai
    import inspect
    print("Signature of genai.Client:")
    print(inspect.signature(genai.Client))
    print("\nDocstring of genai.Client:")
    print(genai.Client.__doc__)
except ImportError:
    print("google.genai not installed")
except Exception as e:
    print(f"Error: {e}")
