#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Termine le correctif precedent (donner_acces_caisse_reclamations.py) :
le controleur a ete corrige avec succes chez vous, mais le gabarit
templates/reclamation/index.html.twig n'a pas pu etre modifie car son
indentation reelle differe legerement de celle du bac a sable (espaces
au lieu de tabulations, ou profondeur differente).

Ce script utilise des expressions regulieres tolerantes a
l'indentation (au lieu d'un texte exact) pour eviter ce probleme.

Il ajoute "or peutPayer" a cote de "estAdmin" a 3 endroits de la page
Reclamations, pour qu'une caisse (ROLE_CAISSE_COMMANDE) voit elle
aussi la colonne "Agent" et la liste complete des reclamations (et
pas seulement les siennes).

Usage:
    python3 finir_liste_reclamations_caisse.py /chemin/vers/successImprim
"""

import os
import re
import sys


def erreur_fatale(message):
    print("\n[ERREUR FATALE] " + message)
    sys.exit(1)


def verifier_racine(racine):
    print("=" * 70)
    print("DIAGNOSTIC DE L'EMPLACEMENT")
    print("=" * 70)
    print("Repertoire courant (pwd)      : " + os.getcwd())
    print("Racine passee en argument     : " + racine)
    print("Racine resolue (chemin absolu): " + os.path.realpath(racine))

    composer_json = os.path.join(racine, "composer.json")
    if not os.path.isfile(composer_json):
        erreur_fatale(
            "Aucun 'composer.json' trouve dans " + os.path.realpath(racine) + "\n"
            "  => Relancez le script en pointant vers la racine du projet."
        )
    print("[OK] composer.json trouve : c'est bien la racine du projet.")
    print()


def main():
    racine = sys.argv[1] if len(sys.argv) >= 2 else "."
    verifier_racine(racine)

    chemin_relatif = "templates/reclamation/index.html.twig"
    chemin_absolu = os.path.join(racine, chemin_relatif)

    print("-" * 70)
    print("Finalisation de l'affichage pour la caisse (" + chemin_relatif + ")")
    print("-" * 70)

    if not os.path.isfile(chemin_absolu):
        print("[ABSENT] " + chemin_relatif + " n'existe pas du tout sur le disque.")
        sys.exit(1)

    with open(chemin_absolu, "r", encoding="utf-8") as f:
        contenu = f.read()

    if "estAdmin or peutPayer" in contenu:
        print("[SKIP] Le correctif est deja applique.")
        return

    contenu_original = contenu
    total_remplacements = 0

    # ------------------------------------------------------------
    # 1) {% if estAdmin %}  ->  {% if estAdmin or peutPayer %}
    #    (apparait 2 fois : colonne d'en-tete "Agent" + cellule
    #    "Agent" de chaque ligne)
    # ------------------------------------------------------------
    motif_if = re.compile(r"\{%-?\s*if\s+estAdmin\s*-?%\}")
    occurrences_if = len(motif_if.findall(contenu))

    if occurrences_if == 0:
        print("[ECHEC] Aucun '{% if estAdmin %}' trouve -> abandon (rien ecrit).")
        print()
        print("Recopiez-moi ce message : le fichier a peut-etre change entre-temps.")
        sys.exit(1)

    contenu, nb = motif_if.subn("{% if estAdmin or peutPayer %}", contenu)
    total_remplacements += nb
    print("  '{% if estAdmin %}' -> '{% if estAdmin or peutPayer %}' : " + str(nb) + " remplacement(s)")

    # ------------------------------------------------------------
    # 2) Titre : estAdmin ? '...' : '...'
    # ------------------------------------------------------------
    motif_titre = re.compile(
        r"\{\{\s*estAdmin\s*\?\s*'Toutes\s+les\s+réclamations'\s*:\s*'Mes\s+réclamations'\s*\}\}"
    )
    contenu, nb = motif_titre.subn(
        "{{ (estAdmin or peutPayer) ? 'Toutes les réclamations' : 'Mes réclamations' }}",
        contenu
    )
    total_remplacements += nb
    print("  Titre de la page : " + str(nb) + " remplacement(s)")

    # ------------------------------------------------------------
    # 3) colspan="{{ estAdmin ? 8 : 7 }}"
    # ------------------------------------------------------------
    motif_colspan = re.compile(r"\{\{\s*estAdmin\s*\?\s*8\s*:\s*7\s*\}\}")
    contenu, nb = motif_colspan.subn("{{ (estAdmin or peutPayer) ? 8 : 7 }}", contenu)
    total_remplacements += nb
    print("  Colspan 'aucune réclamation' : " + str(nb) + " remplacement(s)")

    if contenu == contenu_original:
        print("[ECHEC] Aucun changement applique -> abandon (rien ecrit).")
        sys.exit(1)

    with open(chemin_absolu, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
        f.flush()
        os.fsync(f.fileno())

    with open(chemin_absolu, "r", encoding="utf-8", newline="") as f:
        relu = f.read()

    if relu != contenu:
        print("[ECHEC VERIFICATION] le contenu relu ne correspond pas a ce qui etait attendu.")
        sys.exit(1)

    print()
    print("[OK VERIFIE] " + chemin_relatif + " (" + str(total_remplacements) + " remplacement(s) au total)")
    print("  Chemin reel : " + os.path.realpath(chemin_absolu))
    print()
    print("Tout est en place. Lancez maintenant :")
    print("  php bin/console cache:clear")
    print("puis reconnectez-vous avec un compte ROLE_CAISSE_COMMANDE : la liste")
    print("des reclamations doit maintenant montrer toutes les reclamations")
    print("(colonne Agent visible), avec le bouton Payer sur celles validees.")


if __name__ == "__main__":
    main()
