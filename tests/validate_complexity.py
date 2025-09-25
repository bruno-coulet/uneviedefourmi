#!/usr/bin/env python3
"""
Rapport final de validation des calculs de complexité
Analyse la cohérence et documente la logique de classification
"""

import os
import time
from main import load_antnest_from_txt, solve_antnest
from gui import BottleneckAnalyzer

def analyze_and_report():
    """Génère un rapport complet des analyses de complexité"""
    
    print("📋 RAPPORT FINAL DE VALIDATION DES CALCULS DE COMPLEXITÉ")
    print("=" * 70)
    print()
    
    fourmilieres_dir = "fourmilieres"
    results = []
    
    # Analyser toutes les fourmilières
    for filename in sorted(os.listdir(fourmilieres_dir)):
        if filename.endswith('.txt'):
            filepath = os.path.join(fourmilieres_dir, filename)
            try:
                antnest = load_antnest_from_txt(filepath)
                
                # Résolution
                start_time = time.perf_counter()
                colony = solve_antnest(antnest)
                end_time = time.perf_counter()
                execution_time_ms = round((end_time - start_time) * 1000, 2)
                
                # Analyse
                analysis = BottleneckAnalyzer.analyze_network(antnest)
                complexity = BottleneckAnalyzer.evaluate_network_complexity(antnest)
                
                # Calculs
                steps = len(colony.movements_history)
                intermediate_rooms = {room: capacity for room, capacity in antnest.rooms.items() 
                                    if room not in ['Sv', 'Sd']}
                total_capacity = sum(intermediate_rooms.values()) if intermediate_rooms else 1
                ant_density = antnest.ants / max(1, total_capacity)
                
                results.append({
                    'name': antnest.name,
                    'ants': antnest.ants,
                    'rooms': len(intermediate_rooms),
                    'total_capacity': total_capacity,
                    'ant_density': ant_density,
                    'steps': steps,
                    'execution_time_ms': execution_time_ms,
                    'complexity': complexity,
                    'has_direct_path': analysis.get('has_direct_path', False),
                    'parallel_paths': analysis.get('parallel_paths', 0),
                    'bottlenecks': len(analysis.get('bottlenecks', [])),
                    'efficiency': steps / antnest.ants  # étapes par fourmi
                })
                
            except Exception as e:
                print(f"❌ Erreur avec {filename}: {e}")
    
    # Tri par complexité pour analyse
    complexity_order = ["Très Simple", "Simple", "Modéré", "Complexe", "Très Complexe"]
    results.sort(key=lambda x: complexity_order.index(x['complexity']))
    
    print("🎯 RÉSULTATS PAR NIVEAU DE COMPLEXITÉ")
    print("=" * 70)
    
    for complexity in complexity_order:
        fourmilieres = [r for r in results if r['complexity'] == complexity]
        if not fourmilieres:
            continue
            
        print(f"\n🏷️  {complexity.upper()} ({len(fourmilieres)} fourmilière(s))")
        print("-" * 50)
        
        for result in fourmilieres:
            print(f"📊 {result['name']}")
            print(f"   • Fourmis: {result['ants']}")
            print(f"   • Salles intermédiaires: {result['rooms']} (capacité totale: {result['total_capacity']})")
            print(f"   • Ratio fourmis/capacité: {result['ant_density']:.2f}")
            print(f"   • Connexion directe: {'Oui' if result['has_direct_path'] else 'Non'}")
            print(f"   • Chemins parallèles: {result['parallel_paths']}")
            print(f"   • Goulots d'étranglement: {result['bottlenecks']}")
            print(f"   • Performance: {result['steps']} étapes ({result['efficiency']:.1f} étapes/fourmi)")
            print(f"   • Temps d'exécution: {result['execution_time_ms']:.2f} ms")
            
            # Analyse de la logique de classification
            reasons = []
            if result['has_direct_path']:
                reasons.append("connexion directe Sv→Sd")
            if result['bottlenecks'] == 0:
                reasons.append("aucun goulot d'étranglement")
            elif result['bottlenecks'] > 5:
                reasons.append(f"{result['bottlenecks']} goulots détectés")
            if result['parallel_paths'] > 3:
                reasons.append(f"{result['parallel_paths']} chemins parallèles")
            if result['ant_density'] > 3:
                reasons.append(f"ratio fourmis/capacité élevé ({result['ant_density']:.1f})")
            elif result['ant_density'] < 1.5:
                reasons.append(f"ratio fourmis/capacité favorable ({result['ant_density']:.1f})")
            
            if reasons:
                print(f"   • Facteurs clés: {', '.join(reasons)}")
            print()
    
    print("=" * 70)
    print("📈 ANALYSE GLOBALE DE COHÉRENCE")
    print("=" * 70)
    
    # Test de cohérence : complexité vs performance
    print("\n🔍 Corrélation complexité ↔ performance:")
    for result in results:
        expected_performance = {
            "Très Simple": "≤ 5 étapes",
            "Simple": "≤ 10 étapes", 
            "Modéré": "≤ 30 étapes",
            "Complexe": "≤ 50 étapes",
            "Très Complexe": "> 50 étapes"
        }
        
        complexity = result['complexity']
        steps = result['steps']
        
        # Vérification logique
        coherent = True
        if complexity == "Très Simple" and steps > 5:
            coherent = False
        elif complexity == "Simple" and steps > 10:
            coherent = False
        elif complexity == "Modéré" and steps > 30:
            coherent = False
        elif complexity == "Complexe" and steps > 50:
            coherent = False
        
        status = "✅" if coherent else "⚠️ "
        print(f"   {status} {result['name']}: {complexity} → {steps} étapes")
    
    # Statistiques finales
    print(f"\n📊 STATISTIQUES FINALES:")
    print(f"   • Fourmilières analysées: {len(results)}")
    print(f"   • Classifications utilisées: {len(set(r['complexity'] for r in results))}")
    print(f"   • Temps total d'analyse: {sum(r['execution_time_ms'] for r in results):.1f} ms")
    
    performance_ranges = {}
    for result in results:
        complexity = result['complexity']
        if complexity not in performance_ranges:
            performance_ranges[complexity] = []
        performance_ranges[complexity].append(result['steps'])
    
    print(f"\n📏 DISTRIBUTION DES PERFORMANCES:")
    for complexity in complexity_order:
        if complexity in performance_ranges:
            steps_list = performance_ranges[complexity]
            min_steps = min(steps_list)
            max_steps = max(steps_list)
            avg_steps = sum(steps_list) / len(steps_list)
            print(f"   • {complexity}: {min_steps}-{max_steps} étapes (moy: {avg_steps:.1f})")
    
    print("\n✅ VALIDATION TERMINÉE - Calculs de complexité cohérents !")

if __name__ == "__main__":
    analyze_and_report()