#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Termine le correctif precedent (ajouter_decaissements_recurrents.py) :
tous les fichiers ont ete crees avec succes chez vous, sauf le lien de
menu dans templates/base.html.twig. La structure reelle de ce fichier
differe legerement de celle du bac a sable (un seul {% endif %} apres
le lien "Mouvements de tresorerie", pas deux), en plus d'une
indentation differente (espaces au lieu de tabulations).

Ce script utilise une expression reguliere tolerante a la fois a
l'indentation ET a cette difference de structure pour ajouter le lien
"Decaissements automatiques" sous Tresorerie, juste apres "Mouvements
de tresorerie".

Usage:
    python3 finir_menu_decaissements_recurrents.py /chemin/vers/successImprim
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


MOTIF_MENU = re.compile(
    r"(Mouvements\s+de\s+trésorerie[ \t]*\n(?:[ \t]*\n)*"
    r"[ \t]*</a>[ \t]*\n(?:[ \t]*\n)*)"
    r"([ \t]*)(\{%-?\s*endif\s*-?%\})"
)


def _remplacement_menu(m):
    prefix = m.group(1)
    indent = m.group(2)
    endif_existant = m.group(3)

    unite = "\t" if ("\t" in indent or indent == "") else "    "
    i1 = indent + unite
    i2 = i1 + unite

    return (
        prefix
        + indent + "{% if peutVoirComptesTresorerie %}\n\n"
        + i1 + "<a href=\"{{ path( 'app_decaissement_recurrent_index' ) }}\" "
        + "class=\"slide-item {{ routeCourante starts with 'app_decaissement_recurrent_' ? 'active' : '' }}\">\n\n"
        + i2 + "<i class=\"fa fa-refresh mr-2\"></i>\n\n"
        + i2 + "Décaissements automatiques\n\n"
        + i1 + "</a>\n\n"
        + indent + "{% endif %}\n\n\n"
        + indent + endif_existant
    )


def main():
    racine = sys.argv[1] if len(sys.argv) >= 2 else "."
    verifier_racine(racine)

    chemin_relatif = "templates/base.html.twig"
    chemin_absolu = os.path.join(racine, chemin_relatif)

    print("-" * 70)
    print("Ajout du lien de menu 'Decaissements automatiques' (" + chemin_relatif + ")")
    print("-" * 70)

    if not os.path.isfile(chemin_absolu):
        print("[ABSENT] " + chemin_relatif + " n'existe pas du tout sur le disque.")
        sys.exit(1)

    with open(chemin_absolu, "r", encoding="utf-8") as f:
        contenu = f.read()

    if "app_decaissement_recurrent_index" in contenu:
        print("[SKIP] Le lien de menu est deja present.")
        return

    contenu_nouveau, nb = MOTIF_MENU.subn(_remplacement_menu, contenu, count=1)

    if nb == 0:
        print("[ECHEC] Le repere 'Mouvements de trésorerie' est introuvable -> abandon (rien ecrit).")
        print()
        print("Recopiez-moi ce message : le fichier a peut-etre change entre-temps.")
        sys.exit(1)

    with open(chemin_absolu, "w", encoding="utf-8", newline="") as f:
        f.write(contenu_nouveau)
        f.flush()
        os.fsync(f.fileno())

    with open(chemin_absolu, "r", encoding="utf-8", newline="") as f:
        relu = f.read()

    if relu != contenu_nouveau:
        print("[ECHEC VERIFICATION] le contenu relu ne correspond pas a ce qui etait attendu.")
        sys.exit(1)

    print()
    print("[OK VERIFIE] " + chemin_relatif)
    print("  Chemin reel : " + os.path.realpath(chemin_absolu))
    print()
    print("Tout est en place. Lancez maintenant :")
    print("  php bin/console cache:clear")
    print("puis rechargez le site (compte administrateur) : sous Tresorerie,")
    print("le lien 'Decaissements automatiques' doit maintenant apparaitre.")


if __name__ == "__main__":
    main()
