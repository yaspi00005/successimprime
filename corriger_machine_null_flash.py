#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrige le crash "Appel a la fonction membre getNom() sur null" au
demarrage d'une production, dans le message de succes affiche apres
coup (src/Controller/ProductionController.php, methode demarrer()).

Cause : $machine peut etre null (poste sans machine associee), et le
message de succes appelait $machine->getNom() sans protection -- a la
difference du message de notification juste au-dessus, qui lui verifie
deja "$machine !== null" avant.

Usage:
    python3 corriger_machine_null_flash.py /chemin/vers/successImprim
"""

import os
import re
import subprocess
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


MOTIF = re.compile(
    r"(sprintf\([ \t]*\n"
    r"[ \t]*'La production a démarré sur la machine %s\.',[ \t]*\n"
    r"[ \t]*)\$machine->getNom\(\)([ \t]*\n)"
)


def _remplacement(m):
    avant = m.group(1)
    apres = m.group(2)

    return avant + "$machine?->getNom() ?? 'du poste'" + apres


MARQUEUR = "$machine?->getNom() ?? 'du poste'"


def corriger_fichier(racine, chemin_relatif):
    chemin_absolu = os.path.join(racine, chemin_relatif)

    if not os.path.isfile(chemin_absolu):
        print("[ABSENT] " + chemin_relatif + " n'existe pas du tout sur le disque.")
        return False

    with open(chemin_absolu, "r", encoding="utf-8") as f:
        contenu = f.read()

    if MARQUEUR in contenu:
        print("[SKIP] " + chemin_relatif + " contient deja '" + MARQUEUR + "' (deja applique).")
        return True

    contenu_corrige, nb = MOTIF.subn(_remplacement, contenu, count=1)

    if nb == 0:
        print("[ECHEC] " + chemin_relatif + " : bloc introuvable -> abandon (rien ecrit).")
        print("  Copiez-moi le resultat de :")
        print("    grep -n -B3 -A3 \"La production a démarré sur la machine\" " + chemin_relatif)
        return False

    with open(chemin_absolu, "w", encoding="utf-8", newline="") as f:
        f.write(contenu_corrige)
        f.flush()
        os.fsync(f.fileno())

    with open(chemin_absolu, "r", encoding="utf-8", newline="") as f:
        relu = f.read()

    if relu != contenu_corrige:
        print("[ECHEC VERIFICATION] " + chemin_relatif + " : le contenu relu ne correspond pas.")
        return False

    print("[OK VERIFIE] " + chemin_relatif)
    print("  Chemin reel : " + os.path.realpath(chemin_absolu))

    try:
        resultat = subprocess.run(
            ["php", "-l", chemin_absolu],
            capture_output=True, text=True, timeout=30
        )
        print("  php -l : " + resultat.stdout.strip() + resultat.stderr.strip())
    except Exception:
        pass

    return True


def main():
    racine = sys.argv[1] if len(sys.argv) >= 2 else "."
    verifier_racine(racine)

    chemin_relatif = "src/Controller/ProductionController.php"

    print("-" * 70)
    print(chemin_relatif)
    print("-" * 70)

    resultat = corriger_fichier(racine, chemin_relatif)
    print()

    print("=" * 70)
    print("RESUME")
    print("=" * 70)

    if resultat:
        print("Tout est en place. Lancez maintenant :")
        print("  php bin/console cache:clear")
        print()
        print("Demarrer une production sans machine associee ne doit plus")
        print("faire planter la page (le message affichera 'du poste' a la")
        print("place du nom de la machine).")
    else:
        print("Le fichier n'a pas pu etre modifie (voir [ECHEC] ci-dessus).")
        print("Recopiez-moi TOUT ce resume, je corrige avant de vous renvoyer le script.")


if __name__ == "__main__":
    main()
