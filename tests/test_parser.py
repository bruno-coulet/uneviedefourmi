'''
Test de la fonction de parsing des fourmilières
'''

import os
import re


class AntNest:
    def __init__(self, name: str, ants: int, rooms: dict[str, int], tubes: list[tuple[str, str]]):
        self.name = name
        self.ants = ants
        self.rooms = rooms
        self.tubes = tubes

    def __str__(self) -> str:
        return (
            f"{self.name}\n"
            f"- Fourmis : {self.ants}\n"
            f"- Salles  : {len(self.rooms)} ({self.rooms})\n"
            f"- Tunnels : {len(self.tubes)} {self.tubes}"
        )


def load_antnest_from_txt(filepath: str) -> AntNest:
    """
    Charge une fourmilière depuis un fichier texte.
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


if __name__ == "__main__":
    # Test fourmilière zéro
    print("=== Test fourmilière zéro ===")
    f0 = load_antnest_from_txt("fourmilieres/fourmiliere_zero.txt")
    print(f0)
    print()

    # Test fourmilière quatre
    print("=== Test fourmilière quatre ===")
    f4 = load_antnest_from_txt("fourmilieres/fourmiliere_quatre.txt")
    print(f4)
    print()

    # Test fourmilière cinq (avec capacités)
    print("=== Test fourmilière cinq ===")
    f5 = load_antnest_from_txt("fourmilieres/fourmiliere_cinq.txt")
    print(f5)