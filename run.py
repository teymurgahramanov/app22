from app import create_app
from config import Config

app22 = create_app()

if __name__ == '__main__':
  if Config.DEBUG:
    app22.run(host='0.0.0.0', port=5000)
  else:
    from waitress import serve
    serve(app22, host='0.0.0.0', port=5000)