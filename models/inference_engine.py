from typing import List, Dict, Any, Tuple, Optional

class InferenceEngine:
    def __init__(self, knowledge_base):
        self.kb = knowledge_base
        self.inference_history = []
        
    def normalize_for_comparison(self, expression: str) -> str:
        if '(' in expression and ')' in expression:
            predicate, args = expression.split('(', 1)
            args = args.rstrip(')')
            
            predicate = predicate.lower().strip()
            
            normalized_args = []
            for arg in args.split(','):
                arg = arg.strip()
                if arg and not arg.isupper():  
                    arg = arg.lower()
                normalized_args.append(arg)
            
            return f"{predicate}({','.join(normalized_args)})"
        return expression.lower()
        
    def unify(self, pattern: str, fact: str) -> Optional[Dict[str, str]]:
        pattern_parts = pattern.split('(')
        fact_parts = fact.split('(')
        
        if len(pattern_parts) != 2 or len(fact_parts) != 2:
            return None
            
        predicate_pattern = pattern_parts[0].lower()  
        predicate_fact = fact_parts[0].lower()        
        
        if predicate_pattern != predicate_fact:
            return None
            
        args_pattern = pattern_parts[1].rstrip(')').split(',')
        args_fact = fact_parts[1].rstrip(')').split(',')
        
        if len(args_pattern) != len(args_fact):
            return None
            
        substitution = {}
        for pat_arg, fact_arg in zip(args_pattern, args_fact):
            pat_arg = pat_arg.strip()
            fact_arg = fact_arg.strip()
            if pat_arg.isupper():
                substitution[pat_arg] = fact_arg
            elif pat_arg.lower() != fact_arg.lower():  
                return None
                
        return substitution if substitution else {}
    
    def apply_substitution(self, expression: str, substitution: Dict[str, str]) -> str:
        result = expression
        for var, value in substitution.items():
            result = result.replace(var, value)
        return result
    
    def forward_chaining(self) -> List[Dict[str, Any]]:
        new_inferences = []
        changed = True
        
        while changed:
            changed = False
            for rule in self.kb.rules:
                if ':-' in rule:
                    head, body = rule.split(':-')
                    head = head.strip()
                    body = body.strip()
                    
                    for fact in self.kb.facts:
                        substitution = self.unify(body, fact)
                        if substitution is not None:
                            new_fact = self.apply_substitution(head, substitution)
                            
                            if not self.kb.fact_exists(new_fact) and new_fact not in [inf['fact'] for inf in new_inferences]:
                                self.kb.add_fact(new_fact)
                                new_inferences.append({
                                    'fact': new_fact,
                                    'rule': rule,
                                    'based_on': fact,
                                    'substitution': substitution
                                })
                                changed = True
                                
        self.inference_history.extend(new_inferences)
        return new_inferences
    
    def query_with_proof(self, query: str, visited: set = None) -> Tuple[bool, List[Dict[str, Any]]]:
        if visited is None:
            visited = set()
            
        query_key = self.normalize_for_comparison(query)
        if query_key in visited:
            return False, []  
        visited.add(query_key)
        
        query = query.strip()
        
        if self.is_original_fact(query):
            return True, [{
                'type': 'fact', 
                'content': query,
                'conclusion': query,
                'is_original': True
            }]
        
        
        for rule in self.kb.rules:
            if ':-' in rule:
                head, body = rule.split(':-')
                head = head.strip()
                body = body.strip()
                
                substitution = self.unify(head, query)
                if substitution is not None:
                    substituted_body = self.apply_substitution(body, substitution)
                    
                    is_true, body_proof = self.query_with_proof(substituted_body, visited.copy())
                    if is_true:
                        
                        proof = body_proof + [{
                            'type': 'rule',
                            'rule': rule,
                            'substitution': substitution,
                            'conclusion': query,
                            'premises': body_proof
                        }]
                        return True, proof
        
        return False, []
    
    def is_original_fact(self, fact: str) -> bool:
        normalized_fact = self.normalize_for_comparison(fact)
        
        if normalized_fact in [self.normalize_for_comparison(f) for f in self.kb.facts]:
            
            for inference in self.inference_history:
                if self.normalize_for_comparison(inference['fact']) == normalized_fact:
                    return False
            return True
        return False
    
    def get_proof_tree(self, proof: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not proof:
            return {}
        
        main_conclusion = proof[-1] if proof else {}
        
        if main_conclusion.get('type') == 'fact':
            return {
                'node': main_conclusion['conclusion'],
                'type': 'fact',
                'is_original': main_conclusion.get('is_original', False),
                'children': []
            }
        elif main_conclusion.get('type') == 'rule':
            
            children = []
            for premise in main_conclusion.get('premises', []):
                child_tree = self.get_proof_tree([premise])
                if child_tree:
                    children.append(child_tree)
            
            return {
                'node': main_conclusion['conclusion'],
                'type': 'rule',
                'rule': main_conclusion['rule'],
                'substitution': main_conclusion.get('substitution', {}),
                'children': children
            }
        
        return {}
    
    def format_proof_tree(self, tree: Dict[str, Any], level: int = 0, is_last: bool = True) -> str:
        """Formata a árvore de prova em texto com indentação"""
        if not tree:
            return ""
        
        indent = "    " * level
        prefix = "└── " if is_last else "├── "
        node_str = tree['node']
        
        if tree['type'] == 'fact':
            proof_type = "fato base" if tree.get('is_original', False) else "fato"
            result = f"{indent}{prefix}{node_str} ({proof_type})\n"
        else:
            result = f"{indent}{prefix}{node_str}\n"
            children = tree.get('children', [])
            for i, child in enumerate(children):
                is_last_child = i == len(children) - 1
                result += self.format_proof_tree(child, level + 1, is_last_child)
        
        return result
    
    def execute_query_with_proof(self, query: str) -> Dict[str, Any]:
        original_facts = self.kb.facts.copy()
        original_inferences = self.inference_history.copy()
        
        inferred_facts = [inf['fact'] for inf in self.inference_history]
        self.kb.facts = [fact for fact in self.kb.facts if fact not in inferred_facts]
        self.inference_history = []
        
        try:
            is_true, proof = self.query_with_proof(query)
            proof_tree = self.get_proof_tree(proof)
            formatted_proof = self.format_proof_tree(proof_tree).strip()
            
            return {
                'query': query,
                'result': is_true,
                'proof': proof,
                'proof_tree': proof_tree,
                'formatted_proof': formatted_proof
            }
        finally:
            self.kb.facts = original_facts
            self.inference_history = original_inferences