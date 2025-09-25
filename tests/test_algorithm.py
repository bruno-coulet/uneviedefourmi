'''
Test complet du système de fourmis
'''

from test_parser import load_antnest_from_txt
from ants import solve_antnest


def test_fourmiliere_zero():
    """Test avec la fourmilière la plus simple (2 fourmis)"""
    print("🐜 Test avec fourmilière zero (2 fourmis)")
    print("=" * 50)
    
    # Charger la fourmilière
    antnest = load_antnest_from_txt("fourmilieres/fourmiliere_zero.txt")
    print("Configuration:")
    print(antnest)
    print()
    
    # Résoudre
    colony = solve_antnest(antnest)
    
    # Afficher la solution
    colony.print_solution()
    
    return colony


def test_fourmiliere_quatre():
    """Test avec une fourmilière plus complexe (10 fourmis)"""
    print("🐜 Test avec fourmilière quatre (10 fourmis)")
    print("=" * 50)
    
    # Charger la fourmilière
    antnest = load_antnest_from_txt("fourmilieres/fourmiliere_quatre.txt")
    print("Configuration:")
    print(antnest)
    print()
    
    # Résoudre
    colony = solve_antnest(antnest)
    
    # Afficher la solution
    colony.print_solution()
    
    return colony


if __name__ == "__main__":
    # Test 1: Fourmilière simple
    colony1 = test_fourmiliere_zero()
    
    print("\n" + "="*80 + "\n")
    
    # Test 2: Fourmilière complexe
    colony2 = test_fourmiliere_quatre()
    
    print("✅ Tests terminés!")