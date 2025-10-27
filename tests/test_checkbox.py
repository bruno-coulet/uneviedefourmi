#!/usr/bin/env python3
"""
Script de test rapide pour tester la nouvelle checkbox des chemins
"""

import sys
import os

# Assurer que le chemin est correct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui import main

if __name__ == "__main__":
    print("🚀 Lancement de l'interface avec la nouvelle fonctionnalité de chemins")
    print("✅ Nouvelle fonctionnalité: Checkbox 'Afficher les chemins complets'")
    print("📍 Emplacement: Panneau de contrôle → Options d'affichage")
    print("🎯 Utilisation: Allez à la fin d'une animation pour voir les chemins colorés")
    print("=" * 60)
    main()