#!/usr/bin/env python3
"""
Lanceur principal pour 'Une vie de fourmi'
Choix entre interface terminal ou graphique
"""

import sys
import os

def main():
    """Fonction principale de lancement - Lance directement l'interface graphique"""
    print("� UNE VIE DE FOURMI")
    print("=" * 40)
    print("🚀 Lancement de l'interface graphique...")
    
    try:
        import gui
        gui.main()
    except ImportError as e:
        print(f"❌ Erreur GUI: {e}")
        print("🔄 Basculement vers interface terminal...")
        try:
            import main
            main.main() if hasattr(main, 'main') else exec(open('main.py').read())
        except Exception as e2:
            print(f"❌ Erreur terminal: {e2}")
            print("💡 Essayez de lancer directement: python gui.py")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        print("� Essayez de lancer directement: python gui.py")


if __name__ == "__main__":
    main()