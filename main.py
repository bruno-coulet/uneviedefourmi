'''
résolution des fourmilières.
'''

import networkx as nx
import matplotlib.pyplot as plt

#  undirected graph
G = nx.Graph()
#  directed graph : de A vers B versus de B vers A
G = nx.DiGraph()

# ajouter une arête qui va de A à B, cela créa uassi les sommet s'ils n'existent pas encore
G.add_edge('A', 'B')


class AntNest:

    def __init__(self, name : str, ants : int, rooms : dict[int, int], tubes : list[tuple[str, str]]):
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


# exemple d’utilisation - fourmilière 1
f1 = AntNest("fourmilière 1", 2, {1: 1, 2: 1}, ['v-s1','v-s2', 's1-d', 's2-d'] )
print(f1)  # Appelle automatiquement __str__

# fourmilière 4 COMMENT ON GERE LES FORMIS ET LES CAPACITES DES SALLES ?
edge_list_4 = [(3,4), ("v",1), (1,2), (2,4), (4,5) ,(5,"d"), (4,6), (6,"d"), (1,3)]

G = nx.Graph()
G.add_edges_from(edge_list_4)
nx.draw(G, with_labels=True)
plt.show()




#  Ci dessous, Chat GPT A DECORTIQUER
def load_antnest_from_txt(filepath: str) -> AntNest:
    antNestName = ""
    ants = 0
    rooms = []
    tubes = []

    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line:  # sauter les lignes vides
                continue
            if line.startswith("f="):
                ants = int(line.split("=")[1])
            elif "-" in line:
                a, b = [s.strip() for s in line.split("-")]
                tubes.append((a, b))
            else:
                rooms.append(line)

    return AntNest(ants, rooms, tubes)

# Exemple d’utilisation
# f5 = load_antnest_from_txt("fourmilieres/fourmiliere_quatre.txt")
# print(f5)

