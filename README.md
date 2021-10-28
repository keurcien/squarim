# Squarim API

## 1. Stretch

À utiliser uniquement pour des images à fond uni dont la largeur est inférieure à la hauteur.

### Avec une l'URL d'une image

```javascript
let data = new FormData();
data.append("name", "exemple.jpg");
data.append("left", 50);
data.append("right", 50); 
data.append("file", "http://...exemple.jpg");
data.append("mirror", false)

const response = await fetch("https://squarim-f5ljwmnzga-ew.a.run.app/", {
    method: "POST",
    body: data
})
```

### Avec une image encodée en base64

```javascript
let data = new FormData();
data.append("name", "exemple.jpg");
data.append("left", 50);
data.append("right", 50); 
data.append("file", "data:image/jpeg;base64,iVBORw0KGgoAAAANSUhEU...");
data.append("mirror", false)

const response = await fetch("https://squarim-f5ljwmnzga-ew.a.run.app/", {
    method: "POST",
    body: data
})
```
