from config import *
from app import create_app

app22 = create_app()

if __name__ == '__main__':
  app22.run(host=Config.app_listen_address,port=Config.app_listen_port)