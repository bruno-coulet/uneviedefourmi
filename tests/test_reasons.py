#!/usr/bin/env python3
"""
Test rapide pour voir les nouvelles descriptions de complexité avec raisons
"""

import os
from main import load_antnest_from_txt
from gui import BottleneckAnalyzer

def test_complexity_with_reasons():
    """Teste la nouvelle fonction de complexité avec raisons"""
    
    print("🧪 TEST DES NOUVELLES DESCRIPTIONS DE COMPLEXITÉ")
    print("=" * 60)
    
    fourmilieres_dir = "fourmilieres"
    
    for filename in sorted(os.listdir(fourmilieres_dir)):
        if filename.endswith('.txt'):
            filepath = os.path.join(fourmilieres_dir, filename)
            try:
                antnest = load_antnest_from_txt(filepath)
                
                # Ancienne version (sans raisons)
                old_complexity = BottleneckAnalyzer.evaluate_network_complexity(antnest)
                
                # Nouvelle version (avec raisons)
                new_complexity = BottleneckAnalyzer.evaluate_network_complexity_with_reasons(antnest)
                
                print(f"\n📊 {antnest.name}")
                print(f"   Ancien: {old_complexity}")
                print(f"   Nouveau: {new_complexity}")
                
            except Exception as e:
                print(f"❌ Erreur avec {filename}: {e}")
    
    print(f"\n✅ Test terminé !")

if __name__ == "__main__":
    test_complexity_with_reasons()