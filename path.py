import networkx as nx
import matplotlib.pyplot as plt
import os
from utils import generate_antNest, AntNest

antNest_name, ants, rooms_dict, tubes = generate_antNest("fourmilieres/fourmiliere_cinq.txt")
nest = AntNest(antNest_name, ants, rooms_dict, tubes)

G = nx.Graph()
G.add_edges_from(nest.tubes)
nx.draw(G, with_labels=True)
plt.show()

path = nx.shortest_path(G, "Sv", "Sd")
print(path)


'''Ci dessous Chat GPT'''
from collections import defaultdict
# Pré-calculer les chemins
paths = {f"f{i+1}": nx.shortest_path(G, "Sv", "Sd") for i in range(nest.ants)}

# Initialiser les états
positions = {f"f{i+1}": "Sv" for i in range(nest.ants)}

step = 0
while not all(pos == "Sd" for pos in positions.values()):
    step += 1
    print(f"\n+++ É{step} +++")

    new_positions = positions.copy()

    for ant, path in paths.items():
        if positions[ant] != "Sd":  # si pas déjà arrivé
            current_idx = path.index(positions[ant])
            next_room = path[current_idx + 1]

            # vérifier capacité
            if list(new_positions.values()).count(next_room) < nest.rooms[next_room]:
                new_positions[ant] = next_room  # la fourmi avance
            # sinon, elle attend

    positions = new_positions

    # Affichage
    for ant, room in positions.items():
        print(f"{ant} - {room}")

'''
Exemple de sortie attendue

+++ É1 +++
f1 - S1
f2 - S2
f3 - Sv

+++ É2 +++
f1 - Sd
f2 - Sd
f3 - S1

+++ É3 +++
f3 - Sd
''''''