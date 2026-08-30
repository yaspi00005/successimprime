#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aligne le devis sur la commande : masque definitivement le choix
"Configuration automatique / manuelle" sur une ligne Produit (la
procedure a ete simplifiee, il n'y a plus qu'une seule facon de
configurer : le mode manuel).

Deux endroits a corriger dans templates/devis/_form.html.twig :
  1) le bloc HTML "Mode de configuration" doit demarrer masque
     (style="display:none;"), comme dans commandes/_form.html.twig ;
  2) le JavaScript qui reaffiche cette zone quand le type de ligne
     est "Produit" (zoneMode.style.display = estProduit ? '' : 'none')
     doit toujours la masquer, quel que soit le type de ligne.

Les deux fragments cibles sont des lignes autonomes (independantes de
l'indentation environnante), remplacees telles quelles.

Usage:
    python3 masquer_mode_configuration_devis.py /chemin/vers/successImprim
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


ANCIEN_DIV = '<div class="js-zone-mode-configuration">'
NOUVEAU_DIV = '<div class="js-zone-mode-configuration" style="display:none;">'

ANCIEN_JS = "zoneMode.style.display = estProduit ? '' : 'none';"
NOUVEAU_JS = "zoneMode.style.display = 'none';"

MARQUEUR = NOUVEAU_DIV


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

    if ANCIEN_DIV not in contenu:
        print("[ECHEC] " + chemin_relatif + " : bloc HTML introuvable -> abandon (rien ecrit).")
        print("  Copiez-moi le resultat de :")
        print("    grep -n \"js-zone-mode-configuration\" " + chemin_relatif)
        return False

    if ANCIEN_JS not in contenu:
        print("[ECHEC] " + chemin_relatif + " : bloc JavaScript introuvable -> abandon (rien ecrit).")
        print("  Copiez-moi le resultat de :")
        print("    grep -n -B5 -A5 \"zoneMode.style.display\" " + chemin_relatif)
        return False

    contenu_corrige = contenu.replace(ANCIEN_DIV, NOUVEAU_DIV, 1)
    contenu_corrige = contenu_corrige.replace(ANCIEN_JS, NOUVEAU_JS, 1)

    with open(chemin_absolu, "w", encoding="utf-8", newline="") as f:
        f.write(contenu_corrige)
        f.flush()
        os.fsync(f.fileno())

    with open(chemin_absolu, "r", encoding="utf-8", newline="") as f:
        relu = f.read()

    if relu != contenu_corrige:
        print("[ECHEC VERIFICATION] " + chemin_relatif + " : le contenu relu ne correspond pas.")
        return False

    print("[OK VERIFIE] " + chemin_relatif + " (2 remplacement(s))")
    print("  Chemin reel : " + os.path.realpath(chemin_absolu))
    return True


def main():
    racine = sys.argv[1] if len(sys.argv) >= 2 else "."
    verifier_racine(racine)

    chemin_relatif = "templates/devis/_form.html.twig"

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
        print("Puis videz le cache de votre navigateur (Cmd+Maj+R). Sur un")
        print("devis, une ligne 'Produit / prestation' ne doit plus montrer")
        print("le choix 'Configuration automatique / manuelle' -- comme sur")
        print("les commandes.")
    else:
        print("Le fichier n'a pas pu etre modifie (voir [ECHEC] ci-dessus).")
        print("Recopiez-moi TOUT ce resume, je corrige avant de vous renvoyer le script.")


if __name__ == "__main__":
    main()
