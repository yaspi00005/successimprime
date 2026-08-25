#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilise le fuseau horaire nomme "Africa/Bamako" (plutot que "UTC")
dans public/index.php -- meme heure locale au Mali (GMT+0, sans heure
d'ete), mais plus explicite et correct si PHP venait a changer ses
regles de fuseaux horaires.

Gere 3 cas de figure sur le fichier reel :
  1) le script precedent (UTC) n'a jamais ete lance -> ajoute directement
     Africa/Bamako.
  2) le script precedent (UTC) a deja ete lance -> remplace UTC par
     Africa/Bamako.
  3) deja sur Africa/Bamako -> ne touche a rien.

Usage:
    python3 corriger_heure_bamako.py /chemin/vers/successImprim
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


ANCIEN_SANS_FUSEAU = """<?php

use App\\Kernel;"""

ANCIEN_AVEC_UTC = "date_default_timezone_set('UTC');"

NOUVEAU_LIGNE = "date_default_timezone_set('Africa/Bamako');"

NOUVEAU_SANS_FUSEAU = """<?php

date_default_timezone_set('Africa/Bamako');

use App\\Kernel;"""

MARQUEUR = "Africa/Bamako"


def main():
    racine = sys.argv[1] if len(sys.argv) >= 2 else "."
    verifier_racine(racine)

    if not PHP_LINT_DISPONIBLE:
        print("(info : commande 'php' introuvable ici, le controle 'php -l' sera saute)")
        print()

    chemin_relatif = "public/index.php"
    chemin_absolu = os.path.join(racine, chemin_relatif)

    print("-" * 70)
    print("Passage sur le fuseau Africa/Bamako (" + chemin_relatif + ")")
    print("-" * 70)

    if not os.path.isfile(chemin_absolu):
        print("[ABSENT] " + chemin_relatif + " n'existe pas du tout sur le disque.")
        sys.exit(1)

    with open(chemin_absolu, "r", encoding="utf-8") as f:
        contenu = f.read()

    if MARQUEUR in contenu:
        print("[SKIP] Deja sur Africa/Bamako.")
        return

    if ANCIEN_AVEC_UTC in contenu:
        occurrences = contenu.count(ANCIEN_AVEC_UTC)
        if occurrences != 1:
            print("[ECHEC] La ligne UTC attendue trouvee " + str(occurrences) +
                  " fois au lieu de 1 -> abandon (rien ecrit).")
            sys.exit(1)
        contenu = contenu.replace(ANCIEN_AVEC_UTC, NOUVEAU_LIGNE, 1)

    elif ANCIEN_SANS_FUSEAU in contenu:
        occurrences = contenu.count(ANCIEN_SANS_FUSEAU)
        if occurrences != 1:
            print("[ECHEC] Le debut de fichier attendu trouve " + str(occurrences) +
                  " fois au lieu de 1 -> abandon (rien ecrit).")
            sys.exit(1)
        contenu = contenu.replace(ANCIEN_SANS_FUSEAU, NOUVEAU_SANS_FUSEAU, 1)

    else:
        print("[ECHEC] Le fichier ne correspond a aucun etat attendu -> abandon (rien ecrit).")
        print()
        print("Recopiez-moi ce message : le fichier a peut-etre change entre-temps.")
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

    print("[OK VERIFIE] " + chemin_relatif + " (fuseau Africa/Bamako applique)")
    print("  Chemin reel : " + os.path.realpath(chemin_absolu))
    lint_php_si_possible(chemin_absolu)
    print()
    print("Tout est en place. Lancez maintenant :")
    print("  php bin/console cache:clear")


if __name__ == "__main__":
    main()
