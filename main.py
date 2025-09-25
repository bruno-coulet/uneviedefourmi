'''
résolution des fourmilières.
'''

import networkx as nx
import matplotlib.pyplot as plt
import os
from utils import generate_antNest


''' représenter la fourmilière sous forme de graphe en utilisant la
librairie/module de votre choix'''

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


'''afficher l’ensemble des étapes nécessaires comme cela :
+++ 𝐸1+++
𝑓1 − 𝑆𝑣 − 𝑆1
𝑓2 − 𝑆𝑣 − 𝑆2
+++𝐸2+++
𝑓1 − 𝑆1 − 𝑆𝑑
𝑓2 − 𝑆2 − 𝑆𝑑
𝑓3 − 𝑆v − 𝑆1
+++ 𝐸3+++
𝑓3 − 𝑆1 − 𝑆𝑑
'''






 
   

# Exemple d’utilisation
# f5 = load_antnest_from_txt("fourmilieres/fourmiliere_quatre.txt")
# print(f5)

