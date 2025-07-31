"""
Tests pour la V2 - JAK Company
Validation des composants V2 optimisés
"""

import asyncio
import time
import logging
from typing import Dict, Any

from bloc_config_v2 import BlocType, BLOC_KEYWORDS, PRIORITY_RULES
from detection_engine_v2 import DetectionEngineV2, ProfileType, FinancingType
from memory_store_v2 import OptimizedMemoryStoreV2
from orchestrator_v2 import MultiAgentOrchestratorV2, AgentType

# Configuration du logging pour les tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestSuiteV2:
    """Suite de tests pour la V2"""
    
    def __init__(self):
        self.detection_engine = DetectionEngineV2()
        self.memory_store = OptimizedMemoryStoreV2()
        self.orchestrator = MultiAgentOrchestratorV2()
        self.test_results = []
    
    def run_all_tests(self):
        """Exécute tous les tests"""
        logger.info("=== DÉBUT DES TESTS V2 ===")
        
        # Tests de configuration
        self.test_bloc_configuration()
        self.test_priority_rules()
        
        # Tests du moteur de détection
        self.test_detection_engine()
        self.test_profile_detection()
        self.test_financing_detection()
        self.test_aggressive_behavior_detection()
        
        # Tests du store de mémoire
        self.test_memory_store()
        self.test_session_management()
        
        # Tests de l'orchestrateur
        self.test_orchestrator()
        self.test_bloc_agent_mapping()
        
        # Tests d'intégration
        self.test_integration_scenarios()
        
        # Résumé des tests
        self.print_test_summary()
        
        logger.info("=== FIN DES TESTS V2 ===")
    
    def test_bloc_configuration(self):
        """Test de la configuration des blocs"""
        logger.info("Test: Configuration des blocs")
        
        try:
            # Vérifier que tous les blocs ont des mots-clés
            for bloc_type, config in BLOC_KEYWORDS.items():
                assert "keywords" in config, f"Bloc {bloc_type.value} sans mots-clés"
                assert "description" in config, f"Bloc {bloc_type.value} sans description"
                assert len(config["keywords"]) > 0, f"Bloc {bloc_type.value} avec mots-clés vides"
            
            # Vérifier les règles de priorité
            for priority_level, blocs in PRIORITY_RULES.items():
                assert len(blocs) > 0, f"Niveau de priorité {priority_level} vide"
            
            self.test_results.append(("Configuration des blocs", "PASS"))
            logger.info("✓ Configuration des blocs: PASS")
            
        except Exception as e:
            self.test_results.append(("Configuration des blocs", f"FAIL: {e}"))
            logger.error(f"✗ Configuration des blocs: FAIL - {e}")
    
    def test_priority_rules(self):
        """Test des règles de priorité"""
        logger.info("Test: Règles de priorité")
        
        try:
            # Vérifier que les blocs critiques sont bien prioritaires
            critical_blocs = PRIORITY_RULES["CRITICAL"]
            assert BlocType.AGRO in critical_blocs, "BLOC AGRO doit être critique"
            assert BlocType.LEGAL in critical_blocs, "BLOC LEGAL doit être critique"
            assert BlocType.F1 in critical_blocs, "BLOC F1 doit être critique"
            
            self.test_results.append(("Règles de priorité", "PASS"))
            logger.info("✓ Règles de priorité: PASS")
            
        except Exception as e:
            self.test_results.append(("Règles de priorité", f"FAIL: {e}"))
            logger.error(f"✗ Règles de priorité: FAIL - {e}")
    
    def test_detection_engine(self):
        """Test du moteur de détection"""
        logger.info("Test: Moteur de détection")
        
        try:
            # Test de détection de bloc
            test_message = "Je n'ai pas été payé depuis 3 mois"
            bloc_type = self.detection_engine.detect_primary_bloc(test_message)
            assert bloc_type == BlocType.A, f"Attendu BLOC A, obtenu {bloc_type.value}"
            
            # Test de détection agressive
            aggressive_message = "Vous êtes nuls, je suis énervé"
            is_aggressive = self.detection_engine.detect_aggressive_behavior(aggressive_message)
            assert is_aggressive, "Comportement agressif non détecté"
            
            self.test_results.append(("Moteur de détection", "PASS"))
            logger.info("✓ Moteur de détection: PASS")
            
        except Exception as e:
            self.test_results.append(("Moteur de détection", f"FAIL: {e}"))
            logger.error(f"✗ Moteur de détection: FAIL - {e}")
    
    def test_profile_detection(self):
        """Test de détection de profil"""
        logger.info("Test: Détection de profil")
        
        try:
            # Test ambassadeur
            ambassador_message = "Je veux devenir ambassadeur"
            profile = self.detection_engine.detect_profile(ambassador_message)
            assert profile == ProfileType.AMBASSADOR, f"Attendu AMBASSADOR, obtenu {profile.value}"
            
            # Test apprenant
            learner_message = "Je suis intéressé par vos formations"
            profile = self.detection_engine.detect_profile(learner_message)
            assert profile == ProfileType.LEARNER_INFLUENCER, f"Attendu LEARNER, obtenu {profile.value}"
            
            # Test prospect
            prospect_message = "Je voudrais un devis"
            profile = self.detection_engine.detect_profile(prospect_message)
            assert profile == ProfileType.PROSPECT, f"Attendu PROSPECT, obtenu {profile.value}"
            
            self.test_results.append(("Détection de profil", "PASS"))
            logger.info("✓ Détection de profil: PASS")
            
        except Exception as e:
            self.test_results.append(("Détection de profil", f"FAIL: {e}"))
            logger.error(f"✗ Détection de profil: FAIL - {e}")
    
    def test_financing_detection(self):
        """Test de détection de financement"""
        logger.info("Test: Détection de financement")
        
        try:
            # Test CPF
            cpf_message = "Je veux utiliser mon CPF"
            financing = self.detection_engine.detect_financing_type(cpf_message)
            assert financing == FinancingType.CPF, f"Attendu CPF, obtenu {financing.value}"
            
            # Test OPCO
            opco_message = "Mon OPCO peut-il financer"
            financing = self.detection_engine.detect_financing_type(opco_message)
            assert financing == FinancingType.OPCO, f"Attendu OPCO, obtenu {financing.value}"
            
            # Test direct
            direct_message = "Je veux payer directement"
            financing = self.detection_engine.detect_financing_type(direct_message)
            assert financing == FinancingType.DIRECT, f"Attendu DIRECT, obtenu {financing.value}"
            
            self.test_results.append(("Détection de financement", "PASS"))
            logger.info("✓ Détection de financement: PASS")
            
        except Exception as e:
            self.test_results.append(("Détection de financement", f"FAIL: {e}"))
            logger.error(f"✗ Détection de financement: FAIL - {e}")
    
    def test_aggressive_behavior_detection(self):
        """Test de détection de comportement agressif"""
        logger.info("Test: Détection comportement agressif")
        
        try:
            # Test positif
            aggressive_messages = [
                "Vous êtes nuls",
                "Je suis énervé",
                "C'est de la merde",
                "Vous êtes incompétents"
            ]
            
            for message in aggressive_messages:
                is_aggressive = self.detection_engine.detect_aggressive_behavior(message)
                assert is_aggressive, f"Comportement agressif non détecté: {message}"
            
            # Test négatif
            normal_messages = [
                "Bonjour, comment allez-vous ?",
                "Je voudrais des informations",
                "Merci pour votre aide"
            ]
            
            for message in normal_messages:
                is_aggressive = self.detection_engine.detect_aggressive_behavior(message)
                assert not is_aggressive, f"Faux positif pour comportement agressif: {message}"
            
            self.test_results.append(("Détection comportement agressif", "PASS"))
            logger.info("✓ Détection comportement agressif: PASS")
            
        except Exception as e:
            self.test_results.append(("Détection comportement agressif", f"FAIL: {e}"))
            logger.error(f"✗ Détection comportement agressif: FAIL - {e}")
    
    def test_memory_store(self):
        """Test du store de mémoire"""
        logger.info("Test: Store de mémoire")
        
        try:
            session_id = "test_session_1"
            
            # Test création de session
            session = self.memory_store.get_or_create_session(session_id)
            assert session.session_id == session_id
            assert session.status.value == "active"
            
            # Test ajout de message
            self.memory_store.add_message(session_id, "Test message", "user")
            messages = self.memory_store.get_messages(session_id)
            assert len(messages) == 1
            assert messages[0].content == "Test message"
            
            # Test ajout de bloc
            self.memory_store.add_bloc_presented(session_id, "BLOC A")
            last_bloc = self.memory_store.get_last_bloc(session_id)
            assert last_bloc == "BLOC A"
            
            # Test statistiques
            stats = self.memory_store.get_stats()
            assert "total_sessions" in stats
            assert stats["total_sessions"] > 0
            
            self.test_results.append(("Store de mémoire", "PASS"))
            logger.info("✓ Store de mémoire: PASS")
            
        except Exception as e:
            self.test_results.append(("Store de mémoire", f"FAIL: {e}"))
            logger.error(f"✗ Store de mémoire: FAIL - {e}")
    
    def test_session_management(self):
        """Test de gestion des sessions"""
        logger.info("Test: Gestion des sessions")
        
        try:
            session_id = "test_session_2"
            
            # Test contexte de session
            context = self.memory_store.get_session_context(session_id)
            assert "session" in context
            assert "last_bloc" in context
            assert "recent_blocs" in context
            
            # Test export/import
            self.memory_store.add_message(session_id, "Message test", "user")
            self.memory_store.add_bloc_presented(session_id, "BLOC B")
            
            exported_data = self.memory_store.export_session_data(session_id)
            assert exported_data is not None
            
            # Nettoyer et réimporter
            self.memory_store.clear_session(session_id)
            success = self.memory_store.import_session_data(session_id, exported_data)
            assert success
            
            # Vérifier que les données sont restaurées
            messages = self.memory_store.get_messages(session_id)
            assert len(messages) == 1
            
            self.test_results.append(("Gestion des sessions", "PASS"))
            logger.info("✓ Gestion des sessions: PASS")
            
        except Exception as e:
            self.test_results.append(("Gestion des sessions", f"FAIL: {e}"))
            logger.error(f"✗ Gestion des sessions: FAIL - {e}")
    
    def test_orchestrator(self):
        """Test de l'orchestrateur"""
        logger.info("Test: Orchestrateur")
        
        try:
            # Test d'orchestration simple
            message = "Bonjour, je voudrais des informations"
            session_id = "test_orchestrator_1"
            
            result = asyncio.run(self.orchestrator.orchestrate(message, session_id))
            
            assert result.bloc_type is not None
            assert result.agent_type is not None
            assert result.bloc_id is not None
            assert result.processing_time > 0
            
            self.test_results.append(("Orchestrateur", "PASS"))
            logger.info("✓ Orchestrateur: PASS")
            
        except Exception as e:
            self.test_results.append(("Orchestrateur", f"FAIL: {e}"))
            logger.error(f"✗ Orchestrateur: FAIL - {e}")
    
    def test_bloc_agent_mapping(self):
        """Test du mapping bloc -> agent"""
        logger.info("Test: Mapping bloc -> agent")
        
        try:
            # Vérifier que tous les blocs ont un agent assigné
            for bloc_type in BlocType:
                agent_type = self.orchestrator.bloc_agent_mapping.get(bloc_type)
                assert agent_type is not None, f"Bloc {bloc_type.value} sans agent assigné"
                assert isinstance(agent_type, AgentType), f"Agent invalide pour {bloc_type.value}"
            
            # Vérifier des mappings spécifiques
            assert self.orchestrator.bloc_agent_mapping[BlocType.A] == AgentType.PAYMENT
            assert self.orchestrator.bloc_agent_mapping[BlocType.AGRO] == AgentType.QUALITY
            assert self.orchestrator.bloc_agent_mapping[BlocType.B1] == AgentType.AMBASSADOR
            
            self.test_results.append(("Mapping bloc -> agent", "PASS"))
            logger.info("✓ Mapping bloc -> agent: PASS")
            
        except Exception as e:
            self.test_results.append(("Mapping bloc -> agent", f"FAIL: {e}"))
            logger.error(f"✗ Mapping bloc -> agent: FAIL - {e}")
    
    def test_integration_scenarios(self):
        """Test de scénarios d'intégration"""
        logger.info("Test: Scénarios d'intégration")
        
        try:
            # Scénario 1: Utilisateur agressif
            session_id = "test_integration_1"
            aggressive_message = "Vous êtes nuls, je suis très énervé"
            
            result = asyncio.run(self.orchestrator.orchestrate(aggressive_message, session_id))
            assert result.bloc_type == BlocType.AGRO
            assert result.agent_type == AgentType.QUALITY
            assert result.should_escalate
            
            # Scénario 2: Question de paiement
            session_id = "test_integration_2"
            payment_message = "Je n'ai pas été payé depuis 2 mois"
            
            result = asyncio.run(self.orchestrator.orchestrate(payment_message, session_id))
            assert result.bloc_type == BlocType.A
            assert result.agent_type == AgentType.PAYMENT
            assert result.priority_level in ["HIGH", "CRITICAL"]
            
            # Scénario 3: Demande d'ambassadeur
            session_id = "test_integration_3"
            ambassador_message = "Je veux devenir ambassadeur"
            
            result = asyncio.run(self.orchestrator.orchestrate(ambassador_message, session_id))
            assert result.bloc_type == BlocType.D1
            assert result.agent_type == AgentType.AMBASSADOR
            
            self.test_results.append(("Scénarios d'intégration", "PASS"))
            logger.info("✓ Scénarios d'intégration: PASS")
            
        except Exception as e:
            self.test_results.append(("Scénarios d'intégration", f"FAIL: {e}"))
            logger.error(f"✗ Scénarios d'intégration: FAIL - {e}")
    
    def print_test_summary(self):
        """Affiche le résumé des tests"""
        logger.info("\n=== RÉSUMÉ DES TESTS ===")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for _, result in self.test_results if result == "PASS")
        failed_tests = total_tests - passed_tests
        
        logger.info(f"Total des tests: {total_tests}")
        logger.info(f"Tests réussis: {passed_tests}")
        logger.info(f"Tests échoués: {failed_tests}")
        logger.info(f"Taux de réussite: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            logger.error("\nTests échoués:")
            for test_name, result in self.test_results:
                if result != "PASS":
                    logger.error(f"  - {test_name}: {result}")
        
        logger.info("\n=== FIN DU RÉSUMÉ ===")

def run_performance_test():
    """Test de performance"""
    logger.info("=== TEST DE PERFORMANCE ===")
    
    orchestrator = MultiAgentOrchestratorV2()
    
    # Messages de test
    test_messages = [
        "Bonjour, comment allez-vous ?",
        "Je n'ai pas été payé depuis 3 mois",
        "Je veux devenir ambassadeur",
        "Vous êtes nuls, je suis énervé",
        "Je voudrais utiliser mon CPF",
        "Quelles sont vos formations disponibles ?",
        "Je voudrais un devis",
        "Comment fonctionne l'affiliation ?"
    ]
    
    session_id = "perf_test_session"
    total_time = 0
    results = []
    
    for i, message in enumerate(test_messages):
        start_time = time.time()
        result = asyncio.run(orchestrator.orchestrate(message, session_id))
        end_time = time.time()
        
        processing_time = end_time - start_time
        total_time += processing_time
        
        results.append({
            "message": message[:30] + "...",
            "bloc": result.bloc_id,
            "agent": result.agent_type.value,
            "time": processing_time
        })
        
        logger.info(f"Message {i+1}: {result.bloc_id} -> {result.agent_type.value} ({processing_time:.3f}s)")
    
    avg_time = total_time / len(test_messages)
    logger.info(f"\nTemps total: {total_time:.3f}s")
    logger.info(f"Temps moyen par message: {avg_time:.3f}s")
    logger.info(f"Messages par seconde: {1/avg_time:.1f}")
    
    return results

if __name__ == "__main__":
    # Exécuter les tests
    test_suite = TestSuiteV2()
    test_suite.run_all_tests()
    
    # Exécuter le test de performance
    run_performance_test()