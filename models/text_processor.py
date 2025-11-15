import spacy
import re
from typing import List, Tuple, Dict, Optional

class TextProcessor:
    def __init__(self):
        try:
            self.nlp = spacy.load("pt_core_news_sm")
        except OSError:
            print("Modelo spaCy para português não encontrado. Instale com: python -m spacy download pt_core_news_sm")
            exit(1)
        
        self.name_mapping = {}
        self.entity_counter = 1
        
        self.supported_verbs = ['ser']
        
    def extract_knowledge(self, text: str) -> Tuple[List[str], List[str]]:
        if not self.nlp:
            return [], []
            
        facts = []
        rules = []
        doc = self.nlp(text)
        
        sentences = [sent.text for sent in doc.sents]
        
        for sentence in sentences:
            sentence_facts, sentence_rules = self.process_sentence(sentence)
            facts.extend(sentence_facts)
            rules.extend(sentence_rules)
                    
        return facts, rules
    
    def process_sentence(self, sentence: str) -> Tuple[List[str], List[str]]:
        facts = []
        rules = []
        
        normalized = self.normalize_sentence(sentence)
        
        patterns = [
            
            (r"^tod[oa]\s+(.+?)\s+é\s+(.+?)$",
             lambda g: f"{self.normalize_predicate(g[1])}(X) :- {self.normalize_predicate(g[0])}(X)"),
            
            
            (r"^tod[oa]s\s+(.+?)\s+são\s+(.+?)$",
             lambda g: f"{self.normalize_predicate(g[1])}(X) :- {self.normalize_predicate(g[0])}(X)"),
            
            
            (r"^nenhum[ae]?\s+(.+?)\s+é\s+(.+?)$",
             lambda g: f"nao({self.normalize_predicate(g[1])}(X)) :- {self.normalize_predicate(g[0])}(X)"),
            
            
            (r"^se\s+(.+?)\s*,\s*então\s+(.+?)$",
             lambda g: self.process_conditional(g[0], g[1])),
            
            
            (r"^se\s+(.+?)\s+então\s+(.+?)$",
             lambda g: self.process_conditional(g[0], g[1])),
            
            
            (r"^(?:o|a|os|as)\s+(.+?)\s+é\s+(?:um|uma|o|a)\s+(.+?)$",
             lambda g: f"{self.normalize_predicate(g[1])}({self.normalize_entity(g[0])})"),
            
            
            (r"^(.+?)\s+é\s+(?:um|uma|o|a)?\s*(.+?)$",
             lambda g: self.process_fact_declaration(g[0], g[1])),
            
            
            (r"^(.+?)\s+são\s+(?:uns|umas|os|as)?\s*(.+?)$",
             lambda g: f"{self.normalize_predicate(g[1])}({self.normalize_entity(g[0])})"),
            
            
            (r"^(.+?)\s+é\s+(.+?)$",
             lambda g: self.process_identity(g[0], g[1])),
        ]
        
        for pattern, transformer in patterns:
            match = re.match(pattern, normalized, re.IGNORECASE)
            if match:
                result = transformer(match.groups())
                if result:
                    if ":-" in result:
                        rules.append(result)
                    else:
                        facts.append(result)
                break
        
        if not facts and not rules:
            semantic_result = self.semantic_analysis(sentence)
            if semantic_result:
                if ":-" in semantic_result:
                    rules.append(semantic_result)
                else:
                    facts.append(semantic_result)
        
        return facts, rules
    
    def process_fact_declaration(self, subject: str, predicate: str) -> Optional[str]:
        """Processa declarações de fato, ignorando artigos no predicado"""
        
        cleaned_predicate = self.remove_articles(predicate)
        
        
        if cleaned_predicate and len(cleaned_predicate.strip()) > 0:
            return f"{self.normalize_predicate(cleaned_predicate)}({self.normalize_entity(subject)})"
        
        return None
    
    def remove_articles(self, text: str) -> str:
        """Remove artigos do início do texto"""
        
        text = re.sub(r'^(o|a|os|as|um|uma|uns|umas)\s+', '', text.strip(), flags=re.IGNORECASE)
        return text.strip()
    
    def process_conditional(self, condition: str, conclusion: str) -> Optional[str]:
        try:
            cond_match = re.match(r"^(.+?)\s+é\s+(.+?)$", condition.strip(), re.IGNORECASE)
            concl_match = re.match(r"^(.+?)\s+é\s+(.+?)$", conclusion.strip(), re.IGNORECASE)
            
            if cond_match and concl_match:
                cond_subj, cond_pred = cond_match.groups()
                concl_subj, concl_pred = concl_match.groups()
                
                
                cond_pred = self.remove_articles(cond_pred)
                concl_pred = self.remove_articles(concl_pred)
                
                if cond_subj.lower() == concl_subj.lower() or cond_subj in ['X', 'x']:
                    return f"{self.normalize_predicate(concl_pred)}(X) :- {self.normalize_predicate(cond_pred)}(X)"
                else:
                    return f"{self.normalize_predicate(concl_pred)}(Y) :- {self.normalize_predicate(cond_pred)}(X)"
            
        except Exception as e:
            print(f"Erro ao processar condicional: {e}")
        
        return None
    
    def process_identity(self, subject: str, predicate: str) -> Optional[str]:
        
        cleaned_predicate = self.remove_articles(predicate)
        
        if (any(c.isupper() for c in predicate) or len(predicate.split()) == 1) and len(predicate) > 2:
            return f"{self.normalize_predicate(cleaned_predicate)}({self.normalize_entity(subject)})"
        else:
            return f"{self.normalize_predicate(cleaned_predicate)}({self.normalize_entity(subject)})"
    
    def semantic_analysis(self, sentence: str) -> Optional[str]:
        if not self.nlp:
            return None
            
        try:
            doc = self.nlp(sentence)
            
            for token in doc:
                if token.lemma_ == "ser" and token.pos_ == "VERB":
                    subject = None
                    predicate = None
                    
                    for child in token.children:
                        if child.dep_ in ["nsubj", "nsubj:pass"]:
                            subject = child.text
                        elif child.dep_ in ["attr", "acomp"]: 
                            predicate = child.text
                    
                    if subject and predicate:
                        
                        cleaned_predicate = self.remove_articles(predicate)
                        
                        if self.is_generic_term(subject) or self.is_generic_term(cleaned_predicate):
                            return f"{self.normalize_predicate(cleaned_predicate)}(X) :- {self.normalize_predicate(subject)}(X)"
                        else:
                            return f"{self.normalize_predicate(cleaned_predicate)}({self.normalize_entity(subject)})"
            
        except Exception as e:
            print(f"Erro na análise semântica: {e}")
        
        return None
    
    def is_generic_term(self, term: str) -> bool:
        term_lower = term.lower()
        
        generic_indicators = [
            'todo', 'toda', 'todos', 'todas', 'nenhum', 'nenhuma',
            'cada', 'qualquer', 'algum', 'alguma'
        ]
        
        if any(indicator in term_lower for indicator in generic_indicators):
            return True
        
        if len(term.split()) == 1 and len(term) <= 15:
            return True
            
        return False
    
    def normalize_sentence(self, sentence: str) -> str:
        sentence = re.sub(r'[^\w\s]', ' ', sentence)
        sentence = re.sub(r'\s+', ' ', sentence)
        return sentence.strip().lower()
    
    def normalize_entity(self, entity: str) -> str:
        entity = entity.strip()
        
        entity = re.sub(r'^(o|a|os|as|um|uma|uns|umas)\s+', '', entity, flags=re.IGNORECASE)
        
        normalized = entity.lower().replace(' ', '')
        
        if entity not in self.name_mapping:
            self.name_mapping[entity] = normalized
        
        return normalized
    
    def normalize_predicate(self, predicate: str) -> str:
        predicate = predicate.strip().lower()
        
        predicate = self.remove_articles(predicate)
        
        predicate = re.sub(r'^(todo|toda|todos|todas|nenhum|nenhuma|cada|qualquer|algum|alguma)\s+', '', predicate)
        
        predicate = predicate.replace(' ', '_')
        
        return predicate
    
    def add_verb_support(self, verb: str):
        if verb not in self.supported_verbs:
            self.supported_verbs.append(verb)
            print(f"Verbo '{verb}' adicionado à lista de suporte")
    
    def get_supported_verbs(self) -> List[str]:
        return self.supported_verbs.copy()
    
    def get_name_mapping(self) -> Dict[str, str]:
        return self.name_mapping.copy()
    
    def process_text_file(self, file_path: str) -> Tuple[List[str], List[str]]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            self.name_mapping = {}
            
            return self.extract_knowledge(text)
        except Exception as e:
            print(f"Erro ao processar arquivo: {e}")
            return [], []