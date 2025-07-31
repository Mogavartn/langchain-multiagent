"""
Tests simplifiés pour la V2 - JAK Company
Version sans dépendances externes pour validation rapide
"""

import time
import logging
from typing import Dict, Any

# Configuration du logging pour les tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import des modules V2 (sans cachetools)
try:
    from bloc_config_v2 import BlocType, BLOC_KEYWORDS, PRIORITY_RULES
    logger.info("✓ bloc_config_v2 importé avec succès")
except ImportError as e:
    logger.error(f"✗ Erreur import bloc_config_v2: {e}")

try:
    from detection_engine_v2 import DetectionEngineV2, ProfileType, FinancingType
    logger.info("✓ detection_engine_v2 importé avec succès")
except ImportError as e:
    logger.error(f"✗ Erreur import detection_engine_v2: {e}")

try:
    from orchestrator_v2_simple import MultiAgentOrchestratorV2Simple as MultiAgentOrchestratorV2, AgentType
    logger.info("✓ orchestrator_v2_simple importé avec succès")
except ImportError as e:
    logger.error(f"✗ Erreur import orchestrator_v2_simple: {e}")

class SimpleTestSuiteV2:
    """Suite de tests simplifiée pour la V2"""
    
    def __init__(self):
        self.test_results = []
        self.detection_engine = None
        self.orchestrator = None
        
        # Initialiser les composants si possible
        try:
            self.detection_engine = DetectionEngineV2()
            logger.info("✓ DetectionEngineV2 initialisé")
        except Exception as e:
            logger.error(f"✗ Erreur initialisation DetectionEngineV2: {e}")
        
        try:
            self.orchestrator = MultiAgentOrchestratorV2()
            logger.info("✓ MultiAgentOrchestratorV2 initialisé")
        except Exception as e:
            logger.error(f"✗ Erreur initialisation MultiAgentOrchestratorV2: {e}")
    
    def run_all_tests(self):
        """Exécute tous les tests disponibles"""
        logger.info("=== DÉBUT DES TESTS V2 SIMPLIFIÉS ===")
        
        # Tests de configuration
        self.test_bloc_configuration()
        self.test_priority_rules()
        
        # Tests du moteur de détection (si disponible)
        if self.detection_engine:
            self.test_detection_engine()
            self.test_profile_detection()
            self.test_financing_detection()
            self.test_aggressive_behavior_detection()
        
        # Tests de l'orchestrateur (si disponible)
        if self.orchestrator:
            self.test_orchestrator()
            self.test_bloc_agent_mapping()
        
        # Tests d'intégration
        self.test_integration_scenarios()
        
        # Résumé des tests
        self.print_test_summary()
        
        logger.info("=== FIN DES TESTS V2 SIMPLIFIÉS ===")
    
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
    
    def test_orchestrator(self):
        """Test de l'orchestrateur"""
        logger.info("Test: Orchestrateur")
        
        try:
            # Test d'orchestration simple
            message = "Bonjour, je voudrais des informations"
            session_id = "test_orchestrator_1"
            
            # Simulation d'orchestration (sans async)
            result = self.orchestrator.orchestrate_sync(message, session_id)
            
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
            # Test de validation des messages
            valid_messages = [
                "Bonjour",
                "Je voudrais des informations",
                "Comment ça va ?"
            ]
            
            invalid_messages = [
                "",  # Message vide
                "A",  # Trop court
                "X" * 1001  # Trop long
            ]
            
            for message in valid_messages:
                is_valid, _ = self.orchestrator.validate_message(message)
                assert is_valid, f"Message valide rejeté: {message}"
            
            for message in invalid_messages:
                is_valid, _ = self.orchestrator.validate_message(message)
                assert not is_valid, f"Message invalide accepté: {message}"
            
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
        if total_tests > 0:
            logger.info(f"Taux de réussite: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            logger.error("\nTests échoués:")
            for test_name, result in self.test_results:
                if result != "PASS":
                    logger.error(f"  - {test_name}: {result}")
        
        logger.info("\n=== FIN DU RÉSUMÉ ===")

def test_bloc_keywords():
    """Test simple des mots-clés des blocs"""
    logger.info("=== TEST DES MOTS-CLÉS DES BLOCS ===")
    
    try:
        # Vérifier quelques blocs clés
        key_blocs = [
            BlocType.A,      # Paiement
            BlocType.AGRO,   # Agressif
            BlocType.B1,     # Affiliation
            BlocType.C,      # CPF
            BlocType.D1,     # Devenir ambassadeur
            BlocType.GENERAL # Général
        ]
        
        for bloc_type in key_blocs:
            config = BLOC_KEYWORDS.get(bloc_type)
            if config:
                keywords = config.get("keywords", [])
                description = config.get("description", "")
                logger.info(f"✓ {bloc_type.value}: {len(keywords)} mots-clés - {description}")
            else:
                logger.error(f"✗ {bloc_type.value}: Configuration manquante")
        
        logger.info("=== FIN TEST MOTS-CLÉS ===")
        
    except Exception as e:
        logger.error(f"Erreur lors du test des mots-clés: {e}")

def test_priority_structure():
    """Test de la structure des priorités"""
    logger.info("=== TEST STRUCTURE DES PRIORITÉS ===")
    
    try:
        for priority_level, blocs in PRIORITY_RULES.items():
            logger.info(f"Priorité {priority_level}: {len(blocs)} blocs")
            for bloc in blocs[:3]:  # Afficher les 3 premiers
                logger.info(f"  - {bloc.value}")
            if len(blocs) > 3:
                logger.info(f"  ... et {len(blocs) - 3} autres")
        
        logger.info("=== FIN TEST PRIORITÉS ===")
        
    except Exception as e:
        logger.error(f"Erreur lors du test des priorités: {e}")

if __name__ == "__main__":
    # Tests de base
    test_bloc_keywords()
    test_priority_structure()
    
    # Suite de tests complète
    test_suite = SimpleTestSuiteV2()
    test_suite.run_all_tests()