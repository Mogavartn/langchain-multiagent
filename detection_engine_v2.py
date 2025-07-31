"""
Moteur de détection V2 optimisé - JAK Company
Version nettoyée et optimisée pour la logique décisionnelle V2
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from functools import lru_cache
from enum import Enum
from bloc_config_v2 import BlocType, BLOC_KEYWORDS, PRIORITY_RULES, PROFILE_BLOC_MAPPING, DECISION_LOGIC

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProfileType(Enum):
    """Types de profils utilisateurs"""
    AMBASSADOR = "ambassador"
    LEARNER_INFLUENCER = "learner_influencer"
    PROSPECT = "prospect"
    UNKNOWN = "unknown"

class FinancingType(Enum):
    """Types de financement"""
    DIRECT = "direct"
    OPCO = "opco"
    CPF = "cpf"
    UNKNOWN = "unknown"

class DetectionEngineV2:
    """Moteur de détection V2 optimisé pour JAK Company"""
    
    def __init__(self):
        self._init_keyword_cache()
        self._init_priority_order()
    
    def _init_keyword_cache(self):
        """Initialise le cache des mots-clés pour optimisation"""
        self._keyword_cache = {}
        for bloc_type, config in BLOC_KEYWORDS.items():
            self._keyword_cache[bloc_type] = frozenset(config["keywords"])
    
    def _init_priority_order(self):
        """Initialise l'ordre de priorité des blocs"""
        self._priority_order = []
        for priority_level in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            self._priority_order.extend(PRIORITY_RULES[priority_level])
    
    @lru_cache(maxsize=100)
    def detect_profile(self, message: str) -> ProfileType:
        """Détecte le profil de l'utilisateur"""
        message_lower = message.lower()
        
        # Détection ambassadeur
        ambassador_indicators = DECISION_LOGIC["profile_detection"]["ambassador_indicators"]
        if any(indicator in message_lower for indicator in ambassador_indicators):
            return ProfileType.AMBASSADOR
        
        # Détection apprenant/influenceur
        learner_indicators = DECISION_LOGIC["profile_detection"]["learner_indicators"]
        if any(indicator in message_lower for indicator in learner_indicators):
            return ProfileType.LEARNER_INFLUENCER
        
        # Détection prospect
        prospect_indicators = DECISION_LOGIC["profile_detection"]["prospect_indicators"]
        if any(indicator in message_lower for indicator in prospect_indicators):
            return ProfileType.PROSPECT
        
        return ProfileType.UNKNOWN
    
    @lru_cache(maxsize=50)
    def detect_financing_type(self, message: str) -> FinancingType:
        """Détecte le type de financement"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["cpf", "compte personnel formation"]):
            return FinancingType.CPF
        elif any(word in message_lower for word in ["opco", "opérateur compétences"]):
            return FinancingType.OPCO
        elif any(word in message_lower for word in ["direct", "immédiat", "maintenant"]):
            return FinancingType.DIRECT
        
        return FinancingType.UNKNOWN
    
    @lru_cache(maxsize=50)
    def extract_time_info(self, message: str) -> Dict[str, int]:
        """Extrait les informations temporelles du message"""
        message_lower = message.lower()
        
        time_patterns = {
            "jours": r"(\d+)\s*jour",
            "semaines": r"(\d+)\s*semaine",
            "mois": r"(\d+)\s*mois",
            "années": r"(\d+)\s*année"
        }
        
        time_info = {}
        for unit, pattern in time_patterns.items():
            match = re.search(pattern, message_lower)
            if match:
                time_info[unit] = int(match.group(1))
        
        return time_info
    
    def convert_to_days(self, time_info: Dict[str, int]) -> int:
        """Convertit les informations temporelles en jours"""
        total_days = 0
        if "jours" in time_info:
            total_days += time_info["jours"]
        if "semaines" in time_info:
            total_days += time_info["semaines"] * 7
        if "mois" in time_info:
            total_days += time_info["mois"] * 30
        if "années" in time_info:
            total_days += time_info["années"] * 365
        return total_days
    
    @lru_cache(maxsize=100)
    def detect_aggressive_behavior(self, message: str) -> bool:
        """Détecte les comportements agressifs"""
        message_lower = message.lower()
        aggressive_keywords = BLOC_KEYWORDS[BlocType.AGRO]["keywords"]
        return any(keyword in message_lower for keyword in aggressive_keywords)
    
    @lru_cache(maxsize=100)
    def detect_formation_interest(self, message: str, recent_blocs: List[str]) -> bool:
        """Détecte si l'utilisateur exprime un intérêt pour une formation spécifique"""
        message_lower = message.lower()
        
        interest_indicators = [
            "intéressé par", "je choisis", "je veux", "m'intéresse", 
            "ça m'intéresse", "je prends", "je sélectionne", "je souhaite",
            "je voudrais"
        ]
        
        formation_keywords = [
            "comptabilité", "marketing", "langues", "web", "3d", "vente", 
            "développement", "bureautique", "informatique", "écologie", "bilan",
            "anglais", "français", "espagnol", "allemand", "italien"
        ]
        
        has_interest = any(indicator in message_lower for indicator in interest_indicators)
        has_formation = any(keyword in message_lower for keyword in formation_keywords)
        
        # Vérifier si l'utilisateur a récemment vu les formations
        formations_recently_shown = any("BLOC K" in bloc for bloc in recent_blocs)
        
        return has_interest and has_formation and formations_recently_shown
    
    def detect_primary_bloc(self, message: str, session_context: Dict[str, Any] = None) -> BlocType:
        """Détecte le bloc principal selon la logique V2"""
        message_lower = message.lower()
        
        # 1. Vérification priorité absolue - Comportement agressif
        if self.detect_aggressive_behavior(message):
            logger.info("Comportement agressif détecté - BLOC AGRO")
            return BlocType.AGRO
        
        # 2. Vérification par ordre de priorité
        for bloc_type in self._priority_order:
            if bloc_type in self._keyword_cache:
                if self._has_keywords(message_lower, self._keyword_cache[bloc_type]):
                    logger.info(f"Bloc détecté: {bloc_type.value}")
                    return bloc_type
        
        # 3. Fallback vers le bloc général
        logger.info("Aucun bloc spécifique détecté - BLOC GENERAL")
        return BlocType.GENERAL
    
    def detect_follow_up_context(self, message: str, session_context: Dict[str, Any]) -> Optional[BlocType]:
        """Détecte les messages de suivi basés sur le contexte conversationnel"""
        message_lower = message.lower()
        
        # Récupérer le contexte récent
        last_bloc = session_context.get("last_bloc")
        recent_blocs = session_context.get("recent_blocs", [])
        
        # Détection d'agressivité prioritaire
        if self.detect_aggressive_behavior(message):
            return BlocType.AGRO
        
        # Si l'utilisateur a vu les formations et exprime un intérêt
        if self.detect_formation_interest(message, recent_blocs):
            return BlocType.M
        
        # Si l'utilisateur vient de voir les ambassadeurs et pose des questions
        if last_bloc in ["BLOC D1", "BLOC D2"] and any(word in message_lower for word in ["comment", "quand", "où", "combien"]):
            return BlocType.E  # Processus ambassadeur
        
        # Si l'utilisateur vient de voir un problème de paiement et donne plus d'infos
        if last_bloc == "BLOC A" and any(word in message_lower for word in ["depuis", "ça fait", "délai", "attendre"]):
            return BlocType.L  # Délai dépassé
        
        # Si l'utilisateur répond à une question de filtrage CPF
        if last_bloc == "BLOC F1" and any(word in message_lower for word in ["oui", "non", "bloqué", "informé"]):
            return BlocType.F2  # Suite du processus CPF
        
        # Si l'utilisateur répond à une question de filtrage OPCO
        if last_bloc == "BLOC F3" and any(word in message_lower for word in ["oui", "non", "bloqué", "informé"]):
            return BlocType.F2  # Suite du processus OPCO
        
        return None
    
    @lru_cache(maxsize=100)
    def _has_keywords(self, message_lower: str, keyword_set: frozenset) -> bool:
        """Vérifie si le message contient les mots-clés d'un bloc"""
        return any(keyword in message_lower for keyword in keyword_set)
    
    def should_escalate(self, bloc_type: BlocType, context: Dict[str, Any]) -> bool:
        """Détermine si une escalade est nécessaire"""
        escalation_rules = DECISION_LOGIC["escalation_rules"]
        
        # Escalade immédiate pour comportements critiques
        if bloc_type in [BlocType.AGRO, BlocType.LEGAL, BlocType.F1, BlocType.F3]:
            return True
        
        # Escalade pour délais de paiement dépassés
        if bloc_type == BlocType.A:
            payment_context = context.get("payment_context", {})
            total_days = payment_context.get("total_days", 0)
            if total_days > escalation_rules["payment_delay_threshold"]:
                return True
        
        # Escalade pour blocs d'escalade spécifiques
        if bloc_type in [BlocType.BLOC_61, BlocType.BLOC_62]:
            return True
        
        return False
    
    def get_escalation_type(self, bloc_type: BlocType) -> str:
        """Détermine le type d'escalade"""
        if bloc_type == BlocType.BLOC_61:
            return "admin"
        elif bloc_type == BlocType.BLOC_62:
            return "commercial"
        elif bloc_type == BlocType.AGRO:
            return "quality"
        elif bloc_type in [BlocType.F1, BlocType.F3]:
            return "cpf_specialist"
        else:
            return "general"
    
    def create_response_context(self, bloc_type: BlocType, message: str, session_context: Dict[str, Any]) -> Dict[str, Any]:
        """Crée le contexte de réponse pour le bloc détecté"""
        context = {
            "bloc_type": bloc_type,
            "bloc_id": bloc_type.value,
            "message": message,
            "should_escalate": self.should_escalate(bloc_type, session_context),
            "priority_level": self._get_priority_level(bloc_type),
            "profile": self.detect_profile(message).value,
            "financing_type": self.detect_financing_type(message).value
        }
        
        # Ajouter le type d'escalade si nécessaire
        if context["should_escalate"]:
            context["escalation_type"] = self.get_escalation_type(bloc_type)
        
        # Ajouter le contexte de paiement si pertinent
        if bloc_type == BlocType.A:
            time_info = self.extract_time_info(message)
            total_days = self.convert_to_days(time_info)
            context["payment_context"] = {
                "time_info": time_info,
                "total_days": total_days,
                "financing_type": context["financing_type"]
            }
        
        return context
    
    def _get_priority_level(self, bloc_type: BlocType) -> str:
        """Retourne le niveau de priorité d'un bloc"""
        for level, blocs in PRIORITY_RULES.items():
            if bloc_type in blocs:
                return level
        return "LOW"
    
    def get_bloc_description(self, bloc_type: BlocType) -> str:
        """Retourne la description d'un bloc"""
        if bloc_type in BLOC_KEYWORDS:
            return BLOC_KEYWORDS[bloc_type]["description"]
        return "Description non disponible"
    
    def get_bloc_keywords(self, bloc_type: BlocType) -> List[str]:
        """Retourne les mots-clés d'un bloc"""
        if bloc_type in BLOC_KEYWORDS:
            return BLOC_KEYWORDS[bloc_type]["keywords"]
        return []
    
    def validate_bloc_sequence(self, current_bloc: BlocType, previous_bloc: Optional[BlocType]) -> bool:
        """Valide la séquence de blocs selon la logique métier"""
        if not previous_bloc:
            return True
        
        # Règles de validation spécifiques
        validation_rules = {
            BlocType.F2: [BlocType.F1, BlocType.F3],  # F2 doit suivre F1 ou F3
            BlocType.E: [BlocType.D1, BlocType.D2],   # E doit suivre D1 ou D2
            BlocType.M: [BlocType.K],                 # M doit suivre K
            BlocType.L: [BlocType.A]                  # L doit suivre A
        }
        
        if current_bloc in validation_rules:
            return previous_bloc in validation_rules[current_bloc]
        
        return True