from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from contextlib import asynccontextmanager

class FastAPIApp:
    def __init__(self,title:str):

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            print("Starting up...")
            yield
            print("Shutting down...")

        self._app = FastAPI(
            title=title,
            description="API for Beacon application",
        
            lifespan=lifespan
        )
        self.configure_middleware()

    def configure_middleware(self):
        self._app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def get_app(self) -> FastAPI:
        return self._app