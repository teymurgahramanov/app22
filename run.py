from app import create_app
from config import Config
import uvicorn

app = create_app()

if __name__ == '__main__':
    if Config.DEBUG:
        uvicorn.run("run:app", host='0.0.0.0', port=5000, reload=True)
    else:
        uvicorn.run(app, host='0.0.0.0', port=5000)