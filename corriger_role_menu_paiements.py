#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fait apparaitre le lien "Paiements" dans le menu (base.html.twig).

Cause : le menu verifie is_granted('ROLE_PAIEMENT'), un role qui
n'existe plus depuis que les permissions ont ete affinees en
ROLE_PAIEMENT_VOIR / ROLE_PAIEMENT_ENCAISSER (utilises partout
ailleurs, y compris dans le controle d'acces des routes /paiements
dans security.yaml). Ce test etant toujours faux, le lien ne
s'affichait pour personne, admin compris.

Usage:
    python3 corriger_role_menu_paiements.py /chemin/vers/successImprim
"""

import os
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


ANCIEN = "is_granted('ROLE_PAIEMENT')"
NOUVEAU = "is_granted('ROLE_PAIEMENT_VOIR')"


def corriger_fichier(racine, chemin_relatif):
    chemin_absolu = os.path.join(racine, chemin_relatif)

    if not os.path.isfile(chemin_absolu):
        print("[ABSENT] " + chemin_relatif + " n'existe pas du tout sur le disque.")
        return False

    with open(chemin_absolu, "r", encoding="utf-8") as f:
        contenu = f.read()

    if NOUVEAU in contenu:
        print("[SKIP] " + chemin_relatif + " contient deja '" + NOUVEAU + "' (deja applique).")
        return True

    occurrences = contenu.count(ANCIEN)

    if occurrences == 0:
        print("[ECHEC] " + chemin_relatif + " : \"" + ANCIEN + "\" introuvable -> abandon (rien ecrit).")
        print("  Copiez-moi le resultat de :")
        print("    grep -n \"ROLE_PAIEMENT\" " + chemin_relatif)
        return False

    if occurrences > 1:
        print("[ECHEC] " + chemin_relatif + " : \"" + ANCIEN + "\" trouve " + str(occurrences) + " fois (attendu 1) -> abandon par prudence (rien ecrit).")
        print("  Copiez-moi le resultat de :")
        print("    grep -n \"ROLE_PAIEMENT\" " + chemin_relatif)
        return False

    contenu_corrige = contenu.replace(ANCIEN, NOUVEAU, 1)

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

    return True


def main():
    racine = sys.argv[1] if len(sys.argv) >= 2 else "."
    verifier_racine(racine)

    chemin_relatif = "templates/base.html.twig"

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
        print("Rechargez la page (deconnexion/reconnexion pas necessaire) :")
        print("le lien \"Paiements\" doit apparaitre dans le menu, dans")
        print("l'onglet \"Gestion et tresorerie\", section \"Facturation\",")
        print("pour tout utilisateur ayant le role PAIEMENT_VOIR (les")
        print("admins l'ont via la hierarchie des roles).")
    else:
        print("Le fichier n'a pas pu etre modifie (voir [ECHEC] ci-dessus).")
        print("Recopiez-moi TOUT ce resume, je corrige avant de vous renvoyer le script.")


if __name__ == "__main__":
    main()
