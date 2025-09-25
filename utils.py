import os

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

            