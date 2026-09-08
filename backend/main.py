"""Entry point for Consultar Campo – Packing API."""

import uvicorn

from app.presentation.api.app import app

__all__ = ["app"]

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
