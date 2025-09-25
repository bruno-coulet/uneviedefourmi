'''
Animation interactive des déplacements de fourmis
'''

import networkx as nx
import matplotlib.pyplot as plt
import time
from main import load_antnest_from_txt, solve_antnest


class AntAnimator:
    """Classe pour animer les déplacements des fourmis"""
    
    def __init__(self, colony):
        self.colony = colony
        self.fig, self.ax = plt.subplots(figsize=(14, 10))
        self.pos = nx.spring_layout(self.colony.graph, seed=42, k=3)
        self.step_index = 0
        self.current_occupancy = self._init_occupancy()
        
    def _init_occupancy(self):
        """Initialise l'occupation initiale"""
        occupancy = {room: [] for room in self.colony.antnest.rooms.keys()}
        occupancy["Sv"] = list(range(1, self.colony.antnest.ants + 1))
        occupancy["Sd"] = []
        return occupancy
    
    def _get_node_colors_and_sizes(self, occupancy):
        """Calcule les couleurs et tailles des nœuds selon l'occupation"""
        node_colors = []
        node_sizes = []
        
        for node in self.colony.graph.nodes():
            occupants = len(occupancy.get(node, []))
            
            if node == "Sv":
                # Vestibule : vert, taille selon occupation
                node_colors.append('limegreen')
                node_sizes.append(2500 + occupants * 100)
            elif node == "Sd":
                # Dortoir : rouge, taille selon occupation
                node_colors.append('crimson')
                node_sizes.append(2500 + occupants * 50)
            else:
                # Autres salles : bleu, intensité selon occupation
                capacity = self.colony.antnest.rooms.get(node, 1)
                ratio = occupants / capacity if capacity > 0 else 0
                intensity = 0.3 + ratio * 0.7
                node_colors.append(plt.cm.Blues(intensity))
                node_sizes.append(1800 + occupants * 200)
                
        return node_colors, node_sizes
    
    def _update_occupancy(self, step_num):
        """Met à jour l'occupation après une étape"""
        if step_num <= len(self.colony.movements_history):
            # Réinitialiser
            self.current_occupancy = self._init_occupancy()
            
            # Appliquer tous les mouvements jusqu'à cette étape
            for step_idx in range(step_num):
                if step_idx < len(self.colony.movements_history):
                    movements = self.colony.movements_history[step_idx]
                    for ant_id, old_room, new_room in movements:
                        # Retirer la fourmi de l'ancienne salle
                        if ant_id in self.current_occupancy.get(old_room, []):
                            self.current_occupancy[old_room].remove(ant_id)
                        # Ajouter à la nouvelle salle
                        if new_room not in self.current_occupancy:
                            self.current_occupancy[new_room] = []
                        self.current_occupancy[new_room].append(ant_id)
    
    def animate_step_by_step(self, delay=2.0):
        """Animation manuelle étape par étape avec délai"""
        print(f"\n🎬 ANIMATION : {self.colony.antnest.name}")
        print(f"⏱️  Délai entre étapes : {delay}s")
        print("🔘 Fermez la fenêtre pour passer à la suite\n")
        
        # État initial
        plt.ion()  # Mode interactif
        
        for step_num in range(len(self.colony.movements_history) + 1):
            # Effacer l'ancienne image
            self.ax.clear()
            
            # Mettre à jour l'occupation
            self._update_occupancy(step_num)
            
            # Calculer couleurs et tailles
            node_colors, node_sizes = self._get_node_colors_and_sizes(self.current_occupancy)
            
            # Dessiner le graphe (arêtes normales)
            nx.draw_networkx_edges(self.colony.graph, self.pos, ax=self.ax,
                                  edge_color='lightgray', width=1)
            
            # Dessiner les nœuds
            nx.draw_networkx_nodes(self.colony.graph, self.pos, ax=self.ax,
                                  node_color=node_colors, 
                                  node_size=node_sizes)
            
            # Ajouter des flèches pour les mouvements en cours
            if step_num > 0 and step_num <= len(self.colony.movements_history):
                current_movements = self.colony.movements_history[step_num - 1]
                for ant_id, old_room, new_room in current_movements:
                    if old_room in self.pos and new_room in self.pos:
                        # Position des nœuds
                        x1, y1 = self.pos[old_room]
                        x2, y2 = self.pos[new_room]
                        
                        # Calculer le vecteur directionnel  
                        dx = x2 - x1
                        dy = y2 - y1
                        
                        # Décaler légèrement pour éviter les nœuds
                        offset = 0.15
                        x1_arrow = x1 + dx * offset
                        y1_arrow = y1 + dy * offset
                        x2_arrow = x2 - dx * offset
                        y2_arrow = y2 - dy * offset
                        
                        # Dessiner la flèche
                        self.ax.annotate('', xy=(x2_arrow, y2_arrow), xytext=(x1_arrow, y1_arrow),
                                       arrowprops=dict(arrowstyle='->', color='red', lw=3, alpha=0.8))
                        
                        # Ajouter le numéro de la fourmi
                        mid_x = (x1 + x2) / 2
                        mid_y = (y1 + y2) / 2
                        self.ax.text(mid_x, mid_y, f'f{ant_id}', 
                                   bbox=dict(boxstyle="round,pad=0.2", facecolor='yellow', alpha=0.8),
                                   ha='center', va='center', fontsize=10, fontweight='bold')
            
            # Labels avec occupation
            labels = {}
            for node in self.colony.graph.nodes():
                occupants = self.current_occupancy.get(node, [])
                if node in self.colony.antnest.rooms:
                    capacity = self.colony.antnest.rooms[node]
                    labels[node] = f"{node}\n({len(occupants)}/{capacity})"
                else:
                    labels[node] = f"{node}\n({len(occupants)})"
                    
            nx.draw_networkx_labels(self.colony.graph, self.pos, labels, 
                                  ax=self.ax, font_size=12)
            
            # Titre avec info de l'étape
            if step_num == 0:
                title = f"🐜 État Initial - {self.colony.antnest.name}\nToutes les fourmis au vestibule"
            elif step_num <= len(self.colony.movements_history):
                movements = self.colony.movements_history[step_num - 1]
                movements_text = " | ".join([f"f{ant_id}:{old}→{new}" 
                                           for ant_id, old, new in movements[:3]])
                if len(movements) > 3:
                    movements_text += f" | +{len(movements)-3} autres"
                title = f"🐜 Étape {step_num} - {self.colony.antnest.name}\n{movements_text}"
            else:
                arrived = len(self.current_occupancy.get("Sd", []))
                title = f"🎉 Terminé ! - {self.colony.antnest.name}\n{arrived}/{self.colony.antnest.ants} fourmis au dortoir"
            
            self.ax.set_title(title, fontsize=16, pad=20)
            self.ax.axis('off')
            
            # Afficher et attendre
            plt.draw()
            plt.pause(delay)
            
            # Afficher les mouvements de cette étape
            if step_num > 0 and step_num <= len(self.colony.movements_history):
                movements = self.colony.movements_history[step_num - 1]
                if movements:
                    print(f"+++ E{step_num} +++")
                    for ant_id, old_room, new_room in movements:
                        print(f"f{ant_id} - {old_room} - {new_room}")
                    print()
        
        plt.ioff()  # Désactiver mode interactif
        plt.show()


def demo_animation():
    """Démonstration des animations temps réel"""
    print("🎬 DÉMONSTRATION ANIMATION TEMPS RÉEL")
    print("=" * 50)
    
    # Choisir une fourmilière
    fourmilieres = [
        ("fourmilieres/fourmiliere_zero.txt", "Simple (2 fourmis)"),
        ("fourmilieres/fourmiliere_un.txt", "Moyenne (5 fourmis)"),
        ("fourmilieres/fourmiliere_quatre.txt", "Complexe (10 fourmis)")
    ]
    
    print("Choisissez une fourmilière à animer :")
    for i, (_, desc) in enumerate(fourmilieres):
        print(f"{i+1}. {desc}")
    
    try:
        choice = int(input("\nVotre choix (1-3) : ")) - 1
        if choice < 0 or choice >= len(fourmilieres):
            choice = 0
            
        filepath, desc = fourmilieres[choice]
        print(f"\n🐜 Animation de : {desc}")
        
        # Charger et résoudre
        antnest = load_antnest_from_txt(filepath)
        colony = solve_antnest(antnest)
        
        # Créer l'animateur
        animator = AntAnimator(colony)
        
        # Choisir le type d'animation
        print("\nType d'animation :")
        print("1. Animation étape par étape (recommandé)")
        print("2. Créer un GIF")
        
        anim_choice = input("Votre choix (1-2, défaut=1) : ").strip()
        
        if anim_choice == "2":
            # GIF
            filename = f"animation_{antnest.name}.gif"
            animator.create_gif_animation(filename)
        else:
            # Animation temps réel
            delay = float(input("Délai entre étapes en secondes (défaut=1.5) : ") or "1.5")
            animator.animate_step_by_step(delay)
            
    except (ValueError, KeyboardInterrupt):
        print("\n❌ Animation annulée")
    except Exception as e:
        print(f"\n❌ Erreur : {e}")


if __name__ == "__main__":
    demo_animation()