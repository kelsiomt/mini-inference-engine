import json
import os
from typing import Dict, List
from constants import Constants

class KnowledgeBase:
    def __init__(self):
        self.facts = []
        self.rules = []
        self.kb_file = f"data/{Constants.KNOWLEDGE_BASE_FILENAME}"
        
    def normalize_fact(self, fact: str) -> str:

        if '(' in fact and ')' in fact:
            
            predicate, args = fact.split('(', 1)
            args = args.rstrip(')')
            
            
            predicate = predicate.lower().strip()
            
            
            normalized_args = []
            for arg in args.split(','):
                arg = arg.strip()
                if arg and not arg.isupper():  
                    arg = arg.lower()
                normalized_args.append(arg)
            
            return f"{predicate}({','.join(normalized_args)})"
        return fact.lower()
    
    def add_fact(self, fact: str):

        normalized_fact = self.normalize_fact(fact)
        if normalized_fact not in self.facts:
            self.facts.append(normalized_fact)
            
    def add_rule(self, rule: str):

        
        if rule not in self.rules:
            self.rules.append(rule)
            
    def clear(self):

        self.facts.clear()
        self.rules.clear()
        
    def save_to_file(self):

        os.makedirs(os.path.dirname(self.kb_file), exist_ok=True)
        with open(self.kb_file, 'w', encoding='utf-8') as f:
            json.dump({
                'facts': self.facts,
                'rules': self.rules
            }, f, indent=2, ensure_ascii=False)
            
    def load_from_file(self):

        try:
            with open(self.kb_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.facts = data.get('facts', [])
                self.rules = data.get('rules', [])
        except FileNotFoundError:
            self.facts = []
            self.rules = []
            
    def get_state(self) -> Dict[str, List]:

        return {
            'facts': self.facts,
            'rules': self.rules
        }
    
    def fact_exists(self, fact: str) -> bool:

        normalized_fact = self.normalize_fact(fact)
        return normalized_fact in self.facts