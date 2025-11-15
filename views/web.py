from flask import Flask, render_template, request, jsonify
import os
from constants import Constants

class WebInterface:
    def __init__(self, controller):
        self.app = Flask(
            __name__,
            template_folder='templates',
            static_folder='static'
        )
        self.controller = controller
        self.setup_routes()
        
    def setup_routes(self):
        @self.app.route('/')
        def index():
            return render_template('index.html')
        
        @self.app.route('/upload', methods=['POST'])
        def upload_file():
            if 'file' not in request.files:
                return jsonify({'error': 'Nenhum arquivo enviado'})
                
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'Nenhum arquivo selecionado'})
                
            if file and file.filename.endswith('.txt'):
                file_path = os.path.join('data', 'uploaded_text.txt')
                os.makedirs('data', exist_ok=True)
                file.save(file_path)
                
                result = self.controller.process_text_file(file_path)
                return jsonify(result)
            else:
                return jsonify({'error': 'Apenas arquivos .txt são permitidos'})
        
        @self.app.route('/infer', methods=['POST'])
        def run_inference():
            result = self.controller.run_inference()
            return jsonify(result)
        
        @self.app.route('/query', methods=['POST'])
        def execute_query():
            query = request.json.get('query', '')
            result = self.controller.execute_query(query)
            return jsonify(result)
        
        @self.app.route('/knowledge', methods=['GET'])
        def get_knowledge():
            kb_state = self.controller.get_knowledge_base()
            return jsonify(kb_state)
        
        @self.app.route('/clear', methods=['POST'])
        def clear_knowledge():
            result = self.controller.clear_knowledge_base()
            return jsonify(result)
    
    def run(self, debug=False):
        self.app.run(host=Constants.HOST, port=Constants.PORT, debug=debug )