#!/usr/bin/env python3
"""
Script de démonstration pour 'Une vie de fourmi'
Montre toutes les fonctionnalités du projet
"""

import subprocess
import sys
import os
from main import load_antnest_from_txt, solve_antnest, test_all_fourmilieres

def demo_complete():
    """Démonstration complète du projet"""
    print("🐜 DÉMONSTRATION COMPLÈTE - UNE VIE DE FOURMI")
    print("="*60)
    
    print("\n1. 📋 ANALYSE DE TOUTES LES FOURMILIÈRES")
    print("-"*50)
    results = test_all_fourmilieres()
    
    print("\n2. 🎯 EXEMPLE DÉTAILLÉ - Fourmilière quatre")
    print("-"*50)
    antnest = load_antnest_from_txt("fourmilieres/fourmiliere_quatre.txt")
    colony = solve_antnest(antnest)
    colony.print_solution()
    
    print("\n3. 🎬 ANIMATIONS DISPONIBLES")
    print("-"*50)
    print("• Animation temps réel (anime.py)")
    print("• Animation pas à pas (animation.py)")
    print("• Interface graphique interactive (main.py)")
    
    print("\n4. 💡 UTILISATION RECOMMANDÉE")
    print("-"*50)
    print("Pour l'expérience complète :")
    print("  uv run python main.py")
    print("  → Choisir option 1 (Animation)")
    print("  → Sélectionner une fourmilière")
    print("  → Choisir le type d'animation")
    
    print("\n✅ Démonstration terminée !")

def quick_demo():
    """Démonstration rapide"""
    print("🐜 DÉMONSTRATION RAPIDE")
    print("="*30)
    
    # Test simple
    antnest = load_antnest_from_txt("fourmilieres/fourmiliere_zero.txt")
    colony = solve_antnest(antnest)
    print(f"✅ {antnest.name}: {antnest.ants} fourmis en {len(colony.movements_history)} étapes")
    
    antnest = load_antnest_from_txt("fourmilieres/fourmiliere_quatre.txt")
    colony = solve_antnest(antnest)
    print(f"✅ {antnest.name}: {antnest.ants} fourmis en {len(colony.movements_history)} étapes")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        quick_demo()
    else:
        demo_complete()