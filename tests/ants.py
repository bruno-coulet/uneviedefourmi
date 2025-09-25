'''
différentes classes et fonctions
permettant le bon déplacement des fourmis au sein de la
fourmilière.
'''

from typing import List, Dict, Tuple, Optional
import networkx as nx
from dataclasses import dataclass


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
        self.ants = [Ant(i+1, "Sv") for i in range(antnest.ants)]  # Toutes les fourmis commencent au vestibule
        self.room_occupancy = self._init_room_occupancy()
        self.step_count = 0
        self.movements_history = []  # Historique des mouvements
        
    def _create_graph(self) -> nx.Graph:
        """Crée un graphe NetworkX à partir des tunnels"""
        G = nx.Graph()
        G.add_edges_from(self.antnest.tubes)
        return G
    
    def _init_room_occupancy(self) -> Dict[str, List[int]]:
        """Initialise l'occupation des salles"""
        occupancy = {room: [] for room in self.antnest.rooms.keys()}
        occupancy["Sv"] = [ant.id for ant in self.ants]  # Vestibule : toutes les fourmis
        occupancy["Sd"] = []  # Dortoir vide au début
        return occupancy
    
    def get_available_moves(self, ant: Ant) -> List[str]:
        """Retourne les salles où une fourmi peut se déplacer"""
        current_room = ant.current_room
        available_rooms = []
        
        # Obtenir les voisins dans le graphe
        neighbors = list(self.graph.neighbors(current_room))
        
        for room in neighbors:
            if room == "Sd":  # Le dortoir peut toujours accueillir des fourmis
                available_rooms.append(room)
            elif room in self.antnest.rooms:
                # Vérifier si la salle a encore de la place
                capacity = self.antnest.rooms[room]
                current_occupants = len(self.room_occupancy.get(room, []))
                if current_occupants < capacity:
                    available_rooms.append(room)
            elif room == "Sv":  # Vestibule peut toujours accueillir (mais on veut en sortir)
                available_rooms.append(room)
                
        return available_rooms
    
    def move_ant(self, ant: Ant, destination: str) -> bool:
        """Déplace une fourmi vers la destination si possible"""
        if destination not in self.get_available_moves(ant):
            return False
            
        # Retirer la fourmi de sa position actuelle
        if ant.current_room in self.room_occupancy:
            if ant.id in self.room_occupancy[ant.current_room]:
                self.room_occupancy[ant.current_room].remove(ant.id)
        
        # Ajouter la fourmi à sa nouvelle position
        if destination not in self.room_occupancy:
            self.room_occupancy[destination] = []
        self.room_occupancy[destination].append(ant.id)
        
        # Mettre à jour la position de la fourmi
        old_room = ant.current_room
        ant.current_room = destination
        
        return True
    
    def simulate_step(self) -> List[Tuple[int, str, str]]:
        """Simule une étape de déplacement et retourne les mouvements effectués"""
        movements = []
        
        # Stratégie simple : déplacer les fourmis le plus près possible du dortoir
        for ant in self.ants:
            if ant.current_room == "Sd":
                continue  # Fourmi déjà arrivée
                
            available_moves = self.get_available_moves(ant)
            
            if "Sd" in available_moves:
                # Si le dortoir est accessible, y aller directement
                old_room = ant.current_room
                if self.move_ant(ant, "Sd"):
                    movements.append((ant.id, old_room, "Sd"))
            else:
                # Sinon, choisir le meilleur mouvement (vers le dortoir via le chemin le plus court)
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
            
        # Calculer le chemin le plus court vers Sd depuis chaque mouvement possible
        best_move = None
        shortest_distance = float('inf')
        
        for move in available_moves:
            try:
                # Distance depuis le mouvement potentiel vers Sd
                distance = nx.shortest_path_length(self.graph, move, "Sd")
                if distance < shortest_distance:
                    shortest_distance = distance
                    best_move = move
            except nx.NetworkXNoPath:
                continue  # Pas de chemin possible
                
        return best_move
    
    def all_ants_arrived(self) -> bool:
        """Vérifie si toutes les fourmis sont arrivées au dortoir"""
        return len(self.room_occupancy.get("Sd", [])) == self.antnest.ants
    
    def solve(self) -> List[List[Tuple[int, str, str]]]:
        """Résout complètement le déplacement des fourmis"""
        while not self.all_ants_arrived():
            movements = self.simulate_step()
            if not movements:  # Aucun mouvement possible, éviter boucle infinie
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
            if movements:  # N'afficher que les étapes avec des mouvements
                print(f"+++ E{step_num} +++")
                for ant_id, old_room, new_room in movements:
                    print(f"f{ant_id} - {old_room} - {new_room}")
                print()
        
        print(f"Toutes les fourmis ont rejoint le dortoir en {len(self.movements_history)} étapes.")
        print()


def solve_antnest(antnest) -> AntColony:
    """Fonction utilitaire pour résoudre une fourmilière"""
    colony = AntColony(antnest)
    colony.solve()
    return colony