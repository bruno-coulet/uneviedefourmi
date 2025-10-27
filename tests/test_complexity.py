#!/usr/bin/env python3
"""
Script de test pour vérifier la cohérence du calcul de complexité des fourmilières
Analyse toutes les fourmilières et compare les résultats avec les données réelles
"""

import os
import time
from main import load_antnest_from_txt, solve_antnest
from gui import BottleneckAnalyzer

def analyze_fourmiliere(filepath):
    """Analyse une fourmilière et retourne toutes les métriques"""
    try:
        # Charger la fourmilière
        antnest = load_antnest_from_txt(filepath)
        
        # Résoudre avec mesure du temps
        start_time = time.perf_counter()
        colony = solve_antnest(antnest)
        end_time = time.perf_counter()
        
        execution_time_ms = round((end_time - start_time) * 1000, 2)
        
        # Analyse structurelle
        analysis = BottleneckAnalyzer.analyze_network(antnest)
        complexity = BottleneckAnalyzer.evaluate_network_complexity(antnest)
        
        # Extraction des données réelles
        steps = len(colony.movements_history)
        
        # Calcul des capacités réelles
        room_capacities = {}
        for room, capacity in antnest.rooms.items():
            if room not in ['Sv', 'Sd']:
                room_capacities[room] = capacity
        
        total_capacity = sum(room_capacities.values()) if room_capacities else 0
        avg_capacity = total_capacity / len(room_capacities) if room_capacities else 0
        
        return {
            'name': antnest.name,
            'filepath': filepath,
            'ants': antnest.ants,
            'rooms': len(antnest.rooms),
            'tunnels': len(antnest.tubes),
            'steps': steps,
            'execution_time_ms': execution_time_ms,
            'complexity': complexity,
            'has_direct_path': analysis.get('has_direct_path', False),
            'parallel_paths': analysis.get('parallel_paths', 0),
            'bottlenecks': len(analysis.get('bottlenecks', [])),
            'room_capacities': room_capacities,
            'total_capacity': total_capacity,
            'avg_capacity': avg_capacity,
            'ant_density': antnest.ants / max(1, total_capacity) if total_capacity > 0 else float('inf'),
            'analysis': analysis
        }
        
    except Exception as e:
        return {
            'name': filepath,
            'error': str(e)
        }

def check_complexity_coherence(data):
    """Vérifie la cohérence du calcul de complexité"""
    issues = []
    
    # Test 1: Connexion directe = Très Simple
    if data['has_direct_path'] and data['complexity'] != "Très Simple":
        issues.append(f"❌ Connexion directe détectée mais complexité = {data['complexity']}")
    
    # Test 2: 1 étape = très simple (sauf si erreur)
    if data['steps'] == 1 and data['complexity'] not in ["Très Simple", "Simple"]:
        issues.append(f"❌ 1 étape seulement mais complexité = {data['complexity']}")
    
    # Test 3: Beaucoup d'étapes = complexité élevée
    if data['steps'] > 50 and data['complexity'] in ["Très Simple", "Simple"]:
        issues.append(f"❌ {data['steps']} étapes mais complexité = {data['complexity']}")
    
    # Test 4: Ratio fourmis/capacité élevé = complexité élevée
    if data['ant_density'] > 5 and data['complexity'] in ["Très Simple", "Simple"]:
        issues.append(f"❌ Ratio fourmis/capacité = {data['ant_density']:.2f} mais complexité = {data['complexity']}")
    
    # Test 5: Pas de goulots + capacités suffisantes = pas très complexe
    if (data['bottlenecks'] == 0 and data['ant_density'] < 2 and 
        data['complexity'] in ["Très Complexe", "Complexe"]):
        issues.append(f"❌ Pas de goulots, ratio faible mais complexité = {data['complexity']}")
    
    return issues

def main():
    """Fonction principale de test"""
    print("🔍 SCRIPT DE VÉRIFICATION DE COHÉRENCE")
    print("=" * 50)
    
    fourmilieres_dir = "fourmilieres"
    results = []
    
    # Analyser toutes les fourmilières
    for filename in sorted(os.listdir(fourmilieres_dir)):
        if filename.endswith('.txt'):
            filepath = os.path.join(fourmilieres_dir, filename)
            print(f"\n📊 Analyse de {filename}...")
            
            data = analyze_fourmiliere(filepath)
            if 'error' in data:
                print(f"❌ Erreur: {data['error']}")
                continue
            
            results.append(data)
            
            # Affichage détaillé
            print(f"   Fourmis: {data['ants']}")
            print(f"   Salles: {data['rooms']} (capacités: {data['room_capacities']})")
            print(f"   Total capacité: {data['total_capacity']}")
            print(f"   Ratio fourmis/capacité: {data['ant_density']:.2f}")
            print(f"   Tunnels: {data['tunnels']}")
            print(f"   Connexion directe: {'Oui' if data['has_direct_path'] else 'Non'}")
            print(f"   Chemins parallèles: {data['parallel_paths']}")
            print(f"   Goulots: {data['bottlenecks']}")
            print(f"   Étapes réelles: {data['steps']}")
            print(f"   Temps: {data['execution_time_ms']:.2f} ms")
            print(f"   Complexité calculée: {data['complexity']}")
            
            # Vérification de cohérence
            issues = check_complexity_coherence(data)
            if issues:
                print(f"   🚨 PROBLÈMES DÉTECTÉS:")
                for issue in issues:
                    print(f"      {issue}")
            else:
                print(f"   ✅ Cohérence OK")
    
    # Résumé global
    print("\n" + "=" * 50)
    print("📈 RÉSUMÉ GLOBAL")
    print("=" * 50)
    
    complexity_counts = {}
    for data in results:
        complexity = data['complexity']
        if complexity not in complexity_counts:
            complexity_counts[complexity] = []
        complexity_counts[complexity].append(data)
    
    for complexity, fourmilieres in complexity_counts.items():
        print(f"\n🏷️  {complexity}: {len(fourmilieres)} fourmilière(s)")
        for data in fourmilieres:
            steps_per_ant = data['steps'] / data['ants']
            print(f"   • {data['name']}: {data['steps']} étapes, {steps_per_ant:.1f} étapes/fourmi")
    
    # Tests de cohérence globale
    print(f"\n🔍 TESTS DE COHÉRENCE GLOBALE:")
    
    # Test: Les "Très Simple" doivent avoir le moins d'étapes
    tres_simples = [d for d in results if d['complexity'] == "Très Simple"]
    tres_complexes = [d for d in results if d['complexity'] == "Très Complexe"]
    
    if tres_simples and tres_complexes:
        min_steps_simple = min(d['steps'] for d in tres_simples)
        max_steps_complex = max(d['steps'] for d in tres_complexes)
        
        if min_steps_simple > max_steps_complex:
            print("❌ Incohérence: 'Très Simple' a plus d'étapes que 'Très Complexe'")
        else:
            print("✅ Cohérence: 'Très Simple' ≤ étapes ≤ 'Très Complexe'")
    
    # Test: Corrélation temps vs complexité
    sorted_by_time = sorted(results, key=lambda x: x['execution_time_ms'])
    sorted_by_complexity = sorted(results, key=lambda x: ['Très Simple', 'Simple', 'Modéré', 'Complexe', 'Très Complexe'].index(x['complexity']))
    
    print(f"\n⏱️  Ordre par temps: {[d['name'] for d in sorted_by_time]}")
    print(f"🏷️  Ordre par complexité: {[d['name'] for d in sorted_by_complexity]}")
    
    print(f"\n🎯 Test terminé ! Analysé {len(results)} fourmilières.")

if __name__ == "__main__":
    main()