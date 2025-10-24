# Une vie de fourmi
Algorithmique, python, graphs, NetworkX


## Veille sur les **graphes**

Représente des relations entre des éléments (sommets)
Arête = relation entre 2 sommets
Se compose de zéro ou une arête entre chaque sommets

|Anglais|Français|
|-|-|
|node | sommet|
|edge | arête|

---
**voisins**
2 sommets sont voisins s'il sont relié par une arête
<img src=img/voisins.png width=400>

---
**degre**
Nombre de voisin d'un sommet
deg(sommet)=3 le sommet à 3 voisins

---
**chemin**
nombre d'arêtes qui relient 2 sommet
1 arête : chemin de longueur 1
2 arêtes : chemin de longueur 2
etc...

---
**cycle**
chemein dont les 2 extremité sont relié
(boucle)

<img src=img/cycle.png width=400>
<img src=img/cycle_3.png width=400>
<img src=img/cycle_6.png width=400>

---
**Graphe complet**
contient toutes les arêtes possibles entre tous les sommets

<img src=img/graphe_complet.png width=300>

---
**Graphe connexe**
Pour tout ``u`` et ``v``, le graphe est connexe s'il contient un chemin entre `u` et `v`

<img src=img/graphe_non_convexe.png width=300>

---
**arbre**
graphe **connexe** et **sans cycle**

<img src=img/arbre.png width=200>
<img src=img/arbre_etoile.png width=200>
<img src=img/arbre_chemin.png width=200>
<img src=img/non_arbre.png width=200>

**Relation entre connexité et arbre**
Un graphe est connexe si et seulement si il contient un arbre couvrant
cad que si on supprime certain arête, on obtient un arbre

**Somme des degrés**
En général :
Somme des degrés = 2 * le nombre d'arêtes du graphe


## problématique

➔ représenter la fourmilière sous forme de graphe en utilisant la
librairie/module de votre choix.
➔ afficher l’ensemble des étapes nécessaires au déplacement des
fourmis, comme montré ici :

+++ E1+++
f1 − Sv − S1
f2 − Sv − S2
+++E2+++
f1 − S1 − Sd
f2 − S2 − Sd
f3 − Sv − S1
+++ E3+++
f3 − S1 − Sd

➔ représenter par un graphique le déplacement des fourmis au sein de la
fourmilière, étape par étape.


## les solutions apportées

````shell
pip install networkx
````

[Tutoriel NetworkX](https://networkx.org/documentation/stable/tutorial.html)

**Undirected graph**
```python
G = nx.Graph()
```
**Directed graph : de A vers B versus de B vers A**
```python
G = nx.DiGraph()
```
**Ajouter une arête qui va de A à B**
cela crée aussi les sommets s'ils n'existent pas encore
```python
G.add_edge('A', 'B')
```

[Matrice d'adjacence](https://people.revoledu.com/kardi/tutorial/GraphTheory/Adjacency-Matrix.html)

## conclusion
