#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ajoute le lien "Consommables" dans le menu Production (a cote de
"Vue d'ensemble", "Prepresse", "Productions terminees") -- la page
elle-meme existe deja et fonctionne (/consommables), il ne lui
manquait qu'un lien dans le menu pour ne plus dependre d'un ordre
de production precis.

Fichier concerne :
  - templates/base.html.twig

Usage:
    python3 ajouter_menu_consommables.py /chemin/vers/successImprim
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


ANCIEN = "Vue d'ensemble\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t</a>"
NOUVEAU = 'Vue d\'ensemble\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t</a>\n\n\n\t\t\t\t\t\t\t\t\t\t\t<a href="{{ path(\'app_consommables_index\') }}" class="slide-item {{ routeCourante starts with \'app_consommables_\' ? \'active\' : \'\' }}">\n\n\t\t\t\t\t\t\t\t\t\t\t\t<i class="fa fa-minus-circle mr-2"></i>\n\n\t\t\t\t\t\t\t\t\t\t\t\tConsommables\n\n\t\t\t\t\t\t\t\t\t\t\t</a>'


def main():
    racine = sys.argv[1] if len(sys.argv) >= 2 else "."
    verifier_racine(racine)

    chemin_relatif = "templates/base.html.twig"
    chemin_absolu = os.path.join(racine, chemin_relatif)

    if not os.path.isfile(chemin_absolu):
        erreur_fatale(chemin_relatif + " n'existe pas.")

    with open(chemin_absolu, "r", encoding="utf-8") as f:
        contenu = f.read()

    if NOUVEAU in contenu:
        print("[SKIP] " + chemin_relatif + " : lien Consommables deja present.")
        return

    if ANCIEN not in contenu:
        print("[ECHEC] " + chemin_relatif + " : bloc de reference introuvable.")
        print("Recopiez-moi le resultat de :")
        print("  grep -n \"Vue d.ensemble\" templates/base.html.twig")
        return

    if contenu.count(ANCIEN) > 1:
        print("[ECHEC] bloc de reference trouve plusieurs fois, abandon par prudence.")
        return

    contenu_corrige = contenu.replace(ANCIEN, NOUVEAU, 1)

    with open(chemin_absolu, "w", encoding="utf-8", newline="") as f:
        f.write(contenu_corrige)
        f.flush()
        os.fsync(f.fileno())

    with open(chemin_absolu, "r", encoding="utf-8", newline="") as f:
        relu = f.read()

    if relu != contenu_corrige:
        print("[ECHEC VERIFICATION] le contenu relu ne correspond pas.")
        return

    print("[OK VERIFIE] " + chemin_relatif)
    print("  Chemin reel : " + os.path.realpath(chemin_absolu))
    print()
    print("Le lien 'Consommables' apparait maintenant dans le menu")
    print("Production, a cote de 'Vue d'ensemble' et 'Prepresse'.")


if __name__ == "__main__":
    main()