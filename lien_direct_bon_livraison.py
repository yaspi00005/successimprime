#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pour une ligne "En livraison" qui ne vient pas d'une vente directe
(donc pas de bouton "Marquer comme livre" possible sur la ligne :
elle doit passer par son bon de livraison), le bouton reel se trouve
sur la page du bon de livraison lui-meme (section "Bons de livraison"
en bas de la fiche commande, ou le bouton "Confirmer la livraison"
du bon quand il est valide).

Ce script ajoute un lien direct vers cette section pour ne plus avoir
a la chercher :
- sur la fiche commande (bouton grise -> lien cliquable qui descend
  vers "Bons de livraison") ;
- sur l'ancienne fiche par ligne (message d'avertissement -> lien
  "Voir les bons de livraison de cette commande").

Executer depuis la racine du projet :
    python3 lien_direct_bon_livraison.py
"""

import sys


def appliquer(chemin, ancien, nouveau, label):
    try:
        with open(chemin, "r", encoding="utf-8") as f:
            contenu = f.read()
    except FileNotFoundError:
        print(f"[ERREUR] Fichier introuvable : {chemin}")
        return False

    if nouveau in contenu:
        print(f"[SKIP] {label} : deja applique.")
        return True

    occurrences = contenu.count(ancien)

    if occurrences != 1:
        print(
            f"[ERREUR] {label} : {occurrences} occurrence(s) trouvee(s) "
            f"dans {chemin} (1 attendue)"
        )
        return False

    contenu = contenu.replace(ancien, nouveau)

    with open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)

    print(f"[OK] {label}")
    return True


resultats = []

resultats.append(appliquer(
    "templates/livraisons/show_commande.html.twig",
'{% else %}\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t<span class="btn btn-sm btn-light disabled" title="À livrer depuis le bon de livraison">\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t<i class="fa fa-file-text-o"></i>\n\t\t\t\t\t\t\t\t\t\t\t\t\t</span>\n\n\t\t\t\t\t\t\t\t\t\t\t\t{% endif %}',
'{% else %}\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t<a href="#bons-de-livraison" class="btn btn-sm btn-warning-light" title="Cette ligne se livre depuis son bon de livraison, ci-dessous">\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t<i class="fa fa-file-text-o"></i>\n\t\t\t\t\t\t\t\t\t\t\t\t\t</a>\n\n\t\t\t\t\t\t\t\t\t\t\t\t{% endif %}',
    "1) show_commande.html.twig : lien vers le bon de livraison (au lieu du bouton grise)",
))

resultats.append(appliquer(
    "templates/livraisons/show_commande.html.twig",
'\t\t<div class="card">\n\n\t\t\t<div class="card-header',
'\t\t<div class="card" id="bons-de-livraison">\n\n\t\t\t<div class="card-header',
    "2) show_commande.html.twig : ancre #bons-de-livraison",
))

resultats.append(appliquer(
    "templates/livraisons/show.html.twig",
'{% else %}\n\n\t\t\t\t\t\t\t\t<div class="alert alert-warning mb-0">\n\n\t\t\t\t\t\t\t\t\t<i class="fa fa-truck mr-1"></i>\n\n\t\t\t\t\t\t\t\t\tCette ligne doit être livrée\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t            depuis son bon de livraison.',
'{% else %}\n\n\t\t\t\t\t\t\t\t<div class="alert alert-warning mb-0">\n\n\t\t\t\t\t\t\t\t\t<i class="fa fa-truck mr-1"></i>\n\n\t\t\t\t\t\t\t\t\tCette ligne doit être livrée\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t            depuis son bon de livraison.\n\n\t\t\t\t\t\t\t\t\t{% if commande %}\n\t\t\t\t\t\t\t\t\t\t<a href="{{ path(\'app_livraisons_commande\', { id: commande.id }) }}#bons-de-livraison" class="alert-link d-block mt-2">\n\t\t\t\t\t\t\t\t\t\t\t<i class="fa fa-file-text-o mr-1"></i>\n\t\t\t\t\t\t\t\t\t\t\tVoir les bons de livraison de cette commande\n\t\t\t\t\t\t\t\t\t\t</a>\n\t\t\t\t\t\t\t\t\t{% endif %}',
    "3) show.html.twig (fiche par ligne) : lien vers les bons de livraison",
))


echecs = resultats.count(False)

print()
if echecs:
    print(f"Termine avec {echecs} erreur(s). Voir les [ERREUR] ci-dessus.")
    sys.exit(1)
else:
    print("Termine sans erreur.")
