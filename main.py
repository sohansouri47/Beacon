from fastapi import FastAPI
from src.chat.chat_router import ChatRouter
from src.api.fastapi import FastAPIApp
import uvicorn
from typing import Protocol, Type
import os

host = os.getenv("BEACON_HOST", "0.0.0.0")
port = int(os.getenv("BEACON_PORT", "5001"))
public_url = os.getenv("BEACON_URL", f"http://{host}:{port}")

app_instance = FastAPIApp(title="Beacon API")
app = app_instance.get_app()


class RouterClass(Protocol):
    def get_router(self) -> FastAPI: ...


routers: list[Type[RouterClass]] = [
    ChatRouter,
]

for router_cls in routers:
    router_instance = router_cls(app)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        ws_ping_interval=20,
        ws_ping_timeout=1200,
    )
