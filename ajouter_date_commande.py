#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ajoute la date de la commande :
  1) dans la liste des commandes (templates/commandes/index.html.twig),
     comme nouvelle colonne "Date" ;
  2) sur la fiche detail d'une commande (templates/commandes/show.html.twig),
     a cote de la reference dans l'entete "Details de la commande".

Regex tolerantes a l'indentation (espaces ou tabulations), pour
s'adapter aux differences deja constatees entre ce brouillon et vos
fichiers reels.

Usage:
    python3 ajouter_date_commande.py /chemin/vers/successImprim
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
# templates/commandes/index.html.twig
# ============================================================

MOTIF_ENTETE = re.compile(
    r"(<th scope=\"col\">Commande</th>)([ \t]*\n(?:[ \t]*\n)*)"
    r"([ \t]*)(<th scope=\"col\">Client</th>)"
)


def _remplacement_entete(m):
    th_commande = m.group(1)
    interligne = m.group(2)
    indent = m.group(3)
    th_client = m.group(4)

    return (
        th_commande + interligne
        + indent + "<th scope=\"col\">Date</th>" + interligne
        + indent + th_client
    )


MOTIF_CELLULE = re.compile(
    r"([ \t]*</td>[ \t]*\n(?:[ \t]*\n)*)"
    r"([ \t]*)(\{#\s*2\.\s*Client\s*#\})"
)


def _remplacement_cellule(m):
    fin_td_commande = m.group(1)
    indent = m.group(2)
    commentaire_client = m.group(3)

    unite = "\t" if ("\t" in indent or indent == "") else "\t"
    i1 = indent + unite

    bloc_date = (
        indent + "{# Date de la commande #}\n"
        + indent + "<td>\n"
        + i1 + "{% if commande.dateCommande %}\n"
        + i1 + "\t{{ commande.dateCommande|date('d/m/Y') }}\n"
        + i1 + "{% else %}\n"
        + i1 + "\t<span class=\"text-muted\">—</span>\n"
        + i1 + "{% endif %}\n"
        + indent + "</td>\n\n"
    )

    return fin_td_commande + bloc_date + indent + commentaire_client


MARQUEUR_INDEX = "{# Date de la commande #}"


def corriger_index(racine):
    chemin_relatif = "templates/commandes/index.html.twig"

    print("-" * 70)
    print(chemin_relatif)
    print("-" * 70)

    resultat = appliquer_regex_verifie(
        racine,
        chemin_relatif,
        MARQUEUR_INDEX,
        [
            (MOTIF_ENTETE, _remplacement_entete, "Colonne d'en-tête 'Date'"),
            (MOTIF_CELLULE, _remplacement_cellule, "Cellule 'Date' dans chaque ligne"),
        ]
    )

    if not resultat:
        return False

    # Colspan de l'état vide : 9 -> 10 (une colonne de plus).
    chemin_absolu = os.path.join(racine, chemin_relatif)

    with open(chemin_absolu, "r", encoding="utf-8") as f:
        contenu = f.read()

    if 'colspan="10"' not in contenu and 'colspan="9"' in contenu:
        contenu = contenu.replace('colspan="9"', 'colspan="10"', 1)

        with open(chemin_absolu, "w", encoding="utf-8", newline="") as f:
            f.write(contenu)
            f.flush()
            os.fsync(f.fileno())

        print("  Colspan de l'état vide : 9 -> 10")

    return True


# ============================================================
# templates/commandes/show.html.twig
# ============================================================

MOTIF_SHOW = re.compile(
    r"(<small class=\"text-muted\">[ \t]*\n)"
    r"([ \t]*)(\{\{ reference \}\}[ \t]*\n)"
    r"([ \t]*)(</small>)"
)


def _remplacement_show(m):
    ouverture = m.group(1)
    indent_reference = m.group(2)
    reference = m.group(3)
    indent_fermeture = m.group(4)
    fermeture = m.group(5)

    unite = "\t" if ("\t" in indent_reference or indent_reference == "") else "\t"
    i1 = indent_reference + unite

    return (
        ouverture
        + indent_reference + reference
        + indent_reference + "{% if commande.dateCommande %}\n"
        + i1 + "· {{ commande.dateCommande|date('d/m/Y') }}\n"
        + indent_reference + "{% endif %}\n"
        + indent_fermeture + fermeture
    )


MARQUEUR_SHOW = "commande.dateCommande|date('d/m/Y') }}\n"


def corriger_show(racine):
    chemin_relatif = "templates/commandes/show.html.twig"

    print()
    print("-" * 70)
    print(chemin_relatif)
    print("-" * 70)

    chemin_absolu = os.path.join(racine, chemin_relatif)

    if not os.path.isfile(chemin_absolu):
        print("[ABSENT] " + chemin_relatif + " n'existe pas du tout sur le disque.")
        return False

    with open(chemin_absolu, "r", encoding="utf-8") as f:
        contenu = f.read()

    if "commande.dateCommande|date" in contenu:
        print("[SKIP] " + chemin_relatif + " contient deja la date de la commande (deja applique).")
        return True

    contenu_corrige, nb = MOTIF_SHOW.subn(_remplacement_show, contenu, count=1)

    if nb == 0:
        print("[ECHEC] " + chemin_relatif + " : repere 'Détails de la commande' introuvable -> abandon (rien ecrit).")
        print("  Copiez-moi le resultat de :")
        print("    grep -n -B3 -A3 \"{{ reference }}\" " + chemin_relatif)
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
    return True


def main():
    racine = sys.argv[1] if len(sys.argv) >= 2 else "."
    verifier_racine(racine)

    resultats = [
        corriger_index(racine),
        corriger_show(racine),
    ]

    print()
    print("=" * 70)
    print("RESUME")
    print("=" * 70)

    if all(resultats):
        print("Tout est en place. Lancez maintenant :")
        print("  php bin/console cache:clear")
        print()
        print("La date de la commande apparait maintenant dans la liste des")
        print("commandes (nouvelle colonne) et sur la fiche detail (a cote")
        print("de la reference).")
    else:
        print("Au moins un fichier n'a pas pu etre modifie (voir [ECHEC] ci-dessus).")
        print("Recopiez-moi TOUT ce resume, je corrige avant de vous renvoyer le script.")


if __name__ == "__main__":
    main()
