from flask import Flask, current_app
from api import api
from jf import JobFolder
app = Flask(__name__)
app.register_blueprint(api)

@app.route('/')
def start_app():
    if not hasattr(app, "jf"):
        app.jf = JobFolder()
    return "App started"


if __name__ == '__main__':
    try:
        app.run(host="127.0.0.1", port=5000)
    except Exception as error:
        print(f"An error occurred: {error}")
    finally:
        if hasattr(app, "jf"):
            app.jf.close()
