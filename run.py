from app import create_app

app22 = create_app()

if __name__ == '__main__':
  from waitress import serve
  serve(app22, host='0.0.0.0', port=5000)