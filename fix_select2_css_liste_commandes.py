#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrige l'affichage casse des listes deroulantes (Client, Statut,
Etat, Paiement...) sur la page Liste des commandes.

Cause : Select2 a ete active sur ces listes, mais sa feuille de style
(select2.min.css) n'etait chargee que sur les pages de formulaire
commande/devis, pas sur la liste. Sans elle, le menu deroulant s'affiche
en HTML brut, superpose au texte du dessus.

Executer depuis la racine du projet :
    python3 fix_select2_css_liste_commandes.py
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


ok = appliquer(
    "templates/commandes/index.html.twig",
    "{% block stylesheets %}\n"
    "\t{{ parent() }}\n"
    "\t<style>",

    "{% block stylesheets %}\n"
    "\t{{ parent() }}\n"
    "\t<link href=\"{{ asset( 'assets/plugins/select2/select2.min.css' ) }}\" rel=\"stylesheet\">\n"
    "\t<style>",

    "Feuille de style Select2 sur la liste des commandes",
)

print()
if ok:
    print("Termine sans erreur.")
else:
    print("Termine avec des erreurs. Voir [ERREUR] ci-dessus.")
    sys.exit(1)
