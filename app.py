from controllers.inference import InferenceController
from views.web import WebInterface
import os

def create_app():
    os.makedirs('data', exist_ok=True)
    controller = InferenceController()
    web_interface = WebInterface(controller)
    
    return web_interface


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)