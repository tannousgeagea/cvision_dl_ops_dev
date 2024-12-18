import os
import uvicorn
import logging
import inspect
import importlib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from data_reader.routers.images import endpoint

ROUTERS_DIR = os.path.dirname(__file__) + "/routers"
ROUTERS = [
    f"data_reader.routers.{f.replace('/', '.')}" 
    for f in os.listdir(ROUTERS_DIR)
    if not f.endswith('__pycache__')
    if not f.endswith('__.py')
    ]

print(ROUTERS)

def create_app() -> FastAPI:
    tags_meta = [
        {
            "name": "Data Upload DATA API",
            "description": "Image Upload data entrypoint API"
        }
    ]

    app = FastAPI(
        openapi_tags = tags_meta,
        debug=True,
        title="Data Upload data entrypoint API",
        summary="",
        version="0.0.1",
        contact={
            "name": "Tannous Geagea",
            "url": "https://wasteant.com",
            "email": "tannous.geagea@wasteant.com",            
        },
        openapi_url="/openapi.json"
    )

    origins = ["http://localhost:3002", "http://192.168.0.142:3000", "http://localhost:8085"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=["*"],
        allow_headers=["X-Requested-With", "X-Request-ID"],
        expose_headers=["X-Request-ID"],
    )

    for R in ROUTERS:
        try:
            module = importlib.import_module(R)
            attr = getattr(module, 'endpoint')
            if inspect.ismodule(attr):
                app.include_router(module.endpoint.router)
        except ImportError as err:
            logging.error(f'Failed to import {R}: {err}')
    
    return app

app = create_app()


if __name__ == "__main__":
    import os
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv('DATA_API_PORT')), log_level="debug", reload=True)