import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from models.knowledge_base import KnowledgeBase
from models.text_processor import TextProcessor
from models.inference_engine import InferenceEngine

class InferenceController:
    def __init__(self):
        self.kb = KnowledgeBase()
        self.text_processor = TextProcessor()
        self.inference_engine = InferenceEngine(self.kb)
        self.kb.load_from_file()
        
    def process_text_file(self, file_path: str) -> dict:
        """Processa um arquivo de texto e atualiza a base de conhecimento"""
        facts, rules = self.text_processor.process_text_file(file_path)
        
        for fact in facts:
            self.kb.add_fact(fact)
        for rule in rules:
            self.kb.add_rule(rule)
            
        self.kb.save_to_file()
        
        return {
            'facts_extracted': facts,
            'rules_extracted': rules,
            'total_facts': len(facts),
            'total_rules': len(rules)
        }
    
    def run_inference(self) -> dict:
        """Executa inferência e retorna novos fatos"""
        new_inferences = self.inference_engine.forward_chaining()
        self.kb.save_to_file()
        
        return {
            'new_facts': [inf['fact'] for inf in new_inferences],
            'inference_details': new_inferences,
            'total_new': len(new_inferences)
        }
    
    def execute_query(self, query: str) -> dict:
        """Executa uma consulta e retorna o resultado com prova"""
        result = self.inference_engine.execute_query_with_proof(query)
        
        return {
            'query': query,
            'result': result['result'],
            'proof': result['proof'],
            'proof_tree': result['proof_tree'],
            'formatted_proof': result['formatted_proof']
        }
    
    def get_knowledge_base(self) -> dict:
        """Retorna o estado atual da base de conhecimento"""
        return self.kb.get_state()
    
    def clear_knowledge_base(self) -> dict:
        """Limpa a base de conhecimento"""
        self.kb.clear()
        self.kb.save_to_file()
        return {'message': 'Base de conhecimento limpa com sucesso'}