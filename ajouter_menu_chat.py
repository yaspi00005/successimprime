#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ajoute une entree "Messagerie" dans le menu lateral (base.html.twig) :
le chat interne existait deja (icone dans l'en-tete), mais n'avait pas
sa propre entree dans le menu principal, a cote de Commercial,
Production, Réclamations, etc.

Utilise des expressions regulieres tolerantes a l'indentation (ce
fichier a deja pose des soucis d'indentation par le passe sur ce
projet) pour :
  1) ajouter l'onglet "Messagerie" dans la liste des onglets ;
  2) ajouter le panneau "Messagerie" (lien vers la messagerie) ;
  3) faire en sorte que l'onglet Messagerie reste actif/surligne
     quand on est sur une page de chat.

Usage:
    python3 ajouter_menu_chat.py /chemin/vers/successImprim
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


def appliquer_regex_verifie(racine, chemin_relatif, marqueur, remplacements):
    chemin_absolu = os.path.join(racine, chemin_relatif)

    if not os.path.isfile(chemin_absolu):
        print("[ABSENT] " + chemin_relatif + " n'existe pas du tout sur le disque.")
        return False

    with open(chemin_absolu, "r", encoding="utf-8") as f:
        contenu = f.read()

    if marqueur in contenu:
        print("[SKIP] " + chemin_relatif + " contient deja '" + marqueur + "' (deja applique).")
        return True

    contenu_original = contenu
    total = 0

    for motif, remplacement, description in remplacements:
        contenu, nb = motif.subn(remplacement, contenu, count=1)
        if nb == 0:
            print("[ECHEC] " + chemin_relatif + " : '" + description + "' introuvable -> abandon (rien ecrit).")
            return False
        total += nb
        print("  " + description + " : " + str(nb) + " remplacement(s)")

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

    print("[OK VERIFIE] " + chemin_relatif + " (" + str(total) + " remplacement(s) au total)")
    print("  Chemin reel : " + os.path.realpath(chemin_absolu))
    return True


# ============================================================
# 1) Onglet "Messagerie" dans la liste des onglets (<li>)
# ============================================================

MOTIF_ONGLET = re.compile(
    r"(<div class=\"slider-text\">\s*Réclamations\s*</div>[ \t]*\n"
    r"(?:[ \t]*\n)*[ \t]*</li>[ \t]*\n(?:[ \t]*\n)*)"
    r"([ \t]*)(</ul>)"
)


def _remplacement_onglet(m):
    prefix = m.group(1)
    indent = m.group(2)
    balise_ul = m.group(3)

    unite = "\t" if ("\t" in indent or indent == "") else "    "
    i1 = indent + unite
    i2 = i1 + unite

    return (
        prefix
        + i1 + "<li class=\"{{ menuActif == 'messagerie' ? 'resp-tab-active active' : '' }}\" "
        + "data-menu=\"messagerie\" title=\"Messagerie\">\n\n"
        + i2 + "<i class=\"side-menu__icon fa fa-comments\"></i>\n\n"
        + i2 + "<div class=\"slider-text\">\n"
        + i2 + "\tMessagerie\n"
        + i2 + "</div>\n\n"
        + i1 + "</li>\n\n\n"
        + indent + balise_ul
    )


# ============================================================
# 2) Panneau "Messagerie" (juste apres le panneau Réclamations)
# ============================================================

MOTIF_PANNEAU = re.compile(
    r"(Mes\s+réclamations[ \t]*\n(?:[ \t]*\n)*[ \t]*</a>[ \t]*\n"
    r"(?:[ \t]*\n)*(?:[ \t]*</div>[ \t]*\n(?:[ \t]*\n)*){3})"
)


def _remplacement_panneau(m):
    prefix = m.group(1)

    derniere_ligne_div = prefix.rstrip("\n").splitlines()[-1]
    indent_div = derniere_ligne_div[: len(derniere_ligne_div) - len(derniere_ligne_div.lstrip(" \t"))]
    unite = "\t" if ("\t" in indent_div or indent_div == "") else "    "

    indent = indent_div
    i1 = indent + unite
    i2 = i1 + unite
    i3 = i2 + unite

    return (
        prefix + "\n"
        + indent + "<div data-panel=\"messagerie\" class=\"{{ menuActif == 'messagerie' ? 'resp-tab-content-active' : '' }}\">\n\n"
        + i1 + "<div class=\"row\">\n\n"
        + i2 + "<div class=\"col-md-12\">\n\n"
        + i3 + "<h4 class=\"font-weight-normal\">\n"
        + i3 + "\t<i class=\"fa fa-comments\"></i>\n"
        + i3 + "\tMessagerie\n"
        + i3 + "</h4>\n\n"
        + i3 + "<a href=\"{{ path( 'app_chat_index' ) }}\" "
        + "class=\"slide-item {{ routeCourante starts with 'app_chat_' ? 'active' : '' }}\">\n"
        + i3 + "\t<i class=\"fa fa-comments mr-2\"></i>\n"
        + i3 + "\tDiscussions\n"
        + i3 + "</a>\n\n"
        + i2 + "</div>\n\n"
        + i1 + "</div>\n\n"
        + indent + "</div>\n\n"
    )


# ============================================================
# 3) menuActif : surligner "Messagerie" sur les pages app_chat_*
# ============================================================

MOTIF_MENUACTIF = re.compile(
    r"(routeCourante\s+starts\s+with\s+'app_reclamation_'[ \t]*\n"
    r"[ \t]*%\}[ \t]*\n(?:[ \t]*\n)*"
    r"[ \t]*\{%-?\s*set\s+menuActif\s*=\s*'reclamations'\s*%\}[ \t]*\n(?:[ \t]*\n)*)"
    r"([ \t]*)(\{%-?\s*endif\s*-?%\})"
)


def _remplacement_menuactif(m):
    prefix = m.group(1)
    indent = m.group(2)
    endif_existant = m.group(3)

    return (
        prefix
        + indent + "{% elseif\n"
        + indent + "\trouteCourante starts with 'app_chat_'\n"
        + indent + "%}\n\n"
        + indent + "\t{% set menuActif = 'messagerie' %}\n\n\n"
        + indent + endif_existant
    )


MARQUEUR = "data-menu=\"messagerie\""


def main():
    racine = sys.argv[1] if len(sys.argv) >= 2 else "."
    verifier_racine(racine)

    print("-" * 70)
    print("Ajout du menu 'Messagerie' (templates/base.html.twig)")
    print("-" * 70)

    resultat = appliquer_regex_verifie(
        racine,
        "templates/base.html.twig",
        MARQUEUR,
        [
            (MOTIF_ONGLET, _remplacement_onglet, "Onglet Messagerie (liste des onglets)"),
            (MOTIF_PANNEAU, _remplacement_panneau, "Panneau Messagerie (lien vers la messagerie)"),
            (MOTIF_MENUACTIF, _remplacement_menuactif, "menuActif = 'messagerie' sur les pages app_chat_*"),
        ]
    )
    print()

    print("=" * 70)
    print("RESUME")
    print("=" * 70)

    if resultat:
        print("Tout est en place. Lancez maintenant :")
        print("  php bin/console cache:clear")
        print()
        print("Un nouvel onglet 'Messagerie' doit apparaitre dans le menu")
        print("lateral, a cote de Commercial/Production/Réclamations, avec")
        print("un lien 'Discussions' menant vers la messagerie interne.")
    else:
        print("Le fichier n'a pas pu etre modifie (voir [ECHEC] ci-dessus).")
        print("Recopiez-moi TOUT ce resume, je corrige avant de vous renvoyer le script.")


if __name__ == "__main__":
    main()
