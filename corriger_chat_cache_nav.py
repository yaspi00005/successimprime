#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrige le probleme "c'est cache derriere la nav d'en haut" sur les
pages de messagerie (Messagerie + Nouvelle conversation).

Cause : TOUTES les autres pages du site enveloppent leur contenu dans
<div class="side-app"> ... </div> (ce wrapper donne la marge qui evite
que le haut de la page passe sous la barre de navigation fixe). Les
deux pages de messagerie (templates/chat/chat.html.twig et
templates/chat/nouvelle.html.twig), ajoutees plus tot dans le projet,
n'ont jamais eu ce wrapper : c'est pour ca que leur en-tete (titre
"Messagerie" / fil d'ariane / bouton "Nouvelle conversation") se
retrouve cache derriere la barre du haut.

Ce script ajoute simplement ce wrapper manquant, comme sur toutes les
autres pages du site. Regex tolerantes a l'indentation (espaces ou
tabulations).

Usage:
    python3 corriger_chat_cache_nav.py /chemin/vers/successImprim
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


MOTIF_OUVERTURE = re.compile(
    r"(\{%-?\s*include\s+[\"']alert\.html\.twig[\"']\s*-?%\})([ \t]*\n(?:[ \t]*\n)*)"
    r"([ \t]*)(<div class=\"page-header\">)"
)


def _remplacement_ouverture(m):
    include_alert = m.group(1)
    interligne = m.group(2)
    indent = m.group(3)
    div_page_header = m.group(4)

    return (
        include_alert + interligne
        + indent + "<div class=\"side-app\">" + "\n\n"
        + indent + div_page_header
    )


MOTIF_FERMETURE = re.compile(
    r"([ \t]*</div>[ \t]*\n(?:[ \t]*\n)*)([ \t]*)(<script>[ \t]*\n[ \t]*document\.addEventListener)"
)


def _remplacement_fermeture(m):
    dernier_div_et_interligne = m.group(1)
    indent = m.group(2)
    debut_script = m.group(3)

    return dernier_div_et_interligne + indent + "</div>\n\n" + indent + debut_script


MARQUEUR = 'class="side-app"'


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

    contenu_original = contenu

    contenu, nb1 = MOTIF_OUVERTURE.subn(_remplacement_ouverture, contenu, count=1)
    if nb1 == 0:
        print("[ECHEC] " + chemin_relatif + " : ouverture '<div class=\"side-app\">' introuvable -> abandon (rien ecrit).")
        return False
    print("  Ouverture du wrapper side-app : " + str(nb1) + " remplacement(s)")

    contenu, nb2 = MOTIF_FERMETURE.subn(_remplacement_fermeture, contenu, count=1)
    if nb2 == 0:
        print("[ECHEC] " + chemin_relatif + " : fermeture '</div>' avant <script> introuvable -> abandon (rien ecrit).")
        return False
    print("  Fermeture du wrapper side-app : " + str(nb2) + " remplacement(s)")

    if contenu == contenu_original:
        print("[ECHEC] " + chemin_relatif + " : aucun changement applique -> abandon.")
        return False

    with open(chemin_absolu, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
        f.flush()
        os.fsync(f.fileno())

    with open(chemin_absolu, "r", encoding="utf-8", newline="") as f:
        relu = f.read()

    if relu != contenu:
        print("[ECHEC VERIFICATION] " + chemin_relatif + " : le contenu relu ne correspond pas.")
        return False

    print("[OK VERIFIE] " + chemin_relatif)
    print("  Chemin reel : " + os.path.realpath(chemin_absolu))
    return True


def main():
    racine = sys.argv[1] if len(sys.argv) >= 2 else "."
    verifier_racine(racine)

    fichiers = [
        "templates/chat/chat.html.twig",
        "templates/chat/nouvelle.html.twig",
    ]

    resultats = []

    for chemin_relatif in fichiers:
        print("-" * 70)
        print(chemin_relatif)
        print("-" * 70)
        resultats.append(corriger_fichier(racine, chemin_relatif))
        print()

    print("=" * 70)
    print("RESUME")
    print("=" * 70)

    if all(resultats):
        print("Tout est en place. Lancez maintenant :")
        print("  php bin/console cache:clear")
        print()
        print("Sur les pages Messagerie et Nouvelle conversation, le titre et")
        print("le fil d'ariane ne doivent plus etre caches sous la barre du")
        print("haut.")
    else:
        print("Au moins un fichier n'a pas pu etre modifie (voir [ECHEC] ci-dessus).")
        print("Recopiez-moi TOUT ce resume, je corrige avant de vous renvoyer le script.")


if __name__ == "__main__":
    main()
