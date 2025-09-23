'''
résolution des fourmilières.
'''

import networkx as nx
import matplotlib.pyplot as plt

#  undirefted graph
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
        return f"AntNest(ants={self.ants}, rooms={self.rooms}, tubes={self.tubes})"



f1 = AntNest("fourmilière 1", 2, {1: 1, 2: 1}, ['v-s1','v-s2', 's1-d', 's2-d'] )



print(f1)  # Appelle automatiquement __str__

