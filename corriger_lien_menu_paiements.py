#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrige le lien "Paiements" invisible dans le menu de gauche.

Cause reelle : dans templates/base.html.twig, la variable qui decide
si le lien apparait verifiait le role 'ROLE_PAIEMENT' -- un role qui
n'existe nulle part ailleurs dans l'application (jamais proposable a
la creation d'un compte, jamais dans le role_hierarchy). Personne ne
pouvait donc jamais l'avoir, meme un administrateur : le lien restait
invisible pour tout le monde, alors que la page /paiements elle-meme
fonctionne (elle verifie le bon role, 'ROLE_PAIEMENT_VOIR').

Ce script aligne le menu sur le meme role que la page reelle.

Usage:
    python3 corriger_lien_menu_paiements.py /chemin/vers/successImprim
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


ANCIEN = """	{% set peutVoirPaiements =
		is_granted('ROLE_PAIEMENT')
	%}"""

NOUVEAU = """	{% set peutVoirPaiements =
		is_granted('ROLE_PAIEMENT_VOIR')
	%}"""

MARQUEUR = "is_granted('ROLE_PAIEMENT_VOIR')"


def main():
    racine = sys.argv[1] if len(sys.argv) >= 2 else "."
    verifier_racine(racine)

    chemin_relatif = "templates/base.html.twig"
    chemin_absolu = os.path.join(racine, chemin_relatif)

    print("-" * 70)
    print("Correction du lien Paiements dans le menu (" + chemin_relatif + ")")
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
        print("[ECHEC] Le bloc attendu trouve " + str(occurrences) + " fois au lieu de 1 -> abandon (rien ecrit).")
        print("  Extrait attendu : " + repr(ANCIEN))
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

    print("[OK VERIFIE] " + chemin_relatif + " (role corrige pour le lien Paiements)")
    print("  Chemin reel : " + os.path.realpath(chemin_absolu))
    print()
    print("Tout est en place. Lancez maintenant :")
    print("  php bin/console cache:clear")
    print("puis rechargez la page : le lien 'Paiements' doit apparaitre dans le")
    print("menu 'Gestion et tresorerie' pour les comptes ayant le droit de voir")
    print("les paiements (ROLE_PAIEMENT_VOIR, ou administrateur).")


if __name__ == "__main__":
    main()
