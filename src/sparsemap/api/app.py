from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from sparsemap.core.logging import configure_logging
from sparsemap.api.routes.analyze import router as analyze_router


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="SparseMap API")

    # Enable CORS for development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    static_dir = Path(__file__).resolve().parents[3] / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

        @app.get("/")
        def read_root():
            return FileResponse(str(static_dir / "index.html"), media_type="text/html")
    else:
        @app.get("/")
        def read_root():
            return {"status": "running"}
    app.include_router(analyze_router, prefix="/api")
    return app
