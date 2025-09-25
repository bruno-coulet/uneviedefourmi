import os

class AntNest:

    def __init__(self, name : str, ants : int, rooms : dict['str', int], tubes : list[tuple[str, str]]):
        '''fonction d'initialisation d'une fourmilière avec :
        - le nom de la fourmilière
        - le nombre de fourmis
        - les salles (dict: id -> capacité)
        - les tunnels (list: tuple: origine -> destination)
        '''
        self.name=name
        self.ants=ants
        self.rooms=rooms
        self.tubes=tubes

    def __str__(self) -> str:
        '''représentation textuelle de la fourmilière'''
        return (
            f"{self.name}\n"
            f"- Fourmis : {self.ants}\n"
            f"- Salles  : {len(self.rooms)} ({self.rooms})\n"
            f"- Tunnels : {len(self.tubes)} {self.tubes}"
        )
    
    def __repr__(self):
        '''
        représentation officielle d’un objet
        est censée être non ambiguë et utile pour les développeurs
        méthode spéciale appelée automatiquement avec : repr(obj)
        ou dans le shell
        '''

        return f"AntNest( antnest={self.name}, ants={self.ants}, rooms={self.rooms}, tubes={self.tubes})"

def generate_antNest(file):
    # extrait le deuxième élément du nom de fichier
    basename = os.path.basename(file)
    antNest = basename.split("_")[1] if "_" in basename else basename

    ants = 0
    rooms = {}   # dictionnaire roomId -> roomCapacity
    tubes = []

    with open(file, "r") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue

            # nombre de fourmis
            if line.startswith("f="):
                ants = int(line.split("=")[1])


            # tunnels
            elif " - " in line:
                a, b = [s.strip() for s in line.split(" - ", 1)]
                tubes.append((a, b))

            # salles avec accolades {capacité}
            elif "{" in line and "}" in line:
                big_room = line.replace("{", "").replace("}", "").strip()
                if big_room:
                    parts = big_room.split()
                    if len(parts) == 2:
                        roomId, roomCapacity = parts[0], int(parts[1])
                    rooms[roomId] = roomCapacity

            # salle simple, capacité par défaut = 1
            elif line.startswith("S") and all(x not in line for x in ("{", "}", "-")):
                rooms[line] = 1

    rooms_count = len(rooms)

    # print(f"Fourmilière {antNest} : {ants} fourmis, {rooms_count} salles, {len(tubes)} , détails des salles: {rooms}  ")
    return antNest, ants, rooms, tubes

            