#!/usr/bin/env python3
"""
Démonstration des flèches d'animation
Test spécifique pour visualiser les flèches de déplacement
"""

from main import load_antnest_from_txt, solve_antnest
from anime import animation_simple

def demo_fleches():
    """Démonstration spécifique des flèches"""
    print("🎯 DÉMONSTRATION DES FLÈCHES DE DÉPLACEMENT")
    print("="*50)
    print("Cette démonstration montre les flèches rouges qui indiquent")
    print("le sens de déplacement des fourmis à chaque étape.")
    print("- Flèches rouges : sens de déplacement")
    print("- Étiquettes jaunes : numéro des fourmis en mouvement")
    print("- Couleur des bulles : nombre de fourmis dans chaque salle")
    print()
    
    # Fourmilière avec plusieurs étapes pour bien voir les flèches
    print("🎬 Animation de la fourmilière quatre (10 fourmis, 9 étapes)")
    print("Regardez bien les flèches rouges et les étiquettes jaunes !")
    print("Vitesse recommandée : 2-3 pour bien voir les détails")
    print()
    
    input("Appuyez sur Entrée pour commencer...")
    
    # Animation avec vitesse plus lente pour mieux voir
    animation_simple("fourmilieres/fourmiliere_quatre.txt", delay=2.5)
    
    print("\n✅ Démonstration terminée !")
    print("💡 Les flèches rouges montrent exactement où chaque fourmi se déplace")
    print("💡 Les étiquettes jaunes 'f1', 'f2', etc. identifient chaque fourmi")

if __name__ == "__main__":
    demo_fleches()