'''
résolution des fourmilières.
'''

import networkx as nx
import matplotlib.pyplot as plt
import os
from utils import generate_antNest

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

ant_nest_objects = []


# Crée une liste d'objets fourmilières à partir des fichiers dans le dossier "fourmilieres"
for file in os.listdir("fourmilieres"):
    if file.endswith(".txt"):
        # chemin complet
        filepath = os.path.join("fourmilieres", file)
        # appele generate_antNest
        antNest_name, ants, rooms_dict, tubes = generate_antNest(filepath)
        # modifie le nom : ajoute "fourmilière " et supprime l'extension .txt
        antNest_name = f"fourmilière {os.path.splitext(antNest_name)[0]}"
        # Crée l'objet
        nest = AntNest(antNest_name, ants, rooms_dict, tubes)
        ant_nest_objects.append(nest)

# Affichage de toutes les fourmilières
for nest in ant_nest_objects:
    # print(nest)
    G = nx.Graph()
    G.add_edges_from(nest.tubes)
    nx.draw(G, with_labels=True)
    plt.show()


# f1 = generate_antNest("fourmilieres/fourmiliere_un.txt")
# f2 = generate_antNest("fourmilieres/fourmiliere_deux.txt")
# f3 = generate_antNest("fourmilieres/fourmiliere_trois.txt")
# f4 = generate_antNest("fourmilieres/fourmiliere_quatre.txt")
# f5 = generate_antNest("fourmilieres/fourmiliere_cinq.txt")


# F5 = AntNest(*f5)
# print(F5)


# # Exemple d’utilisation - fourmilière 1
# f1 = AntNest("fourmilière 1", 2, {1: 1, 2: 1}, ['v-s1','v-s2', 's1-d', 's2-d'] )
# print(f1)  # Appelle automatiquement __str__


# G = nx.Graph()
# G.add_edges_from(edge_list_4)
# nx.draw(G, with_labels=True)
# plt.show()




 
   

# Exemple d’utilisation
# f5 = load_antnest_from_txt("fourmilieres/fourmiliere_quatre.txt")
# print(f5)

