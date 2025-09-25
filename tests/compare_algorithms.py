#!/usr/bin/env python3
"""
Comparaison entre l'ancien et le nouveau algorithme
"""

import os
import time
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import networkx as nx

# Classe AntNest partagée
class AntNest:
    def __init__(self, name: str, ants: int, rooms: dict[str, int], tubes: list[tuple[str, str]]):
        self.name = name
        self.ants = ants
        self.rooms = rooms
        self.tubes = tubes

@dataclass
class Ant:
    id: int
    current_room: str

def load_antnest_from_txt(filepath: str) -> AntNest:
    """Charge une fourmilière depuis un fichier texte"""
    import re
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

# ANCIEN ALGORITHME (séquentiel)
class AntColonyOld:
    def __init__(self, antnest):
        self.antnest = antnest
        self.graph = nx.Graph()
        self.graph.add_edges_from(antnest.tubes)
        self.ants = [Ant(i+1, "Sv") for i in range(antnest.ants)]
        self.room_occupancy = self._init_room_occupancy()
        self.step_count = 0
        self.movements_history = []
        
    def _init_room_occupancy(self):
        occupancy = {room: [] for room in self.antnest.rooms.keys()}
        occupancy["Sv"] = [ant.id for ant in self.ants]
        occupancy["Sd"] = []
        return occupancy
    
    def get_available_moves(self, ant: Ant) -> List[str]:
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
        movements = []
        
        # ANCIEN: Traitement séquentiel simple
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
        return len(self.room_occupancy.get("Sd", [])) == self.antnest.ants
    
    def solve(self) -> List[List[Tuple[int, str, str]]]:
        while not self.all_ants_arrived():
            movements = self.simulate_step()
            if not movements:
                break
        return self.movements_history

# NOUVEAU ALGORITHME (simultané)
class AntColonyNew:
    def __init__(self, antnest):
        self.antnest = antnest
        self.graph = nx.Graph()
        self.graph.add_edges_from(antnest.tubes)
        self.ants = [Ant(i+1, "Sv") for i in range(antnest.ants)]
        self.room_occupancy = self._init_room_occupancy()
        self.step_count = 0
        self.movements_history = []
        
    def _init_room_occupancy(self):
        occupancy = {room: [] for room in self.antnest.rooms.keys()}
        occupancy["Sv"] = [ant.id for ant in self.ants]
        occupancy["Sd"] = []
        return occupancy
    
    def get_available_moves(self, ant: Ant) -> List[str]:
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
    
    def _choose_best_move(self, ant: Ant, available_moves: List[str]) -> Optional[str]:
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

    def simulate_step(self) -> List[Tuple[int, str, str]]:
        movements = []
        planned_moves = []
        
        # Phase 1: Planifier tous les mouvements possibles
        for ant in self.ants:
            if ant.current_room == "Sd":
                continue
                
            available_moves = self.get_available_moves(ant)
            
            if "Sd" in available_moves:
                planned_moves.append((ant, ant.current_room, "Sd"))
            else:
                best_move = self._choose_best_move(ant, available_moves)
                if best_move:
                    planned_moves.append((ant, ant.current_room, best_move))
        
        # Phase 2: Résoudre les conflits
        valid_moves = self._resolve_movement_conflicts(planned_moves)
        
        # Phase 3: Exécuter les mouvements
        for ant, old_room, new_room in valid_moves:
            if self._execute_move(ant, old_room, new_room):
                movements.append((ant.id, old_room, new_room))
        
        self.step_count += 1
        self.movements_history.append(movements)
        return movements
    
    def _resolve_movement_conflicts(self, planned_moves):
        valid_moves = []
        room_destinations = {}
        room_departures = {}
        
        for ant, old_room, new_room in planned_moves:
            if new_room not in room_destinations:
                room_destinations[new_room] = []
            room_destinations[new_room].append((ant, old_room, new_room))
            
            if old_room not in room_departures:
                room_departures[old_room] = []
            room_departures[old_room].append((ant, old_room, new_room))
        
        for destination, moves_to_dest in room_destinations.items():
            if destination in ["Sd", "Sv"]:
                valid_moves.extend(moves_to_dest)
            elif destination in self.antnest.rooms:
                capacity = self.antnest.rooms[destination]
                current_occupants = len(self.room_occupancy.get(destination, []))
                departing_from_dest = len(room_departures.get(destination, []))
                available_spots = capacity - current_occupants + departing_from_dest
                valid_moves.extend(moves_to_dest[:available_spots])
        
        return valid_moves
    
    def _execute_move(self, ant, old_room, new_room) -> bool:
        if old_room in self.room_occupancy:
            if ant.id in self.room_occupancy[old_room]:
                self.room_occupancy[old_room].remove(ant.id)
        
        if new_room not in self.room_occupancy:
            self.room_occupancy[new_room] = []
        self.room_occupancy[new_room].append(ant.id)
        
        ant.current_room = new_room
        return True
    
    def all_ants_arrived(self) -> bool:
        return len(self.room_occupancy.get("Sd", [])) == self.antnest.ants
    
    def solve(self) -> List[List[Tuple[int, str, str]]]:
        while not self.all_ants_arrived():
            movements = self.simulate_step()
            if not movements:
                break
        return self.movements_history

def compare_algorithms():
    """Compare les deux algorithmes"""
    fourmilieres = [
        "fourmilieres/fourmiliere_zero.txt",
        "fourmilieres/fourmiliere_un.txt", 
        "fourmilieres/fourmiliere_deux.txt",
        "fourmilieres/fourmiliere_trois.txt",
        "fourmilieres/fourmiliere_quatre.txt",
        "fourmilieres/fourmiliere_cinq.txt"
    ]
    
    print("🔍 COMPARAISON DES ALGORITHMES")
    print("=" * 80)
    print(f"{'Fourmilière':<15} {'Fourmis':<8} {'Ancien':<8} {'Nouveau':<8} {'Diff':<8} {'Résultat'}")
    print("-" * 80)
    
    for filepath in fourmilieres:
        try:
            # Charger
            antnest = load_antnest_from_txt(filepath)
            
            # Test ancien algorithme
            colony_old = AntColonyOld(antnest)
            colony_old.solve()
            old_steps = len(colony_old.movements_history)
            
            # Test nouveau algorithme  
            colony_new = AntColonyNew(antnest)
            colony_new.solve()
            new_steps = len(colony_new.movements_history)
            
            # Comparaison
            diff = new_steps - old_steps
            if diff > 0:
                result = f"❌ +{diff}"
            elif diff < 0:
                result = f"✅ {diff}"
            else:
                result = "➖ =0"
            
            name = antnest.name.replace("fourmiliere_", "").title()
            print(f"{name:<15} {antnest.ants:<8} {old_steps:<8} {new_steps:<8} {diff:<8} {result}")
            
        except Exception as e:
            print(f"❌ Erreur avec {filepath}: {e}")

if __name__ == "__main__":
    compare_algorithms()