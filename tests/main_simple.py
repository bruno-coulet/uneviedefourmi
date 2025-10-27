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
        """Simule une étape de déplacement et retourne les mouvements effectués"""
        movements = []
        
        for ant in self.ants:
            if ant.current_room == "Sd":
                continue
                
            available_moves = self.get_available_moves(ant)
            
            if "Sd" in available_moves:
                old_room = ant.current_room
                if self.move_ant(ant, "Sd"):
                    movements.append((ant.id, old_room, "Sd"))
            else:
                best_move = self._choose_best_move(ant, available_moves)
                if best_move:
                    old_room = ant.current_room
                    if self.move_ant(ant, best_move):
                        movements.append((ant.id, old_room, best_move))
        
        self.step_count += 1
        self.movements_history.append(movements)
        return movements
    
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
        """Visualise le graphe de la fourmilière"""
        plt.figure(figsize=(12, 8))
        
        pos = nx.spring_layout(self.graph, seed=42)
        
        node_colors = []
        node_sizes = []
        for node in self.graph.nodes():
            if node == "Sv":
                node_colors.append('green')
                node_sizes.append(2000)
            elif node == "Sd":
                node_colors.append('red')
                node_sizes.append(2000)
            else:
                node_colors.append('lightblue')
                node_sizes.append(1500)
        
        nx.draw(self.graph, pos, 
                node_color=node_colors, 
                node_size=node_sizes,
                with_labels=True, 
                font_size=12, 
                font_weight='bold',
                edge_color='gray',
                width=2)
        
        labels = {}
        for node in self.graph.nodes():
            if node in self.antnest.rooms:
                capacity = self.antnest.rooms[node]
                labels[node] = f"{node}\n({capacity})"
            else:
                labels[node] = node
                
        nx.draw_networkx_labels(self.graph, pos, labels, font_size=10)
        
        plt.title(f"Fourmilière: {self.antnest.name}\n"
                  f"Fourmis: {self.antnest.ants} | "
                  f"Salles: {len(self.antnest.rooms)} | "
                  f"Tunnels: {len(self.antnest.tubes)}")
        plt.axis('off')
        plt.tight_layout()
        plt.show()


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


if __name__ == "__main__":
    print("🐜 UNE VIE DE FOURMI - Résolution des fourmilières")
    print("="*60)
    
    # Test avec fourmilière simple
    print("🐜 Exemple: Fourmilière zéro (2 fourmis)")
    antnest = load_antnest_from_txt("fourmilieres/fourmiliere_zero.txt")
    colony = solve_antnest(antnest)
    colony.print_solution()
    colony.visualize_graph()
    
    print("\n" + "="*60)
    print("✅ Pour tester toutes les fourmilières, lancez main_complete.py")