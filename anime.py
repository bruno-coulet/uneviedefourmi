'''
Animation simple et rapide des fourmis
'''

import matplotlib.pyplot as plt
import networkx as nx
import time
from main import load_antnest_from_txt, solve_antnest


def animation_simple(fourmiliere_path, delay=1.5):
    """Animation simple d'une fourmilière"""
    print(f"🎬 Animation de {fourmiliere_path}")
    
    # Charger et résoudre
    antnest = load_antnest_from_txt(fourmiliere_path)
    colony = solve_antnest(antnest)
    
    print(f"Solution trouvée en {len(colony.movements_history)} étapes")
    
    # Configuration de l'affichage
    plt.ion()  # Mode interactif
    fig, ax = plt.subplots(figsize=(12, 8))
    pos = nx.spring_layout(colony.graph, seed=42, k=2)
    
    # État initial - toutes les fourmis au vestibule
    occupancy = {room: [] for room in antnest.rooms.keys()}
    occupancy["Sv"] = list(range(1, antnest.ants + 1))
    occupancy["Sd"] = []
    
    def dessiner_etape(step_num, occupancy):
        """Dessine une étape"""
        ax.clear()
        
        # Couleurs et tailles selon occupation
        node_colors = []
        node_sizes = []
        
        # Obtenir les salles visitées pendant toute la simulation
        visited_rooms = colony.get_visited_rooms()
        
        for node in colony.graph.nodes():
            nb_fourmis = len(occupancy.get(node, []))
            
            if node == "Sv":
                node_colors.append('lightgreen')
                # Vestibule : taille fixe grande + bonus par fourmi
                node_sizes.append(2500 + nb_fourmis * 80)
            elif node == "Sd":
                node_colors.append('salmon')
                # Dortoir : taille fixe grande + bonus par fourmi
                node_sizes.append(2500 + nb_fourmis * 40)
            else:
                # Salles normales : taille basée sur la capacité + occupation
                capacity = antnest.rooms.get(node, 1)
                intensity = min(1.0, nb_fourmis / capacity)
                
                # Différenciation entre salles visitées et non visitées
                if node in visited_rooms:
                    # Salles empruntées : couleur basée sur la capacité ET l'occupation
                    capacity_lightness = min(0.4 + capacity * 0.15, 0.9)
                    node_colors.append(plt.cm.Blues(capacity_lightness * (0.3 + intensity * 0.6)))
                else:
                    # Salles jamais empruntées : gris foncé
                    node_colors.append('darkgray')
                
                # Taille basée sur la capacité
                base_size = 800
                capacity_bonus = capacity * 400  
                occupancy_bonus = nb_fourmis * 100
                total_size = base_size + capacity_bonus + occupancy_bonus
                node_sizes.append(total_size)
        
        # 🐜 Dessiner les arêtes avec phéromones progressives (jusqu'à l'étape actuelle)
        pheromone_data = colony.get_pheromone_data_until_step(step_num)
        
        # Arêtes normales (sans phéromones significatives)
        normal_edges = []
        for edge in colony.graph.edges():
            normalized_edge = tuple(sorted(edge))
            if normalized_edge not in pheromone_data:
                normal_edges.append(edge)
        
        # Dessiner arêtes normales (tunnels non empruntés en noir)
        if normal_edges:
            nx.draw_networkx_edges(colony.graph, pos, ax=ax, edgelist=normal_edges,
                                 edge_color='black', width=0.8, alpha=0.4)
        
        # Dessiner arêtes avec phéromones (progressives!)
        for edge, data in pheromone_data.items():
            if edge in colony.graph.edges() or (edge[1], edge[0]) in colony.graph.edges():
                # Couleur qui évolue avec l'intensité
                color = plt.cm.plasma(data['intensity'])  # Couleur dégradée selon intensité
                nx.draw_networkx_edges(colony.graph, pos, ax=ax, edgelist=[edge],
                                     edge_color=[color], 
                                     width=data['width'] * 0.9,
                                     alpha=data['alpha'] * 0.8)
        
        # Dessiner les nœuds
        nx.draw_networkx_nodes(colony.graph, pos, ax=ax,
                              node_color=node_colors, 
                              node_size=node_sizes, alpha=0.8)
        
        # Ajouter des flèches pour les mouvements en cours (sauf à l'étape finale)
        is_final_display = step_num > len(colony.movements_history)
        
        if step_num > 0 and step_num <= len(colony.movements_history) and not is_final_display:
            current_movements = colony.movements_history[step_num - 1]
            
            # Grouper les mouvements par tunnel
            tunnel_movements = {}
            for ant_id, old_room, new_room in current_movements:
                tunnel = (old_room, new_room)
                if tunnel not in tunnel_movements:
                    tunnel_movements[tunnel] = []
                tunnel_movements[tunnel].append(ant_id)
            
            # Dessiner une flèche par tunnel
            for (old_room, new_room), ant_ids in tunnel_movements.items():
                if old_room in pos and new_room in pos:
                    x1, y1 = pos[old_room]
                    x2, y2 = pos[new_room]
                    dx = x2 - x1
                    dy = y2 - y1
                    
                    # Décaler légèrement pour éviter les nœuds
                    offset = 0.15
                    x1_arrow = x1 + dx * offset
                    y1_arrow = y1 + dy * offset
                    x2_arrow = x2 - dx * offset  
                    y2_arrow = y2 - dy * offset
                    
                    # Flèche adaptée au nombre de fourmis
                    nb_fourmis = len(ant_ids)
                    line_width = min(2 + nb_fourmis * 1.5, 8)
                    alpha = min(0.6 + nb_fourmis * 0.1, 1.0)
                    
                    ax.annotate('', xy=(x2_arrow, y2_arrow), xytext=(x1_arrow, y1_arrow),
                               arrowprops=dict(arrowstyle='->', color='red', lw=line_width, alpha=alpha))
                    
                    # Label groupé
                    mid_x = (x1 + x2) / 2
                    mid_y = (y1 + y2) / 2
                    
                    if nb_fourmis == 1:
                        label_text = f'f{ant_ids[0]}'
                        bg_color = 'yellow'
                    else:
                        if nb_fourmis <= 3:
                            label_text = ', '.join([f'f{aid}' for aid in sorted(ant_ids)])
                        else:
                            label_text = f'{nb_fourmis} fourmis'
                        bg_color = 'orange'
                    
                    ax.text(mid_x, mid_y, label_text, 
                           bbox=dict(boxstyle="round,pad=0.3", facecolor=bg_color, alpha=0.9),
                           ha='center', va='center', fontsize=9, fontweight='bold')
        
        # Labels simples et clairs
        labels = {}
        for node in colony.graph.nodes():
            nb_fourmis = len(occupancy.get(node, []))
            if node in antnest.rooms:
                capacity = antnest.rooms[node]
                labels[node] = f"{node}\n{nb_fourmis}/{capacity}"
            else:
                # Vestibule et Dortoir
                labels[node] = f"{node}\n{nb_fourmis}"
        
        # 📊 Étiquettes de comptage de passages sur les tunnels
        pheromone_data = colony.get_pheromone_data_until_step(step_num)
        for edge, data in pheromone_data.items():
            if data['passages'] > 0:  # Afficher seulement les tunnels utilisés
                # Trouver les positions des nœuds
                if edge[0] in pos and edge[1] in pos:
                    x1, y1 = pos[edge[0]]
                    x2, y2 = pos[edge[1]]
                    
                    # Position du milieu du tunnel (légèrement décalée)
                    mid_x = (x1 + x2) / 2
                    mid_y = (y1 + y2) / 2 + 0.08  # Décalage pour éviter la superposition
                    
                    # Couleur selon l'intensité d'utilisation
                    if data['intensity'] < 0.3:
                        label_color = 'lightcyan'
                    elif data['intensity'] < 0.7:
                        label_color = 'lightgreen'
                    else:
                        label_color = 'gold'
                    
                    # Afficher le compteur de passages
                    ax.text(mid_x, mid_y, str(data['passages']),
                           bbox=dict(boxstyle="circle,pad=0.2", facecolor=label_color, 
                                   alpha=0.9, edgecolor='black', linewidth=1),
                           ha='center', va='center', fontsize=9, fontweight='bold',
                           color='darkblue')
                
        nx.draw_networkx_labels(colony.graph, pos, labels, ax=ax, font_size=11)
        
        # Titre avec statistiques des tunnels
        if step_num == 0:
            titre = f"DEBUT - {antnest.name} ({antnest.ants} fourmis)"
        elif step_num <= len(colony.movements_history):
            stats = colony.get_tunnel_statistics(step_num)
            active = stats['global']['active_tunnels']
            total = stats['global']['total_tunnels']
            passages = stats['global']['total_passages']
            rate = stats['global']['usage_rate']
            
            titre = (f"ETAPE {step_num} - {antnest.name}\n"
                    f"Tunnels actifs: {active}/{total} ({rate:.0f}%) | Passages: {passages}")
        else:
            titre = f"FINI ! - Toutes les fourmis au dortoir"
        
        ax.set_title(titre, fontsize=14, pad=15)
        ax.axis('off')
        
        plt.draw()
        plt.pause(delay)
    
    # Animation
    print("🎬 Démarrage de l'animation...\n")
    
    # État initial
    dessiner_etape(0, occupancy)
    print("État initial : Toutes les fourmis au vestibule")
    time.sleep(delay)
    
    # Chaque étape
    for step_num in range(1, len(colony.movements_history) + 1):
        # Appliquer les mouvements de cette étape
        movements = colony.movements_history[step_num - 1]
        
        if movements:
            print(f"\n+++ ETAPE {step_num} +++")
            for ant_id, old_room, new_room in movements:
                print(f"f{ant_id}: {old_room} -> {new_room}")
                
                # Mettre à jour l'occupation
                if ant_id in occupancy.get(old_room, []):
                    occupancy[old_room].remove(ant_id)
                if new_room not in occupancy:
                    occupancy[new_room] = []
                occupancy[new_room].append(ant_id)
        
        # Dessiner
        dessiner_etape(step_num, occupancy)
        time.sleep(delay)
    
    # Étape finale : affichage propre sans flèches
    final_step = len(colony.movements_history) + 1
    dessiner_etape(final_step, occupancy)
    time.sleep(delay)
    
    # État final
    arrived = len(occupancy.get("Sd", []))
    print(f"\n🎉 TERMINÉ ! {arrived}/{antnest.ants} fourmis au dortoir")
    
    plt.ioff()
    plt.show()


if __name__ == "__main__":
    print("🐜 ANIMATION SIMPLE DES FOURMIS")
    print("=" * 40)
    
    fourmilieres = [
        "fourmilieres/fourmiliere_zero.txt",
        "fourmilieres/fourmiliere_un.txt",
        "fourmilieres/fourmiliere_deux.txt", 
        "fourmilieres/fourmiliere_trois.txt",
        "fourmilieres/fourmiliere_quatre.txt",
        "fourmilieres/fourmiliere_cinq.txt"
    ]
    
    print("Choisissez une fourmilière :")
    for i, path in enumerate(fourmilieres):
        name = path.split('/')[-1].replace('.txt', '').replace('_', ' ')
        print(f"{i+1}. {name}")
    
    try:
        choix = int(input(f"\nVotre choix (1-{len(fourmilieres)}) : ")) - 1
        if choix < 0 or choix >= len(fourmilieres):
            print("❌ Choix invalide, utilisation de fourmiliere zero")
            choix = 0
        
        vitesse = input("Vitesse (lent=3, normal=1.5, rapide=0.5) : ").strip()
        delay = float(vitesse) if vitesse else 1.5
        
        animation_simple(fourmilieres[choix], delay)
        
    except (ValueError, KeyboardInterrupt):
        print("Animation annulée")
    except Exception as e:
        print(f"Erreur : {e}")