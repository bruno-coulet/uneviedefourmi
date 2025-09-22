# Une vie de fourmi
Algorithmique, python, graphs, NetworkX


## Veille sur kes graphes

Représente des relations entre des élémentsSe compose de zéro ou une arrrêter entre chaque sommets

**voisins**
2 sommets sont voisins s'il sont relié par une arrête
[voisin](img/voisins.png)

**degre**
Nombre de voisin d'un sommet
deg(sommet)=3 le sommet à 3 voisins

**chemin**
nombre d'arrêtes qui relient 2 sommet
1 arrête : chemin de longueur 1
2 arrêtes : chemin de longueur 2
etc...

**cycle**
chemein dont les 2 extremité sont relié
(boucle)

[cycle](img/cycle.png)
[cycle](img/cycle_3.png)
[cycle](img/cycle_6.png)


**Graphe complet**
contient toutes les arrêtes possibles entre tous les sommets

[complet](img/graphe_complet.png)

**Graphe connexe**
Pour tout u et vle graphe contient un chemin entre u et v

[Graphe non connexe](img/graphe_non_convexe.png)

**arbre**
graphe connexe et sans cycle

[arbre](img/arbre.png)
[arbre](img/arbre_etoile.png)
[arbre](img/arbre_chemin.png)

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
[Tutoriel NetworkX](https://networkx.org/documentation/stable/tutorial.html)

[Matrice d'adjacence](https://people.revoledu.com/kardi/tutorial/GraphTheory/Adjacency-Matrix.html)

## conclusion
