"""
Évite de générer une miniature pour une image trop volumineuse
(grosse photo, scan haute résolution...).

Même avec URL.createObjectURL() (au lieu de readAsDataURL()), le
navigateur doit décoder l'image entière (dimensions réelles) pour
en afficher une simple vignette 40x40 — ce décodage peut geler la
page un instant sur une très grosse image. Au-delà de 8 Mo, on
affiche directement l'icône générique de fichier, sans tenter
d'aperçu.

Modifie :
- templates/commandes/_form.html.twig

A executer a la racine du dépôt : python3 limiter_apercu_grosses_images.py
"""

import sys

path = "templates/commandes/_form.html.twig"

old = """function creerLigneUpload(fichier) {
const ligne = document.createElement('div');

ligne.className = 'd-flex align-items-center border rounded p-2 mb-2 js-upload-ligne';

const estImage = fichier.type && fichier.type.indexOf('image/') === 0;

const apercu = document.createElement(estImage ? 'img' : 'i');

if (estImage) {"""

new = """/*
 * Au-dela de cette taille, on n'essaie plus de generer d'apercu
 * miniature pour une image : meme via createObjectURL(), le
 * navigateur doit decoder toute l'image (largeur/hauteur reelles)
 * pour en afficher ne serait-ce qu'une vignette 40x40, ce qui peut
 * geler la page un instant sur une tres grosse photo/scan.
 */
const LIMITE_APERCU_IMAGE = 8 * 1024 * 1024;

function creerLigneUpload(fichier) {
const ligne = document.createElement('div');

ligne.className = 'd-flex align-items-center border rounded p-2 mb-2 js-upload-ligne';

const estImage = fichier.type
&& fichier.type.indexOf('image/') === 0
&& fichier.size <= LIMITE_APERCU_IMAGE;

const apercu = document.createElement(estImage ? 'img' : 'i');

if (estImage) {"""

with open(path, encoding="utf-8") as f:
    content = f.read()

if new in content:
    print("Déjà présent - rien à faire.")
else:
    count = content.count(old)
    if count != 1:
        print(f"[ERREUR] {count} occurrence(s) trouvée(s) (1 attendue)")
        sys.exit(1)

    content = content.replace(old, new)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    print("OK - apercu desactive au-dela de 8 Mo pour les images.")
