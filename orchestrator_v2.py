"""
Orchestrateur V2 optimisé - JAK Company
Version nettoyée et optimisée pour la logique décisionnelle V2
"""

import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass

from bloc_config_v2 import BlocType, PROFILE_BLOC_MAPPING, DECISION_LOGIC
from detection_engine_v2 import DetectionEngineV2, ProfileType, FinancingType
from memory_store_v2 import OptimizedMemoryStoreV2

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentType(Enum):
    """Types d'agents spécialisés V2"""
    GENERAL = "general"
    AMBASSADOR = "ambassador"
    LEARNER = "learner"
    PROSPECT = "prospect"
    PAYMENT = "payment"
    CPF_BLOCKED = "cpf_blocked"
    QUALITY = "quality"

@dataclass
class OrchestrationResult:
    """Résultat de l'orchestration"""
    bloc_type: BlocType
    agent_type: AgentType
    bloc_id: str
    should_escalate: bool
    escalation_type: Optional[str] = None
    priority_level: str = "MEDIUM"
    profile: str = "unknown"
    financing_type: str = "unknown"
    context_data: Dict[str, Any] = None
    processing_time: float = 0.0
    
    def __post_init__(self):
        if self.context_data is None:
            self.context_data = {}

class MultiAgentOrchestratorV2:
    """Orchestrateur V2 optimisé pour JAK Company"""
    
    def __init__(self):
        self.detection_engine = DetectionEngineV2()
        self.memory_store = OptimizedMemoryStoreV2()
        self._init_bloc_agent_mapping()
        logger.info("Orchestrateur V2 initialisé")
    
    def _init_bloc_agent_mapping(self):
        """Initialise le mapping bloc -> agent"""
        self.bloc_agent_mapping = {
            # Agent Général
            BlocType.GENERAL: AgentType.GENERAL,
            BlocType.G: AgentType.GENERAL,
            
            # Agent Ambassadeur
            BlocType.B1: AgentType.AMBASSADOR,
            BlocType.B2: AgentType.AMBASSADOR,
            BlocType.D1: AgentType.AMBASSADOR,
            BlocType.D2: AgentType.AMBASSADOR,
            BlocType.E: AgentType.AMBASSADOR,
            
            # Agent Apprenant/Formation
            BlocType.K: AgentType.LEARNER,
            BlocType.M: AgentType.LEARNER,
            
            # Agent Prospect
            BlocType.H: AgentType.PROSPECT,
            BlocType.I1: AgentType.PROSPECT,
            BlocType.I2: AgentType.PROSPECT,
            
            # Agent Paiement
            BlocType.A: AgentType.PAYMENT,
            BlocType.F: AgentType.PAYMENT,
            BlocType.J: AgentType.PAYMENT,
            BlocType.L: AgentType.PAYMENT,
            
            # Agent CPF Bloqué
            BlocType.C: AgentType.CPF_BLOCKED,
            BlocType.F1: AgentType.CPF_BLOCKED,
            BlocType.F2: AgentType.CPF_BLOCKED,
            BlocType.F3: AgentType.CPF_BLOCKED,
            BlocType.BLOC_51: AgentType.CPF_BLOCKED,
            BlocType.BLOC_52: AgentType.CPF_BLOCKED,
            BlocType.BLOC_53: AgentType.CPF_BLOCKED,
            BlocType.BLOC_54: AgentType.CPF_BLOCKED,
            
            # Agent Qualité
            BlocType.AGRO: AgentType.QUALITY,
            BlocType.LEGAL: AgentType.QUALITY,
            BlocType.BLOC_61: AgentType.QUALITY,
            BlocType.BLOC_62: AgentType.QUALITY,
        }
    
    async def orchestrate(self, message: str, session_id: str) -> OrchestrationResult:
        """Orchestre le traitement d'un message"""
        start_time = time.time()
        
        try:
            # 1. Récupérer le contexte de session
            session_context = self._get_session_context(session_id)
            
            # 2. Ajouter le message à l'historique
            self.memory_store.add_message(session_id, message, "user")
            
            # 3. Détecter le bloc approprié
            bloc_type = await self._determine_bloc(message, session_context)
            
            # 4. Déterminer l'agent
            agent_type = self._determine_agent(bloc_type)
            
            # 5. Créer le contexte de réponse
            response_context = self.detection_engine.create_response_context(
                bloc_type, message, session_context
            )
            
            # 6. Enregistrer les informations
            self._record_orchestration_data(session_id, bloc_type, agent_type, response_context)
            
            # 7. Créer le résultat
            result = OrchestrationResult(
                bloc_type=bloc_type,
                agent_type=agent_type,
                bloc_id=bloc_type.value,
                should_escalate=response_context["should_escalate"],
                escalation_type=response_context.get("escalation_type"),
                priority_level=response_context["priority_level"],
                profile=response_context["profile"],
                financing_type=response_context["financing_type"],
                context_data=response_context,
                processing_time=time.time() - start_time
            )
            
            logger.info(f"Orchestration terminée pour session {session_id}: {bloc_type.value} -> {agent_type.value}")
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors de l'orchestration pour session {session_id}: {e}")
            # Retourner un résultat de fallback
            return OrchestrationResult(
                bloc_type=BlocType.GENERAL,
                agent_type=AgentType.GENERAL,
                bloc_id=BlocType.GENERAL.value,
                should_escalate=False,
                priority_level="LOW",
                processing_time=time.time() - start_time
            )
    
    def _get_session_context(self, session_id: str) -> Dict[str, Any]:
        """Récupère le contexte de session"""
        return self.memory_store.get_session_context(session_id)
    
    async def _determine_bloc(self, message: str, session_context: Dict[str, Any]) -> BlocType:
        """Détermine le bloc approprié selon la logique V2"""
        
        # 1. Vérifier le contexte de suivi
        follow_up_bloc = self.detection_engine.detect_follow_up_context(message, session_context)
        if follow_up_bloc:
            logger.info(f"Contexte de suivi détecté: {follow_up_bloc.value}")
            return follow_up_bloc
        
        # 2. Détection du bloc principal
        primary_bloc = self.detection_engine.detect_primary_bloc(message, session_context)
        
        # 3. Validation de la séquence
        last_bloc = session_context.get("last_bloc")
        if last_bloc:
            # Convertir le string en BlocType pour la validation
            try:
                last_bloc_type = BlocType(last_bloc)
                if not self.detection_engine.validate_bloc_sequence(primary_bloc, last_bloc_type):
                    logger.warning(f"Séquence de blocs invalide: {last_bloc} -> {primary_bloc.value}")
                    # Retourner le bloc général en cas de séquence invalide
                    return BlocType.GENERAL
            except ValueError:
                logger.warning(f"Bloc précédent invalide: {last_bloc}")
        
        return primary_bloc
    
    def _determine_agent(self, bloc_type: BlocType) -> AgentType:
        """Détermine l'agent approprié pour un bloc"""
        return self.bloc_agent_mapping.get(bloc_type, AgentType.GENERAL)
    
    def _record_orchestration_data(self, session_id: str, bloc_type: BlocType, 
                                 agent_type: AgentType, context: Dict[str, Any]) -> None:
        """Enregistre les données d'orchestration"""
        
        # Enregistrer le bloc présenté
        self.memory_store.add_bloc_presented(session_id, bloc_type.value)
        
        # Enregistrer l'agent utilisé
        self.memory_store.add_agent_used(session_id, agent_type.value)
        
        # Enregistrer le profil si détecté
        if context.get("profile") and context["profile"] != "unknown":
            self.memory_store.set_session_profile(session_id, context["profile"])
        
        # Enregistrer le contexte de paiement si pertinent
        if bloc_type == BlocType.A and "payment_context" in context:
            payment_ctx = context["payment_context"]
            self.memory_store.set_payment_context(
                session_id,
                payment_ctx["financing_type"],
                payment_ctx["time_info"],
                payment_ctx["total_days"]
            )
        
        # Marquer comme escaladé si nécessaire
        if context.get("should_escalate"):
            self.memory_store.mark_session_escalated(session_id)
    
    def get_agent_specialization(self, agent_type: AgentType) -> str:
        """Retourne la spécialisation d'un agent"""
        specializations = {
            AgentType.GENERAL: "Accueil et orientation générale JAK Company",
            AgentType.AMBASSADOR: "Programme ambassadeur et processus d'affiliation",
            AgentType.LEARNER: "Catalogue formations et processus d'inscription",
            AgentType.PROSPECT: "Qualification prospects et devis commerciaux",
            AgentType.PAYMENT: "Suivi paiements, factures et délais",
            AgentType.CPF_BLOCKED: "Déblocage dossiers CPF et OPCO",
            AgentType.QUALITY: "Contrôle qualité, escalades et gestion conflits"
        }
        return specializations.get(agent_type, "Spécialisation non définie")
    
    def get_bloc_instructions(self, bloc_type: BlocType) -> str:
        """Retourne les instructions spécifiques pour un bloc"""
        instructions = {
            BlocType.A: "Gestion paiement - Vérifier délais et type de financement",
            BlocType.B1: "Découverte programme affiliation - Présenter les avantages",
            BlocType.B2: "Explication affiliation - Définir le rôle d'ambassadeur",
            BlocType.C: "Question CPF - Expliquer le processus de financement",
            BlocType.D1: "Devenir ambassadeur - Présenter les 4 étapes",
            BlocType.D2: "Définition ambassadeur - Expliquer le concept",
            BlocType.E: "Processus ambassadeur - Détail des étapes",
            BlocType.F: "Paiement formation - Suivi des factures",
            BlocType.F1: "CPF bloqué - Filtrage et diagnostic",
            BlocType.F2: "CPF dossier bloqué - Processus de déblocage",
            BlocType.F3: "OPCO - Gestion des dossiers OPCO",
            BlocType.G: "Contact humain - Orientation vers conseiller",
            BlocType.H: "Comprendre offres - Présentation catalogue",
            BlocType.K: "Formations disponibles - Catalogue complet",
            BlocType.L: "Délai dépassé - Vérification et escalade",
            BlocType.M: "Après choix formation - Processus d'inscription",
            BlocType.AGRO: "Comportement agressif - Gestion ferme mais bienveillante",
            BlocType.LEGAL: "Aspects légaux - Orientation juridique",
            BlocType.GENERAL: "Accueil général - Orientation JAK Company"
        }
        return instructions.get(bloc_type, "Instructions non définies")
    
    def get_escalation_instructions(self, escalation_type: str) -> str:
        """Retourne les instructions d'escalade"""
        instructions = {
            "admin": "Escalade administrative - Contact responsable technique",
            "commercial": "Escalade commerciale - Contact conseiller commercial",
            "quality": "Escalade qualité - Gestion comportement agressif",
            "cpf_specialist": "Escalade CPF - Contact spécialiste CPF/OPCO",
            "general": "Escalade générale - Contact support"
        }
        return instructions.get(escalation_type, "Instructions d'escalade non définies")
    
    def get_orchestration_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques d'orchestration"""
        memory_stats = self.memory_store.get_stats()
        
        stats = {
            "orchestrator_version": "V2",
            "detection_engine": "DetectionEngineV2",
            "memory_store": "OptimizedMemoryStoreV2",
            "total_blocs_mapped": len(self.bloc_agent_mapping),
            "total_agents": len(AgentType),
            "memory_stats": memory_stats,
            "bloc_agent_mapping": {
                bloc.value: agent.value 
                for bloc, agent in self.bloc_agent_mapping.items()
            }
        }
        
        return stats
    
    def validate_message(self, message: str) -> Tuple[bool, Optional[str]]:
        """Valide un message entrant"""
        if not message or not message.strip():
            return False, "Message vide"
        
        if len(message.strip()) < 2:
            return False, "Message trop court"
        
        if len(message) > 1000:
            return False, "Message trop long"
        
        return True, None
    
    def cleanup_old_sessions(self) -> int:
        """Nettoie les anciennes sessions"""
        return self.memory_store.cleanup_inactive_sessions()
    
    def export_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Exporte les données d'une session"""
        return self.memory_store.export_session_data(session_id)
    
    def import_session_data(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Importe les données d'une session"""
        return self.memory_store.import_session_data(session_id, data)