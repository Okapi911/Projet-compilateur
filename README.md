# Projet-compilateur : Objets, fonctions, typage dynamique


## Ce que vous pouvez faire 
#
- Utiliser les opérations élémentaires (addition, soustraction, multiplication).
- Utiliser If et If / else.

```c++
if (condition){
    bloc de commandes : si condition != 0;
}else{
    bloc de commandes : si condition = 0;
}
```

- Utiliser while.

```c++
while (condition){
    bloc de commandes : tant que condition != 0;
}
```

- Utiliser des arguments dans main.

```c++
main(a, b){
    return a + b;
}
```

- Créer des fonctions et les appeler avec des arguments (variables ou non).

```c++
somme(a, b){
    return a + b;
}

main(){
    entier1 = 10;
    entier2 = somme(entier1, 5);
    return entier2;
}
```

- Créer une classe avec un constructeur et définir des attributs.

```c++
class Point{
    Point(entier1, entier2){
        this.x = entier1;
        this.y = entier2;
    }
}
```

- Instancier un objet.

```c++
main() {
    p1 = Point(1, 2);
    return 1;
}
```

- Accéder aux attributs d'un objet (et les utiliser comme arguments).

```c++
main() {
    p1 = Point(1, 2);
    a = p1.x;
    b = somme(a, p1.y);
    return b;
}
```

- Modifier les attributs d'un objet

```c++
main() {
    p1 = Point(1, 2);
    p1.x = 42;
    return p1.x;
}
```

- Attribuer des objets en paramètres d'autres objets et accéder à ses attributs.

```c++
class Arbre{
    Arbre(left, value, right){
        this.left = left;
        this.value = value;
        this.right = right;
    }
}

main(){
    arbre1 = Arbre(Null, 10, Null);
    arbre2 = Arbre(1, 2, 3);
    arbre3 = Arbre(4, 5, 6);

    arbre1.left = arbre2;
    arbre1.right = arbre3;

    return arbre1.right.value;
}
```

- Redéfinir le type d'un objet par affectation.

```c++
main(){

    arbre1 = Arbre(Null, 10, Null);
    b = arbre1.value;

    arbre1 = Point(1, 2);
    c = arbre1.x;

    return b - c;
}
```

## Ce que vous devez faire
#

- Déclarer une fonction main
```c++
main(){
    Bloc de commandes;
    return expression;
}
```

- Déclarer toutes les classes avant les fonctions ; déclarer toutes les fonctions avant le main.
```c++
class c1{
    ...
}

class c2{
    ...
}

f1(){
    ...
}

f2(){
    ...
}

main(){
    return 0;
}
```

## Ce que vous ne devez/pouvez pas faire
#
- Ne pas créer des classes différentes avec des attributs en communs.
- Ne pas instancier d'objets en dehors de la fonction main.
- Ne pas utiliser d'expressions comme arguments d'un(e) fonction / constructeur de classe.
```c++
main(x, y, z){
    a = x * y;
    b = somme(a, z); // et non pas somme(x*y, z);
    return b;
}
```
## Faire fonctionner le compilateur
#
Pour faire fonctionner le compilateur, exécutez le programme python compilo.py avec votre code à l'intérieur. Éxécutez ensuite les commandes suivantes dans un terminal (ici, le fichier asm est appelé par défaut ouf.asm)

- `nasm -f elf64 ouf.asm`
- `gcc -no-pie -fno-pie ouf.o`
- `./a.out [arguments]`

<br/>

## Un exemple utilisant un maximum de fonctionnalités
#

Vous trouverez ci-dessous un exemple fonctionnel qui utilise les principes énoncés précedemment :

```c++
class Point{
    Point(x, y){
        this.x = x;
        this.y = y;
    }
}

class Rectangle{
    Rectangle(point1, point2, point3, point4){
        this.p1 = point1;
        this.p2 = point2;
        this.p3 = point3;
        this.p4 = point4;
    }
}

perimetre(rectangle){
    d1 = rectangle.p2.x - rectangle.p1.x;
    d2 = rectangle.p4.y - rectangle.p1.y;
    return (2*d1) + (2*d2);
}

aire(rectangle){
    d1 = rectangle.p2.x - rectangle.p1.x;
    d2 = rectangle.p4.y - rectangle.p1.y;
    return d1*d2;
}

somme(a, b){
    return a+b;
}

main(){
    p1 = Point(0, 0);
    p2 = Point(3, 0);
    p3 = Point(2, 7);
    p4 = Point(0, 7);

    p3 = Point(3, 7);

    r = Rectangle(p1, p2, p3, p4);

    if (r.p1.x){
        b = somme(r.p4.y, 50);
    }else {
        b = aire(r);
    }

    return b;
}
```
