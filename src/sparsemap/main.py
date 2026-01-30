from sparsemap.api.app import create_app


def main() -> None:
    app = create_app()
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8003, log_level="info")


if __name__ == "__main__":
    main()
