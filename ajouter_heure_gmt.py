#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fixe le fuseau horaire par defaut de PHP sur GMT/UTC (Mali est en
GMT+0, donc c'est aussi l'heure locale), directement dans le point
d'entree de l'application (public/index.php) -- pour que toutes les
dates/heures affichees dans l'app (commandes, paiements, journal de
caisse, etc.) soient coherentes, sans dependre de la configuration du
serveur.

Usage:
    python3 ajouter_heure_gmt.py /chemin/vers/successImprim
"""

import os
import sys
import shutil
import subprocess


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


PHP_LINT_DISPONIBLE = shutil.which("php") is not None


def lint_php_si_possible(chemin_absolu):
    if not PHP_LINT_DISPONIBLE:
        return
    try:
        resultat = subprocess.run(
            ["php", "-l", chemin_absolu],
            capture_output=True, text=True, timeout=10,
        )
        sortie = (resultat.stdout + resultat.stderr).strip()
        if resultat.returncode == 0:
            print("  php -l : OK")
        else:
            print("  [ATTENTION] php -l a signale un probleme :")
            print("  " + sortie.replace("\n", "\n  "))
    except Exception as exc:
        print("  (php -l ignore : " + repr(exc) + ")")


ANCIEN = """<?php

use App\\Kernel;"""

NOUVEAU = """<?php

date_default_timezone_set('UTC');

use App\\Kernel;"""

MARQUEUR = "date_default_timezone_set"


def main():
    racine = sys.argv[1] if len(sys.argv) >= 2 else "."
    verifier_racine(racine)

    if not PHP_LINT_DISPONIBLE:
        print("(info : commande 'php' introuvable ici, le controle 'php -l' sera saute)")
        print()

    chemin_relatif = "public/index.php"
    chemin_absolu = os.path.join(racine, chemin_relatif)

    print("-" * 70)
    print("Ajout de l'heure GMT (" + chemin_relatif + ")")
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
        print("[ECHEC] Le debut de fichier attendu trouve " + str(occurrences) +
              " fois au lieu de 1 -> abandon (rien ecrit).")
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

    print("[OK VERIFIE] " + chemin_relatif + " (fuseau horaire GMT/UTC ajoute)")
    print("  Chemin reel : " + os.path.realpath(chemin_absolu))
    lint_php_si_possible(chemin_absolu)
    print()
    print("Tout est en place. Lancez maintenant :")
    print("  php bin/console cache:clear")


if __name__ == "__main__":
    main()
