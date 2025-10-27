#!/usr/bin/env python3
"""
Script de débogage détaillé pour analyser les calculs de complexité
Se concentre sur les cas problématiques identifiés
"""

import os
from main import load_antnest_from_txt
from gui import BottleneckAnalyzer
import networkx as nx

def debug_fourmiliere(filepath):
    """Analyse détaillée d'une fourmilière avec toutes les métriques de débogage"""
    print(f"\n🔍 DÉBOGAGE DÉTAILLÉ: {os.path.basename(filepath)}")
    print("=" * 60)
    
    # Charger la fourmilière
    antnest = load_antnest_from_txt(filepath)
    
    print(f"📊 DONNÉES DE BASE:")
    print(f"   Fourmis: {antnest.ants}")
    print(f"   Salles: {list(antnest.rooms.keys())}")
    print(f"   Capacités: {antnest.rooms}")
    print(f"   Tunnels: {antnest.tubes}")
    
    # Créer le graphe pour analyse
    G = nx.Graph()
    for room, capacity in antnest.rooms.items():
        G.add_node(room, capacity=capacity)
    for tube in antnest.tubes:
        G.add_edge(tube[0], tube[1])
    
    print(f"\n🌐 GRAPHE NetworkX:")
    print(f"   Nœuds: {list(G.nodes())}")
    print(f"   Arêtes: {list(G.edges())}")
    
    # Analyse complète
    analysis = BottleneckAnalyzer.analyze_network(antnest)
    
    print(f"\n🔍 ANALYSE STRUCTURELLE:")
    print(f"   Connexion directe: {analysis.get('has_direct_path', False)}")
    print(f"   Chemins parallèles: {analysis.get('parallel_paths', 0)}")
    print(f"   Goulots détectés: {len(analysis.get('bottlenecks', []))}")
    print(f"   Liste goulots: {analysis.get('bottlenecks', [])}")
    print(f"   Ponts: {analysis.get('bridges', [])}")
    
    # Calcul étape par étape de la complexité
    print(f"\n🧮 CALCUL DE COMPLEXITÉ DÉTAILLÉ:")
    
    # Étape 1: Connexion directe
    has_direct = G.has_edge('Sv', 'Sd')
    print(f"   1. Connexion directe Sv-Sd: {has_direct}")
    if has_direct:
        print(f"      → Classification: Très Simple (override)")
        return "Très Simple"
    
    # Étape 2: Capacités
    intermediate_rooms = {room: capacity for room, capacity in antnest.rooms.items() 
                         if room not in ['Sv', 'Sd']}
    total_capacity = sum(intermediate_rooms.values()) if intermediate_rooms else 0
    ant_density = antnest.ants / max(1, total_capacity) if total_capacity > 0 else float('inf')
    
    print(f"   2. Salles intermédiaires: {intermediate_rooms}")
    print(f"   3. Capacité totale: {total_capacity}")
    print(f"   4. Ratio fourmis/capacité: {ant_density:.2f}")
    
    # Étape 3: Analyse des chemins
    try:
        all_paths = list(nx.all_simple_paths(G, 'Sv', 'Sd'))
        print(f"   5. Tous les chemins Sv→Sd: {len(all_paths)}")
        for i, path in enumerate(all_paths):
            print(f"      Chemin {i+1}: {' → '.join(path)}")
    except:
        print(f"   5. Erreur dans le calcul des chemins")
        all_paths = []
    
    # Étape 4: Goulots d'étranglement
    bottlenecks = analysis.get('bottlenecks', [])
    print(f"   6. Analyse des goulots:")
    print(f"      Nombre: {len(bottlenecks)}")
    print(f"      Détail: {bottlenecks}")
    
    # Étape 5: Calcul du score final
    complexity_score = 0
    
    # Facteur densité
    density_factor = min(ant_density * 10, 40)
    complexity_score += density_factor
    print(f"   7. Score densité: {density_factor:.1f}")
    
    # Facteur goulots
    bottleneck_factor = len(bottlenecks) * 5
    complexity_score += bottleneck_factor
    print(f"   8. Score goulots: {bottleneck_factor}")
    
    # Facteur chemins parallèles (réduction)
    parallel_paths = analysis.get('parallel_paths', 0)
    parallel_reduction = min(parallel_paths * 2, 15)
    complexity_score -= parallel_reduction
    print(f"   9. Réduction chemins parallèles: -{parallel_reduction}")
    
    # Facteur taille
    size_factor = max(0, len(intermediate_rooms) - 5) * 2
    complexity_score += size_factor
    print(f"   10. Score taille: {size_factor}")
    
    complexity_score = max(0, complexity_score)
    print(f"   11. SCORE TOTAL: {complexity_score}")
    
    # Classification
    if complexity_score <= 10:
        classification = "Très Simple"
    elif complexity_score <= 25:
        classification = "Simple"
    elif complexity_score <= 45:
        classification = "Modéré"
    elif complexity_score <= 70:
        classification = "Complexe"
    else:
        classification = "Très Complexe"
    
    print(f"   12. CLASSIFICATION: {classification}")
    
    # Comparaison avec le résultat officiel
    official_result = BottleneckAnalyzer.evaluate_network_complexity(antnest)
    print(f"   13. Résultat officiel: {official_result}")
    
    if classification != official_result:
        print(f"   ⚠️  DIFFÉRENCE DÉTECTÉE!")
    else:
        print(f"   ✅ Cohérence OK")
    
    return classification

def main():
    """Fonction principale de débogage"""
    print("🔍 SCRIPT DE DÉBOGAGE DÉTAILLÉ")
    
    # Cas problématiques identifiés
    problematic_cases = [
        "fourmilieres/fourmiliere_zero.txt",  # Pas de goulots mais "Complexe"
        "fourmilieres/fourmiliere_deux.txt",  # Connexion directe - doit être "Très Simple"
        "fourmilieres/fourmiliere_un.txt",    # Trop de "Très Complexe" ?
    ]
    
    for filepath in problematic_cases:
        if os.path.exists(filepath):
            debug_fourmiliere(filepath)
        else:
            print(f"❌ Fichier non trouvé: {filepath}")
    
    print(f"\n🎯 Débogage terminé!")

if __name__ == "__main__":
    main()