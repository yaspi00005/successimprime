#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrige le tableau des employes qui apparait sombre et illisible.

Cause probable : le CSS personnalise de cette page fixe la couleur du
TEXTE en gris fonce (#1f2937) et le fond de l'EN-TETE en clair, mais ne
fixe jamais le fond des LIGNES elles-memes -- elles heritent donc du
fond ambiant. Si ce fond ambiant est sombre (theme sombre du
navigateur/OS), le resultat est du texte sombre sur fond sombre,
illisible -- uniquement sur cette page, puisque c'est la seule a avoir
ce CSS personnalise.

Correctif : fixer explicitement un fond blanc sur le tableau et sur
chaque ligne, pour que l'affichage reste clair quel que soit le theme
ambiant.

Usage:
    python3 corriger_couleur_tableau_employes.py /chemin/vers/successImprim
"""

import os
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


ANCIEN = """		#users-table {
			color: #1f2937;
		}

		#users-table thead th {
			background: #f4f7fc;"""

NOUVEAU = """		#users-table {
			color: #1f2937;
			background-color: #ffffff;
		}

		#users-table tbody tr {
			background-color: #ffffff;
		}

		#users-table thead th {
			background: #f4f7fc;"""

MARQUEUR = "#users-table tbody tr {"


def main():
    racine = sys.argv[1] if len(sys.argv) >= 2 else "."
    verifier_racine(racine)

    chemin_relatif = "templates/employes/index.html.twig"
    chemin_absolu = os.path.join(racine, chemin_relatif)

    print("-" * 70)
    print("Correction de la couleur du tableau employes (" + chemin_relatif + ")")
    print("-" * 70)

    if not os.path.isfile(chemin_absolu):
        print("[ABSENT] " + chemin_relatif + " n'existe pas du tout sur le disque.")
        sys.exit(1)

    with open(chemin_absolu, "r", encoding="utf-8") as f:
        contenu = f.read()

    if MARQUEUR in contenu:
        print("[SKIP] Le correctif est deja applique.")
        return

    occurrences = contenu.count(ANCIEN)
    if occurrences != 1:
        print("[ECHEC] La ligne attendue trouvee " + str(occurrences) +
              " fois au lieu de 1 -> abandon (rien ecrit).")
        print("  Extrait attendu (debut) : " + repr(ANCIEN[:150]))
        print()
        print("Recopiez-moi ce message : le fichier a peut-etre change entre-temps.")
        sys.exit(1)

    contenu = contenu.replace(ANCIEN, NOUVEAU, 1)

    with open(chemin_absolu, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
        f.flush()
        os.fsync(f.fileno())

    with open(chemin_absolu, "r", encoding="utf-8", newline="") as f:
        relu = f.read()

    if relu != contenu:
        print("[ECHEC VERIFICATION] le contenu relu ne correspond pas a ce qui etait attendu.")
        sys.exit(1)

    print("[OK VERIFIE] " + chemin_relatif + " (fond blanc force sur le tableau)")
    print("  Chemin reel : " + os.path.realpath(chemin_absolu))
    print()
    print("Tout est en place. Lancez maintenant :")
    print("  php bin/console cache:clear")
    print("puis rechargez la page Employes (Ctrl+F5 pour forcer le rechargement")
    print("du CSS) et dites-moi si le tableau est redevenu lisible.")


if __name__ == "__main__":
    main()
