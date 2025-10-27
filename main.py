'''
résolution des fourmilières.
'''

import networkx as nx
import matplotlib.pyplot as plt
import os
import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


class AntNest:
    def __init__(self, name: str, ants: int, rooms: dict[str, int], tubes: list[tuple[str, str]]):
        '''fonction d'initialisation d'une fourmilière avec :
        - le nom de la fourmilière
        - le nombre de fourmis
        - les salles (dict: nom -> capacité)
        - les tunnels (list: tuple: origine -> destination)
        '''
        self.name = name
        self.ants = ants
        self.rooms = rooms
        self.tubes = tubes

    def __str__(self) -> str:
        '''représentation textuelle de la fourmilière'''
        return (
            f"{self.name}\n"
            f"- Fourmis : {self.ants}\n"
            f"- Salles  : {len(self.rooms)} ({self.rooms})\n"
            f"- Tunnels : {len(self.tubes)} {self.tubes}"
        )
    
    def __repr__(self):
        return f"AntNest(name={self.name}, ants={self.ants}, rooms={self.rooms}, tubes={self.tubes})"


@dataclass
class Ant:
    """Représente une fourmi avec son identifiant et sa position actuelle"""
    id: int
    current_room: str
    
    def __str__(self):
        return f"f{self.id}"


class AntColony:
    """Gère une colonie de fourmis et leur déplacement dans la fourmilière"""
    
    def __init__(self, antnest):
        self.antnest = antnest
        self.graph = self._create_graph()
        self.ants = [Ant(i+1, "Sv") for i in range(antnest.ants)]
        self.room_occupancy = self._init_room_occupancy()
        self.step_count = 0
        self.movements_history = []
        
        # 🐜 Tracking des phéromones (passages sur les arêtes)
        self.edge_passages = self._init_edge_passages()
        
    def _init_edge_passages(self) -> Dict[tuple, int]:
        """Initialise le compteur de passages pour chaque arête"""
        passages = {}
        # Toutes les arêtes du graphe (tunnels)
        for edge in self.graph.edges():
            # Normaliser l'ordre des sommets pour éviter (A,B) vs (B,A)
            normalized_edge = tuple(sorted(edge))
            passages[normalized_edge] = 0
        return passages
        
    def _create_graph(self) -> nx.Graph:
        """Crée un graphe NetworkX à partir des tunnels"""
        G = nx.Graph()
        G.add_edges_from(self.antnest.tubes)
        return G
    
    def _init_room_occupancy(self) -> Dict[str, List[int]]:
        """Initialise l'occupation des salles"""
        occupancy = {room: [] for room in self.antnest.rooms.keys()}
        occupancy["Sv"] = [ant.id for ant in self.ants]
        occupancy["Sd"] = []
        return occupancy
    
    def get_available_moves(self, ant: Ant) -> List[str]:
        """Retourne les salles où une fourmi peut se déplacer"""
        current_room = ant.current_room
        available_rooms = []
        
        neighbors = list(self.graph.neighbors(current_room))
        
        for room in neighbors:
            if room == "Sd":
                available_rooms.append(room)
            elif room in self.antnest.rooms:
                capacity = self.antnest.rooms[room]
                current_occupants = len(self.room_occupancy.get(room, []))
                if current_occupants < capacity:
                    available_rooms.append(room)
            elif room == "Sv":
                available_rooms.append(room)
                
        return available_rooms
    
    def move_ant(self, ant: Ant, destination: str) -> bool:
        """Déplace une fourmi vers la destination si possible"""
        if destination not in self.get_available_moves(ant):
            return False
            
        if ant.current_room in self.room_occupancy:
            if ant.id in self.room_occupancy[ant.current_room]:
                self.room_occupancy[ant.current_room].remove(ant.id)
        
        if destination not in self.room_occupancy:
            self.room_occupancy[destination] = []
        self.room_occupancy[destination].append(ant.id)
        
        ant.current_room = destination
        return True
    
    def simulate_step(self) -> List[Tuple[int, str, str]]:
        """Simule une étape de déplacement - Version hybride optimisée"""
        movements = []
        
        # STRATÉGIE HYBRIDE:
        # 1. Essayer d'abord l'approche simple (séquentielle) efficace
        # 2. Seulement si nécessaire, utiliser la résolution de conflits
        
        # Phase 1: Tentative d'approche séquentielle simple (comme l'ancien)
        ants_needing_conflict_resolution = []
        temp_occupancy = {k: v.copy() for k, v in self.room_occupancy.items()}  # Copie temporaire
        
        for ant in self.ants:
            if ant.current_room == "Sd":
                continue
                
            available_moves = self._get_available_moves_with_temp(ant, temp_occupancy)
            
            if "Sd" in available_moves:
                # Priorité absolue pour aller au dortoir
                old_room = ant.current_room
                if self._can_move_immediately(ant, "Sd", temp_occupancy):
                    movements.append((ant.id, old_room, "Sd"))
                    self._update_temp_occupancy(ant, old_room, "Sd", temp_occupancy)
                    self._record_edge_passage(old_room, "Sd")  # 🐜 Phéromones
                    ant.current_room = "Sd"  # Mettre à jour immédiatement
                else:
                    ants_needing_conflict_resolution.append(ant)
            else:
                best_move = self._choose_best_move_with_temp(ant, available_moves)
                if best_move and self._can_move_immediately(ant, best_move, temp_occupancy):
                    old_room = ant.current_room
                    movements.append((ant.id, old_room, best_move))
                    self._update_temp_occupancy(ant, old_room, best_move, temp_occupancy)
                    self._record_edge_passage(old_room, best_move)  # 🐜 Phéromones
                    ant.current_room = best_move  # Mettre à jour immédiatement
                elif best_move:
                    ants_needing_conflict_resolution.append(ant)
        
        # Phase 2: Résolution de conflits pour les fourmis restantes (si nécessaire)
        if ants_needing_conflict_resolution:
            planned_moves = []
            for ant in ants_needing_conflict_resolution:
                available_moves = self.get_available_moves(ant)
                if "Sd" in available_moves:
                    planned_moves.append((ant, ant.current_room, "Sd"))
                else:
                    best_move = self._choose_best_move(ant, available_moves)
                    if best_move:
                        planned_moves.append((ant, ant.current_room, best_move))
            
            valid_moves = self._resolve_movement_conflicts(planned_moves)
            
            for ant, old_room, new_room in valid_moves:
                if self._execute_move(ant, old_room, new_room):
                    movements.append((ant.id, old_room, new_room))
        
        # Mettre à jour l'occupation réelle
        self.room_occupancy = temp_occupancy
        
        self.step_count += 1
        self.movements_history.append(movements)
        return movements
    
    def _can_move_immediately(self, ant, destination: str, temp_occupancy: dict) -> bool:
        """Vérifie si une fourmi peut bouger immédiatement sans conflit"""
        if destination in ["Sd", "Sv"]:  # Capacité illimitée
            return True
        elif destination in self.antnest.rooms:
            capacity = self.antnest.rooms[destination]
            current_occupants = len(temp_occupancy.get(destination, []))
            return current_occupants < capacity
        return False
    
    def _update_temp_occupancy(self, ant, old_room: str, new_room: str, temp_occupancy: dict):
        """Met à jour l'occupation temporaire"""
        if old_room in temp_occupancy and ant.id in temp_occupancy[old_room]:
            temp_occupancy[old_room].remove(ant.id)
        
        if new_room not in temp_occupancy:
            temp_occupancy[new_room] = []
        temp_occupancy[new_room].append(ant.id)
    
    def _get_available_moves_with_temp(self, ant, temp_occupancy: dict) -> List[str]:
        """Retourne les salles où une fourmi peut se déplacer (avec occupation temporaire)"""
        current_room = ant.current_room
        available_rooms = []
        
        neighbors = list(self.graph.neighbors(current_room))
        
        for room in neighbors:
            if room == "Sd":
                available_rooms.append(room)
            elif room in self.antnest.rooms:
                capacity = self.antnest.rooms[room]
                current_occupants = len(temp_occupancy.get(room, []))
                if current_occupants < capacity:
                    available_rooms.append(room)
            elif room == "Sv":
                available_rooms.append(room)
                
        return available_rooms
    
    def _choose_best_move_with_temp(self, ant, available_moves: List[str]) -> Optional[str]:
        """Choisit le meilleur mouvement pour se rapprocher du dortoir"""
        if not available_moves:
            return None
            
        best_move = None
        shortest_distance = float('inf')
        
        for move in available_moves:
            try:
                distance = nx.shortest_path_length(self.graph, move, "Sd")
                if distance < shortest_distance:
                    shortest_distance = distance
                    best_move = move
            except nx.NetworkXNoPath:
                continue
                
        return best_move
    
    def _resolve_movement_conflicts(self, planned_moves) -> List[Tuple]:
        """Résout les conflits de mouvement et détecte les échanges simultanés"""
        valid_moves = []
        room_destinations = {}  # destination -> liste des fourmis qui veulent y aller
        room_departures = {}    # salle -> liste des fourmis qui la quittent
        
        # Analyser les mouvements planifiés
        for ant, old_room, new_room in planned_moves:
            # Enregistrer les destinations
            if new_room not in room_destinations:
                room_destinations[new_room] = []
            room_destinations[new_room].append((ant, old_room, new_room))
            
            # Enregistrer les départs
            if old_room not in room_departures:
                room_departures[old_room] = []
            room_departures[old_room].append((ant, old_room, new_room))
        
        # Traiter chaque destination
        for destination, moves_to_dest in room_destinations.items():
            if destination == "Sd":
                # Dortoir : capacité illimitée
                valid_moves.extend(moves_to_dest)
            elif destination == "Sv":
                # Vestibule : capacité illimitée
                valid_moves.extend(moves_to_dest)
            elif destination in self.antnest.rooms:
                # Salle normale : vérifier capacité et libérations
                capacity = self.antnest.rooms[destination]
                current_occupants = len(self.room_occupancy.get(destination, []))
                
                # Calculer les places qui se libèrent
                departing_from_dest = len(room_departures.get(destination, []))
                available_spots = capacity - current_occupants + departing_from_dest
                
                # SIMPLIFICATION : pas de tri par priorité, ordre naturel (FIFO)
                # Cela évite les embouteillages artificiels
                valid_moves.extend(moves_to_dest[:available_spots])
        
        return valid_moves
    
    def _execute_move(self, ant, old_room, new_room) -> bool:
        """Exécute un mouvement préalablement validé"""
        # Retirer la fourmi de sa position actuelle
        if old_room in self.room_occupancy:
            if ant.id in self.room_occupancy[old_room]:
                self.room_occupancy[old_room].remove(ant.id)
        
        # Ajouter la fourmi à sa nouvelle position
        if new_room not in self.room_occupancy:
            self.room_occupancy[new_room] = []
        self.room_occupancy[new_room].append(ant.id)
        
        # 🐜 Enregistrer le passage sur l'arête (dépôt de phéromones)
        self._record_edge_passage(old_room, new_room)
        
        # Mettre à jour la position de la fourmi
        ant.current_room = new_room
        return True
    
    def _record_edge_passage(self, room1: str, room2: str):
        """Enregistre le passage d'une fourmi sur une arête"""
        # Normaliser l'ordre pour éviter (A,B) vs (B,A)
        edge = tuple(sorted([room1, room2]))
        if edge in self.edge_passages:
            self.edge_passages[edge] += 1
    
    def get_pheromone_data(self) -> Dict[tuple, dict]:
        """Retourne les données de phéromones avec intensité normalisée"""
        if not self.edge_passages:
            return {}
            
        max_passages = max(self.edge_passages.values()) if self.edge_passages.values() else 1
        
        pheromone_data = {}
        for edge, passages in self.edge_passages.items():
            if passages > 0:  # Seulement les arêtes avec des passages
                intensity = passages / max_passages  # Normalisation 0-1
                pheromone_data[edge] = {
                    'passages': passages,
                    'intensity': intensity,
                    'width': 1 + intensity * 4,  # Largeur 1-5
                    'alpha': 0.3 + intensity * 0.7  # Transparence 0.3-1.0
                }
        return pheromone_data
    
    def get_tunnel_statistics(self, target_step: int = None) -> dict:
        """Retourne les statistiques complètes des tunnels"""
        if target_step is None:
            target_step = len(self.movements_history)
            
        # Obtenir les phéromones jusqu'à l'étape cible
        pheromone_data = self.get_pheromone_data_until_step(target_step)
        
        # Statistiques globales
        total_tunnels = len(self.graph.edges())
        active_tunnels = len(pheromone_data)
        unused_tunnels = total_tunnels - active_tunnels
        total_passages = sum(data['passages'] for data in pheromone_data.values())
        
        # Statistiques détaillées par tunnel
        tunnel_details = {}
        
        # Tunnels utilisés
        for edge, data in pheromone_data.items():
            tunnel_name = f"{edge[0]} ↔ {edge[1]}"
            tunnel_details[tunnel_name] = {
                'passages': data['passages'],
                'intensity': data['intensity'],
                'status': 'actif'
            }
        
        # Tunnels non utilisés
        for edge in self.graph.edges():
            normalized_edge = tuple(sorted(edge))
            if normalized_edge not in pheromone_data:
                tunnel_name = f"{edge[0]} ↔ {edge[1]}"
                tunnel_details[tunnel_name] = {
                    'passages': 0,
                    'intensity': 0.0,
                    'status': 'inutilisé'
                }
        
        return {
            'global': {
                'total_tunnels': total_tunnels,
                'active_tunnels': active_tunnels,
                'unused_tunnels': unused_tunnels,
                'total_passages': total_passages,
                'usage_rate': (active_tunnels / total_tunnels * 100) if total_tunnels > 0 else 0
            },
            'details': tunnel_details,
            'step': target_step
        }
    
    def print_tunnel_statistics(self, target_step: int = None):
        """Affiche les statistiques détaillées des tunnels"""
        stats = self.get_tunnel_statistics(target_step)
        
        print(f"\n🐜 === STATISTIQUES DES TUNNELS (Étape {stats['step']}) ===")
        print(f"📊 Vue d'ensemble :")
        print(f"   • Total de tunnels : {stats['global']['total_tunnels']}")
        print(f"   • Tunnels actifs : {stats['global']['active_tunnels']} ({stats['global']['usage_rate']:.1f}%)")
        print(f"   • Tunnels inutilisés : {stats['global']['unused_tunnels']}")
        print(f"   • Passages totaux : {stats['global']['total_passages']}")
        
        print(f"\n🟣 Tunnels actifs (avec phéromones) :")
        active_tunnels = {k: v for k, v in stats['details'].items() if v['status'] == 'actif'}
        if active_tunnels:
            # Trier par nombre de passages (décroissant)
            sorted_active = sorted(active_tunnels.items(), key=lambda x: x[1]['passages'], reverse=True)
            for tunnel, data in sorted_active:
                bar = "█" * int(data['intensity'] * 10)  # Barre visuelle
                print(f"   • {tunnel:<12} : {data['passages']:>2} passages {bar} ({data['intensity']:.2f})")
        else:
            print("   (Aucun tunnel utilisé)")
            
        print(f"\n⚪ Tunnels inutilisés :")
        unused_tunnels = [k for k, v in stats['details'].items() if v['status'] == 'inutilisé']
        if unused_tunnels:
            for tunnel in sorted(unused_tunnels):
                print(f"   • {tunnel}")
        else:
            print("   (Tous les tunnels ont été utilisés)")
    
    def get_pheromone_data_until_step(self, target_step: int) -> Dict[tuple, dict]:
        """Retourne les données de phéromones accumulées jusqu'à une étape donnée"""
        if target_step <= 0 or not self.movements_history:
            return {}
        
        # Compter les passages jusqu'à l'étape cible
        progressive_passages = {}
        
        # Initialiser tous les edges à 0
        for edge in self.graph.edges():
            normalized_edge = tuple(sorted(edge))
            progressive_passages[normalized_edge] = 0
        
        # Compter les passages étape par étape
        for step_idx in range(min(target_step, len(self.movements_history))):
            movements = self.movements_history[step_idx]
            for ant_id, old_room, new_room in movements:
                edge = tuple(sorted([old_room, new_room]))
                if edge in progressive_passages:
                    progressive_passages[edge] += 1
        
        # Calculer les intensités
        max_passages = max(progressive_passages.values()) if progressive_passages.values() else 1
        if max_passages == 0:
            return {}
            
        pheromone_data = {}
        for edge, passages in progressive_passages.items():
            if passages > 0:  # Seulement les arêtes avec des passages
                intensity = passages / max_passages  # Normalisation 0-1
                pheromone_data[edge] = {
                    'passages': passages,
                    'intensity': intensity,
                    'width': 1 + intensity * 4,  # Largeur 1-5
                    'alpha': 0.3 + intensity * 0.7  # Transparence 0.3-1.0
                }
        return pheromone_data
    
    def _choose_best_move(self, ant: Ant, available_moves: List[str]) -> Optional[str]:
        """Choisit le meilleur mouvement pour se rapprocher du dortoir"""
        if not available_moves:
            return None
            
        best_move = None
        shortest_distance = float('inf')
        
        for move in available_moves:
            try:
                distance = nx.shortest_path_length(self.graph, move, "Sd")
                if distance < shortest_distance:
                    shortest_distance = distance
                    best_move = move
            except nx.NetworkXNoPath:
                continue
                
        return best_move
    
    def all_ants_arrived(self) -> bool:
        """Vérifie si toutes les fourmis sont arrivées au dortoir"""
        return len(self.room_occupancy.get("Sd", [])) == self.antnest.ants
    
    def solve(self) -> List[List[Tuple[int, str, str]]]:
        """Résout complètement le déplacement des fourmis"""
        while not self.all_ants_arrived():
            movements = self.simulate_step()
            if not movements:
                break
                
        return self.movements_history
    
    def get_visited_rooms(self) -> set:
        """Retourne l'ensemble de toutes les salles visitées pendant la simulation"""
        visited = {'Sv'}  # Le vestibule est toujours visité (point de départ)
        
        for movements in self.movements_history:
            for ant_id, old_room, new_room in movements:
                visited.add(old_room)
                visited.add(new_room)
                
        return visited
    
    def print_solution(self):
        """Affiche la solution sous le format demandé"""
        print(f"=== Solution pour {self.antnest.name} ===")
        print(f"Fourmis: {self.antnest.ants}")
        print()
        
        for step_num, movements in enumerate(self.movements_history, 1):
            if movements:
                print(f"+++ E{step_num} +++")
                for ant_id, old_room, new_room in movements:
                    print(f"f{ant_id} - {old_room} - {new_room}")
                print()
        
        print(f"Toutes les fourmis ont rejoint le dortoir en {len(self.movements_history)} étapes.")
        print()
    
    def visualize_graph(self):
        """Visualise le graphe de la fourmilière avec les traces de phéromones"""
        plt.figure(figsize=(14, 10))
        
        # Position des nœuds
        pos = nx.spring_layout(self.graph, seed=42)
        
        # Couleurs et tailles des nœuds selon l'occupation finale
        final_occupancy = self._get_occupancy_at_step(len(self.movements_history))
        node_colors = []
        node_sizes = []
        
        for node in self.graph.nodes():
            current_ants = len(final_occupancy.get(node, []))
            
            if node == "Sv":
                node_colors.append('lightgreen')
                node_sizes.append(max(1000, 2000 + current_ants * 100))
            elif node == "Sd":
                node_colors.append('lightcoral')  
                node_sizes.append(max(1000, 2000 + current_ants * 100))
            else:
                capacity = self.antnest.rooms.get(node, 1)
                # Taille proportionnelle à la capacité
                base_size = 800 + capacity * 300
                node_sizes.append(base_size + current_ants * 150)
                
                # Couleur selon le ratio occupation/capacité
                ratio = current_ants / capacity if capacity > 0 else 0
                if ratio == 0:
                    node_colors.append('lightblue')
                elif ratio < 0.5:
                    node_colors.append('yellow')
                elif ratio < 1.0:
                    node_colors.append('orange')
                else:
                    node_colors.append('red')
        
        # 🐜 Dessiner les arêtes avec intensité de phéromones
        pheromone_data = self.get_pheromone_data()
        
        # Arêtes normales (sans phéromones)
        normal_edges = []
        for edge in self.graph.edges():
            normalized_edge = tuple(sorted(edge))
            if normalized_edge not in pheromone_data:
                normal_edges.append(edge)
        
        # Dessiner arêtes normales
        if normal_edges:
            nx.draw_networkx_edges(self.graph, pos, edgelist=normal_edges,
                                 edge_color='lightgray', width=1, alpha=0.5)
        
        # Dessiner arêtes avec phéromones
        for edge, data in pheromone_data.items():
            # Convertir tuple ordonné vers edge du graphe
            if edge in self.graph.edges() or (edge[1], edge[0]) in self.graph.edges():
                color_intensity = data['intensity']
                nx.draw_networkx_edges(self.graph, pos, edgelist=[edge],
                                     edge_color='purple', 
                                     width=data['width'],
                                     alpha=data['alpha'])
        
        # Dessiner les nœuds
        nx.draw_networkx_nodes(self.graph, pos,
                             node_color=node_colors,
                             node_size=node_sizes,
                             alpha=0.8)
        
        # Labels avec capacités et occupation
        labels = {}
        for node in self.graph.nodes():
            current_ants = len(final_occupancy.get(node, []))
            if node in self.antnest.rooms:
                capacity = self.antnest.rooms[node]
                labels[node] = f"{node}\n({current_ants}/{capacity})"
            else:
                labels[node] = f"{node}\n({current_ants})"
                
        nx.draw_networkx_labels(self.graph, pos, labels, font_size=9, font_weight='bold')
        
        # Légende pour les phéromones
        if pheromone_data:
            from matplotlib.lines import Line2D
            legend_elements = [
                Line2D([0], [0], color='purple', lw=1, alpha=0.5, label='Peu emprunté'),
                Line2D([0], [0], color='purple', lw=3, alpha=0.8, label='Moyennement emprunté'),
                Line2D([0], [0], color='purple', lw=5, alpha=1.0, label='Très emprunté')
            ]
            plt.legend(handles=legend_elements, loc='upper right')
        
        plt.title(f"Fourmilière: {self.antnest.name} - Traces de Phéromones\n"
                  f"Fourmis: {self.antnest.ants} | Étapes: {len(self.movements_history)} | "
                  f"Chemins empruntés: {len(pheromone_data)}")
        plt.axis('off')
        plt.tight_layout()
        plt.show()
    
    def animate_solution(self):
        """Anime la solution étape par étape"""
        if not self.movements_history:
            print("Aucune solution à animer. Résolvez d'abord la fourmilière.")
            return
            
        for step_num, movements in enumerate(self.movements_history, 1):
            if not movements:
                continue
                
            plt.figure(figsize=(12, 8))
            
            # Position des nœuds
            pos = nx.spring_layout(self.graph, seed=42)
            
            # Couleurs des nœuds selon l'occupation actuelle
            node_colors = []
            node_sizes = []
            
            # Reconstituer l'état à cette étape
            current_occupancy = self._get_occupancy_at_step(step_num)
            
            for node in self.graph.nodes():
                occupants = len(current_occupancy.get(node, []))
                
                if node == "Sv":
                    node_colors.append('green')
                    node_sizes.append(2000 + occupants * 200)
                elif node == "Sd":
                    node_colors.append('red')
                    node_sizes.append(2000 + occupants * 100)
                else:
                    intensity = min(1.0, occupants / self.antnest.rooms.get(node, 1))
                    node_colors.append(plt.cm.Blues(0.3 + intensity * 0.7))
                    node_sizes.append(1500 + occupants * 300)
            
            # Dessiner le graphe
            nx.draw(self.graph, pos, 
                    node_color=node_colors, 
                    node_size=node_sizes,
                    with_labels=False,  # ← Désactiver les labels par défaut 
                    font_size=12, 
                    font_weight='bold',
                    edge_color='gray',
                    width=2)
            
            # Ajouter les labels avec occupation
            labels = {}
            for node in self.graph.nodes():
                occupants = current_occupancy.get(node, [])
                if node in self.antnest.rooms:
                    capacity = self.antnest.rooms[node]
                    labels[node] = f"{node}\n({len(occupants)}/{capacity})"
                else:
                    labels[node] = f"{node}\n({len(occupants)})"
                    
            nx.draw_networkx_labels(self.graph, pos, labels, font_size=10)
            
            # Titre avec les mouvements de cette étape
            movements_text = " | ".join([f"f{ant_id}: {old}->{new}" for ant_id, old, new in movements])
            plt.title(f"Étape {step_num}: {movements_text}\n"
                      f"Fourmilière: {self.antnest.name}")
            
            plt.axis('off')
            plt.tight_layout()
            plt.show()
    
    def _get_occupancy_at_step(self, step_num: int) -> Dict[str, List[int]]:
        """Reconstitue l'occupation des salles à une étape donnée"""
        occupancy = self._init_room_occupancy()
        
        # Appliquer tous les mouvements jusqu'à l'étape donnée
        for step_idx in range(min(step_num, len(self.movements_history))):
            movements = self.movements_history[step_idx]
            for ant_id, old_room, new_room in movements:
                if ant_id in occupancy.get(old_room, []):
                    occupancy[old_room].remove(ant_id)
                if new_room not in occupancy:
                    occupancy[new_room] = []
                occupancy[new_room].append(ant_id)
        
        return occupancy


def load_antnest_from_txt(filepath: str) -> AntNest:
    """
    Charge une fourmilière depuis un fichier texte.
    Format attendu:
    - f=X : nombre de fourmis
    - SX : salle de capacité 1
    - SX { Y } : salle de capacité Y  
    - A - B : tunnel entre A et B
    """
    antnest_name = os.path.splitext(os.path.basename(filepath))[0]
    ants = 0
    rooms = {}
    tubes = []

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith("f="):
                ants = int(line.split("=")[1])
                
            elif "-" in line:
                a, b = [s.strip() for s in line.split("-", 1)]
                tubes.append((a, b))
                
            else:
                match = re.match(r'(\w+)\s*\{\s*(\d+)\s*\}', line)
                if match:
                    room_name, capacity = match.groups()
                    rooms[room_name] = int(capacity)
                else:
                    room_name = line.strip()
                    if room_name:
                        rooms[room_name] = 1

    return AntNest(antnest_name, ants, rooms, tubes)


def solve_antnest(antnest: AntNest) -> AntColony:
    """Fonction utilitaire pour résoudre une fourmilière"""
    colony = AntColony(antnest)
    colony.solve()
    return colony


def test_all_fourmilieres():
    """Test toutes les fourmilières disponibles"""
    fourmilieres_files = [
        "fourmilieres/fourmiliere_zero.txt",
        "fourmilieres/fourmiliere_un.txt", 
        "fourmilieres/fourmiliere_deux.txt",
        "fourmilieres/fourmiliere_trois.txt",
        "fourmilieres/fourmiliere_quatre.txt",
        "fourmilieres/fourmiliere_cinq.txt"
    ]
    
    results = []
    
    for filepath in fourmilieres_files:
        if os.path.exists(filepath):
            print(f"\n🐜 Traitement de {filepath}")
            print("=" * 60)
            
            # Charger
            antnest = load_antnest_from_txt(filepath)
            print(f"Configuration: {antnest.ants} fourmis, {len(antnest.rooms)} salles")
            
            # Résoudre
            colony = solve_antnest(antnest)
            
            # Afficher solution
            colony.print_solution()
            
            # Visualiser (optionnel - commenter si trop d'images)
            colony.visualize_graph()
            
            results.append({
                'name': antnest.name,
                'ants': antnest.ants,
                'steps': len(colony.movements_history),
                'colony': colony
            })
    
    # Résumé
    print("\n" + "="*80)
    print("📊 RÉSUMÉ DES RÉSULTATS")
    print("="*80)
    for result in results:
        print(f"{result['name']:20} | {result['ants']:2} fourmis | {result['steps']:2} étapes")
    
    return results


if __name__ == "__main__":
    print("🐜 UNE VIE DE FOURMI - Résolution des fourmilières")
    print("="*60)
    
    print("Choisissez le mode :")
    print("1. 🎬 Animation simple (RECOMMANDÉ)")
    print("2. 📊 Test complet de toutes les fourmilières")
    print("3. 🎨 Visualisation statique simple")
    
    try:
        choice = input("\nVotre choix (1-3, défaut=1) : ").strip() or "1"
        
        if choice == "1":
            # Animation personnalisée
            print("🎬 Configuration de l'animation")
            print()
            
            # Choix de la fourmilière
            fourmilieres = [
                "fourmiliere_zero.txt",
                "fourmiliere_un.txt", 
                "fourmiliere_deux.txt",
                "fourmiliere_trois.txt",
                "fourmiliere_quatre.txt",
                "fourmiliere_cinq.txt"
            ]
            
            print("Choisissez une fourmilière :")
            for i, f in enumerate(fourmilieres, 1):
                print(f"{i}. {f.replace('_', ' ').replace('.txt', '')}")
            
            fourmiliere_choice = input(f"\nVotre choix (1-{len(fourmilieres)}) : ").strip()
            try:
                fourmiliere_idx = int(fourmiliere_choice) - 1
                if 0 <= fourmiliere_idx < len(fourmilieres):
                    selected_fourmiliere = fourmilieres[fourmiliere_idx]
                else:
                    print("❌ Choix invalide, utilisation de fourmiliere_zero.txt")
                    selected_fourmiliere = "fourmiliere_zero.txt"
            except ValueError:
                print("❌ Choix invalide, utilisation de fourmiliere_zero.txt")
                selected_fourmiliere = "fourmiliere_zero.txt"
            
            # Demander la vitesse
            speed = input("Vitesse d'animation (lent=3, normal=1.5, rapide=0.5, défaut=1.5) : ").strip()
            try:
                delay = float(speed) if speed else 1.5
            except ValueError:
                delay = 1.5
            
            # Lancement de l'animation temps réel
            print(f"🎬 Animation temps réel pour {selected_fourmiliere}")
            antnest = load_antnest_from_txt(f"fourmilieres/{selected_fourmiliere}")
            colony = solve_antnest(antnest)
            
            print(f"Solution trouvée en {len(colony.movements_history)} étapes")
            print("🎬 Démarrage de l'animation...")
            
            # Lancer l'animation simple directement
            try:
                from anime import animation_simple
                animation_simple(f"fourmilieres/{selected_fourmiliere}", delay)
            except ImportError:
                print("❌ Module anime non disponible, utilisation de subprocess...")
                import subprocess  
                subprocess.run(["uv", "run", "python", "anime.py"])
            
        elif choice == "2":
            # Test complet (mode original)
            results = test_all_fourmilieres()
            
        elif choice == "3":
            # Mode simple sans animation
            print("🐜 Exemple simple - Fourmilière zéro")
            antnest = load_antnest_from_txt("fourmilieres/fourmiliere_zero.txt")
            colony = solve_antnest(antnest)
            colony.print_solution()
            colony.print_tunnel_statistics()  # 📊 Statistiques des tunnels
            colony.visualize_graph()
            
        else:
            print("❌ Choix invalide, lancement du mode animation...")
            import subprocess
            subprocess.run(["uv", "run", "python", "anime.py"])
    
    except KeyboardInterrupt:
        print("\n❌ Interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        # Fallback vers le mode simple
        print("🔄 Fallback vers le mode simple...")
        antnest = load_antnest_from_txt("fourmilieres/fourmiliere_zero.txt")
        colony = solve_antnest(antnest)
        colony.print_solution()
        colony.visualize_graph()
    
    print("\n✅ Traitement terminé!")