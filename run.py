from app import create_app
from config import config
import uvicorn

app = create_app()

if __name__ == '__main__':
    if config.debug:
        uvicorn.run("run:app", host=config.host, port=config.port, reload=True)
    else:
        uvicorn.run(app, host=config.host, port=config.port)