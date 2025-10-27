#!/usr/bin/env python3
"""
Test rapide pour vérifier l'extraction des chemins des fourmis
"""

import os
from main import load_antnest_from_txt, solve_antnest
from gui import FourmiGUI

def test_ant_paths():
    """Teste l'extraction des chemins des fourmis"""
    
    print("🧪 TEST D'EXTRACTION DES CHEMINS")
    print("=" * 40)
    
    # Test avec fourmilière simple
    filepath = "fourmilieres/fourmiliere_deux.txt"
    if os.path.exists(filepath):
        antnest = load_antnest_from_txt(filepath)
        colony = solve_antnest(antnest)
        
        print(f"\n📊 {antnest.name}")
        print(f"   Fourmis: {antnest.ants}")
        print(f"   Étapes: {len(colony.movements_history)}")
        
        print(f"\n📋 Historique des mouvements:")
        for step, movements in enumerate(colony.movements_history, 1):
            print(f"   Étape {step}: {movements}")
        
        # Tester l'extraction des chemins
        ant_paths = FourmiGUI.extract_ant_paths(colony)
        
        print(f"\n🛤️  Chemins extraits:")
        for ant_id, path in ant_paths.items():
            print(f"   f{ant_id}: {' → '.join(path)}")
        
        # Tester le regroupement
        path_groups = {}
        for ant_id, path in ant_paths.items():
            path_key = tuple(path)
            if path_key not in path_groups:
                path_groups[path_key] = []
            path_groups[path_key].append(ant_id)
        
        print(f"\n🎨 Regroupement des chemins identiques:")
        for path, ant_ids in path_groups.items():
            if len(ant_ids) == 1:
                print(f"   f{ant_ids[0]}: {' → '.join(path)}")
            else:
                ants_str = ', '.join([f"f{aid}" for aid in sorted(ant_ids)])
                print(f"   {ants_str}: {' → '.join(path)}")
        
        print(f"\n✅ Test réussi ! {len(path_groups)} chemin(s) distinct(s)")
    else:
        print(f"❌ Fichier non trouvé: {filepath}")
    
    print(f"\n🎯 Maintenant lance l'interface pour voir les chemins en couleur !")

if __name__ == "__main__":
    test_ant_paths()