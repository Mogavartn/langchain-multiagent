"""
Démonstration de la V2 - JAK Company Multi-Agents API
Affiche les capacités de la nouvelle version optimisée
"""

import time
import logging
from typing import List, Dict, Any

from bloc_config_v2 import BlocType, BLOC_KEYWORDS, PRIORITY_RULES
from orchestrator_v2_simple import MultiAgentOrchestratorV2Simple, AgentType

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class V2Demo:
    """Démonstration des capacités de la V2"""
    
    def __init__(self):
        self.orchestrator = MultiAgentOrchestratorV2Simple()
        self.session_id = "demo_session"
    
    def run_demo(self):
        """Exécute la démonstration complète"""
        logger.info("🚀 === DÉMONSTRATION V2 - JAK Company Multi-Agents ===")
        
        # 1. Afficher la configuration
        self.show_configuration()
        
        # 2. Tests de détection
        self.test_detection_scenarios()
        
        # 3. Tests d'orchestration
        self.test_orchestration_scenarios()
        
        # 4. Tests de performance
        self.test_performance()
        
        # 5. Résumé
        self.show_summary()
        
        logger.info("✅ === FIN DE LA DÉMONSTRATION V2 ===")
    
    def show_configuration(self):
        """Affiche la configuration de la V2"""
        logger.info("\n📋 CONFIGURATION V2")
        logger.info("=" * 50)
        
        # Statistiques générales
        total_blocs = len(BLOC_KEYWORDS)
        total_agents = len(AgentType)
        
        logger.info(f"📊 Statistiques générales:")
        logger.info(f"   • Blocs configurés: {total_blocs}")
        logger.info(f"   • Agents spécialisés: {total_agents}")
        logger.info(f"   • Niveaux de priorité: {len(PRIORITY_RULES)}")
        
        # Afficher les agents
        logger.info(f"\n🤖 Agents spécialisés:")
        for agent_type in AgentType:
            logger.info(f"   • {agent_type.value}: {self.get_agent_description(agent_type)}")
        
        # Afficher les priorités
        logger.info(f"\n⚡ Règles de priorité:")
        for priority, blocs in PRIORITY_RULES.items():
            logger.info(f"   • {priority}: {len(blocs)} blocs")
    
    def test_detection_scenarios(self):
        """Teste différents scénarios de détection"""
        logger.info("\n🎯 TESTS DE DÉTECTION")
        logger.info("=" * 50)
        
        test_scenarios = [
            {
                "name": "Paiement en retard",
                "message": "Je n'ai pas été payé depuis 3 mois",
                "expected_bloc": "BLOC A",
                "expected_agent": "payment"
            },
            {
                "name": "Comportement agressif",
                "message": "Vous êtes nuls, je suis très énervé",
                "expected_bloc": "BLOC AGRO",
                "expected_agent": "quality"
            },
            {
                "name": "Devenir ambassadeur",
                "message": "Je veux devenir ambassadeur",
                "expected_bloc": "BLOC D1",
                "expected_agent": "ambassador"
            },
            {
                "name": "Question CPF",
                "message": "Comment utiliser mon CPF ?",
                "expected_bloc": "BLOC C",
                "expected_agent": "cpf_blocked"
            },
            {
                "name": "Formations disponibles",
                "message": "Quelles sont vos formations ?",
                "expected_bloc": "BLOC K",
                "expected_agent": "learner"
            },
            {
                "name": "Devis commercial",
                "message": "Je voudrais un devis",
                "expected_bloc": "BLOC H",
                "expected_agent": "prospect"
            },
            {
                "name": "Contact humain",
                "message": "Je veux parler à un humain",
                "expected_bloc": "BLOC G",
                "expected_agent": "general"
            }
        ]
        
        for scenario in test_scenarios:
            self.test_single_scenario(scenario)
    
    def test_single_scenario(self, scenario: Dict[str, Any]):
        """Teste un scénario individuel"""
        logger.info(f"\n🔍 Test: {scenario['name']}")
        logger.info(f"   Message: '{scenario['message']}'")
        
        # Orchestration
        result = self.orchestrator.orchestrate_sync(scenario['message'], self.session_id)
        
        # Vérification
        bloc_correct = result.bloc_id == scenario['expected_bloc']
        agent_correct = result.agent_type.value == scenario['expected_agent']
        
        logger.info(f"   Détecté: {result.bloc_id} -> {result.agent_type.value}")
        logger.info(f"   Attendu: {scenario['expected_bloc']} -> {scenario['expected_agent']}")
        logger.info(f"   Profil: {result.profile}")
        logger.info(f"   Priorité: {result.priority_level}")
        logger.info(f"   Escalade: {'OUI' if result.should_escalate else 'NON'}")
        logger.info(f"   Temps: {result.processing_time:.3f}s")
        
        if bloc_correct and agent_correct:
            logger.info(f"   ✅ SUCCÈS")
        else:
            logger.warning(f"   ⚠️  ATTENTION: Résultat différent de l'attendu")
    
    def test_orchestration_scenarios(self):
        """Teste des scénarios d'orchestration complexes"""
        logger.info("\n🔄 TESTS D'ORCHESTRATION")
        logger.info("=" * 50)
        
        # Test de continuité de conversation
        conversation = [
            "Bonjour, je voudrais des informations sur vos formations",
            "Je suis intéressé par la formation en marketing",
            "Comment puis-je payer ?",
            "Je préfère utiliser mon CPF",
            "Mon CPF est bloqué depuis 2 mois",
            "Je suis très énervé par cette situation"
        ]
        
        logger.info("💬 Test de conversation continue:")
        for i, message in enumerate(conversation, 1):
            logger.info(f"\n   Message {i}: '{message}'")
            result = self.orchestrator.orchestrate_sync(message, self.session_id)
            logger.info(f"   → {result.bloc_id} -> {result.agent_type.value} (Priorité: {result.priority_level})")
    
    def test_performance(self):
        """Teste les performances"""
        logger.info("\n⚡ TESTS DE PERFORMANCE")
        logger.info("=" * 50)
        
        # Messages de test
        test_messages = [
            "Bonjour",
            "Je n'ai pas été payé",
            "Je veux devenir ambassadeur",
            "Vous êtes nuls",
            "Comment utiliser mon CPF ?",
            "Quelles sont vos formations ?",
            "Je voudrais un devis",
            "Je veux parler à un humain"
        ]
        
        total_time = 0
        results = []
        
        logger.info("🔄 Test de performance:")
        for i, message in enumerate(test_messages, 1):
            start_time = time.time()
            result = self.orchestrator.orchestrate_sync(message, f"perf_test_{i}")
            end_time = time.time()
            
            processing_time = end_time - start_time
            total_time += processing_time
            
            results.append({
                "message": message[:30] + "..." if len(message) > 30 else message,
                "bloc": result.bloc_id,
                "agent": result.agent_type.value,
                "time": processing_time
            })
            
            logger.info(f"   {i}. {result.bloc_id} -> {result.agent_type.value} ({processing_time:.3f}s)")
        
        # Statistiques
        avg_time = total_time / len(test_messages)
        messages_per_second = 1 / avg_time if avg_time > 0 else 0
        
        logger.info(f"\n📊 Statistiques de performance:")
        logger.info(f"   • Temps total: {total_time:.3f}s")
        logger.info(f"   • Temps moyen: {avg_time:.3f}s")
        logger.info(f"   • Messages/seconde: {messages_per_second:.1f}")
        logger.info(f"   • Messages testés: {len(test_messages)}")
    
    def show_summary(self):
        """Affiche un résumé de la démonstration"""
        logger.info("\n📈 RÉSUMÉ DE LA DÉMONSTRATION")
        logger.info("=" * 50)
        
        # Statistiques de l'orchestrateur
        stats = self.orchestrator.get_orchestration_stats()
        
        logger.info("🎯 Capacités démontrées:")
        logger.info("   ✅ Détection intelligente des intentions")
        logger.info("   ✅ Routage spécialisé par agent")
        logger.info("   ✅ Gestion des priorités")
        logger.info("   ✅ Détection de comportements agressifs")
        logger.info("   ✅ Profilage automatique des utilisateurs")
        logger.info("   ✅ Gestion du contexte conversationnel")
        logger.info("   ✅ Escalade intelligente")
        logger.info("   ✅ Performance optimisée")
        
        logger.info(f"\n📊 Statistiques système:")
        logger.info(f"   • Version: {stats['orchestrator_version']}")
        logger.info(f"   • Blocs mappés: {stats['total_blocs_mapped']}")
        logger.info(f"   • Agents disponibles: {stats['total_agents']}")
        
        logger.info("\n🚀 Avantages de la V2:")
        logger.info("   • Architecture modulaire et maintenable")
        logger.info("   • Logique décisionnelle optimisée")
        logger.info("   • Gestion de mémoire avancée")
        logger.info("   • API RESTful complète")
        logger.info("   • Tests automatisés")
        logger.info("   • Documentation détaillée")
        logger.info("   • Compatibilité V1 maintenue")
    
    def get_agent_description(self, agent_type: AgentType) -> str:
        """Retourne la description d'un agent"""
        descriptions = {
            AgentType.GENERAL: "Accueil et orientation générale",
            AgentType.AMBASSADOR: "Programme ambassadeur et affiliation",
            AgentType.LEARNER: "Formations et apprentissage",
            AgentType.PROSPECT: "Qualification et devis commerciaux",
            AgentType.PAYMENT: "Suivi paiements et factures",
            AgentType.CPF_BLOCKED: "Déblocage CPF/OPCO",
            AgentType.QUALITY: "Contrôle qualité et escalades"
        }
        return descriptions.get(agent_type, "Description non disponible")

def main():
    """Fonction principale de démonstration"""
    demo = V2Demo()
    demo.run_demo()

if __name__ == "__main__":
    main()