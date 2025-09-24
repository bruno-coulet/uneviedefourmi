def generate_antNest (file):
    antNest = ""
    ants = 0
    rooms= []
    tubes = []
    with open(file, "r") as f:
        for line in f:
            # Retire tous les espaces blancs
            line = line.strip()
            # S
            # aute le lignes vides, chaîne vide "" → False
            if not line:
                continue
            if line.startswith("f="):
                # converti en int l'élément de la str après le = (index 1)
                ants = int(line.split("=")[1])
            elif " - " in line:
                # Pour chaque morceau autour de " - " enlève les espaces superflus.
                a, b = [s.strip() for s in line.split(" - ")]
                tubes.append((a, b))
            elif "{" in line and "}" in line:
                # extrait les capacités des salles
                for room in line.split(","):
                    room_id, capacity = [s.strip() for s in room.split(":")]
                    rooms.append((int(room_id), int(capacity)))


            