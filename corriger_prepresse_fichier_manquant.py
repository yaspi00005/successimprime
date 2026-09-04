#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrige le probleme "on n'a pas ajoute de fichier au moment de la
creation et on ne voit pas la ligne au niveau du controle prepresse".

Cause : la liste du controle prepresse (et son bouton d'action)
n'affichait QUE les lignes ayant deja au moins un fichier joint
(innerJoin sur les fichiers). Une ligne creee sans fichier disparait
donc completement de cette liste -- personne ne sait qu'il faut
reclamer le fichier au client.

Ce script :
  1. change la liste (ControlePrePresseController::index()) pour
     afficher aussi les lignes sans fichier (avec ou sans fichier,
     tant que la ligne necessite reellement un controle prepresse) ;
  2. dans le tableau, affiche un badge "Fichier manquant" a la place
     du nombre de fichiers quand il n'y en a aucun ;
  3. remplace le bouton "Controler" (qui refusait de s'ouvrir sans
     fichier) par un bouton "Ajouter le fichier" menant directement
     a la modification de la commande, pour les lignes concernees.

Usage:
    python3 corriger_prepresse_fichier_manquant.py /chemin/vers/successImprim
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


# ============================================================
# FICHIER 1 : src/Controller/ControlePrePresseController.php
# ============================================================

ANCIEN_PHP = """            ->innerJoin('detail.fichiers', 'fichier')
            ->andWhere('fichier.actif = :actif')
            ->andWhere('detail.prePresseNecessaire = :prepresseNecessaire')"""

NOUVEAU_PHP = """            ->leftJoin(
                'detail.fichiers',
                'fichier',
                'WITH',
                'fichier.actif = :actif'
            )
            ->andWhere('detail.prePresseNecessaire = :prepresseNecessaire')"""

MARQUEUR_PHP = "'WITH',"


def corriger_php(racine):
    chemin_relatif = "src/Controller/ControlePrePresseController.php"
    chemin_absolu = os.path.join(racine, chemin_relatif)

    if not os.path.isfile(chemin_absolu):
        print("[ABSENT] " + chemin_relatif + " n'existe pas du tout sur le disque.")
        return False

    with open(chemin_absolu, "r", encoding="utf-8") as f:
        contenu = f.read()

    if MARQUEUR_PHP in contenu:
        print("[SKIP] " + chemin_relatif + " contient deja le correctif (deja applique).")
        return True

    if ANCIEN_PHP not in contenu:
        print("[ECHEC] " + chemin_relatif + " : bloc de reference introuvable -> abandon (rien ecrit).")
        print("  Copiez-moi le resultat de :")
        print("    grep -n -B3 -A3 \"innerJoin('detail.fichiers'\" " + chemin_relatif)
        return False

    if contenu.count(ANCIEN_PHP) > 1:
        print("[ECHEC] " + chemin_relatif + " : bloc de reference trouve plusieurs fois -> abandon par prudence.")
        return False

    contenu_corrige = contenu.replace(ANCIEN_PHP, NOUVEAU_PHP, 1)

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


# ============================================================
# FICHIER 2 : templates/controle_pre_presse/index.html.twig
# ============================================================
#
# Regex tolerantes aux espaces/tabulations (la mise en forme reelle
# du serveur peut differer legerement de celle du brouillon).
# ============================================================

MARQUEUR_TWIG = "Fichier manquant"

REGEX_BADGE = re.compile(
    r"([ \t]*)<td class=\"text-center\">\n"
    r"[ \t]*<span class=\"badge badge-primary\">\n"
    r"[ \t]*\{\{ detail\.fichiers\|length \}\}\n"
    r"[ \t]*</span>\n"
    r"[ \t]*</td>"
)

REGEX_BOUTON = re.compile(
    r"([ \t]*)<td class=\"text-center\">\n"
    r"[ \t]*<a href=\"\{\{ path\( 'app_controle_pre_presse_controler', \{id: detail\.id\} \) \}\}\" class=\"btn btn-sm btn-primary\">\n"
    r"[ \t]*<i class=\"fe fe-check-square mr-1\"></i>\n"
    r"[ \t]*Contrôler\n"
    r"[ \t]*</a>\n"
    r"[ \t]*</td>"
)


def remplacer_badge(correspondance):
    indent = correspondance.group(1)
    return (
        indent + "<td class=\"text-center\">\n"
        + indent + "\t{% if detail.fichiers is empty %}\n"
        + indent + "\t\t<span class=\"badge badge-danger\">\n"
        + indent + "\t\t\tFichier manquant\n"
        + indent + "\t\t</span>\n"
        + indent + "\t{% else %}\n"
        + indent + "\t\t<span class=\"badge badge-primary\">\n"
        + indent + "\t\t\t{{ detail.fichiers|length }}\n"
        + indent + "\t\t</span>\n"
        + indent + "\t{% endif %}\n"
        + indent + "</td>"
    )


def remplacer_bouton(correspondance):
    indent = correspondance.group(1)
    return (
        indent + "<td class=\"text-center\">\n"
        + indent + "\t{% if detail.fichiers is empty %}\n"
        + indent + "\t\t<a href=\"{{ path( 'app_commandes_edit', {id: detail.commande.id} ) }}\" class=\"btn btn-sm btn-warning\">\n"
        + indent + "\t\t\t<i class=\"fe fe-upload mr-1\"></i>\n"
        + indent + "\t\t\tAjouter le fichier\n"
        + indent + "\t\t</a>\n"
        + indent + "\t{% else %}\n"
        + indent + "\t\t<a href=\"{{ path( 'app_controle_pre_presse_controler', {id: detail.id} ) }}\" class=\"btn btn-sm btn-primary\">\n"
        + indent + "\t\t\t<i class=\"fe fe-check-square mr-1\"></i>\n"
        + indent + "\t\t\tContrôler\n"
        + indent + "\t\t</a>\n"
        + indent + "\t{% endif %}\n"
        + indent + "</td>"
    )


def corriger_twig(racine):
    chemin_relatif = "templates/controle_pre_presse/index.html.twig"
    chemin_absolu = os.path.join(racine, chemin_relatif)

    if not os.path.isfile(chemin_absolu):
        print("[ABSENT] " + chemin_relatif + " n'existe pas du tout sur le disque.")
        return False

    with open(chemin_absolu, "r", encoding="utf-8") as f:
        contenu = f.read()

    if MARQUEUR_TWIG in contenu:
        print("[SKIP] " + chemin_relatif + " contient deja le correctif (deja applique).")
        return True

    contenu_corrige, nombre_badge = REGEX_BADGE.subn(remplacer_badge, contenu, count=1)

    if nombre_badge != 1:
        print("[ECHEC] " + chemin_relatif + " : bloc \"badge fichiers\" introuvable -> abandon (rien ecrit).")
        print("  Copiez-moi le resultat de :")
        print("    grep -n -B2 -A3 \"detail.fichiers|length\" " + chemin_relatif)
        return False

    contenu_corrige, nombre_bouton = REGEX_BOUTON.subn(remplacer_bouton, contenu_corrige, count=1)

    if nombre_bouton != 1:
        print("[ECHEC] " + chemin_relatif + " : bloc \"bouton Controler\" introuvable -> abandon (rien ecrit).")
        print("  Copiez-moi le resultat de :")
        print("    grep -n -B2 -A3 \"app_controle_pre_presse_controler\" " + chemin_relatif)
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

    resultats = []

    print("-" * 70)
    print("src/Controller/ControlePrePresseController.php")
    print("-" * 70)
    resultats.append(corriger_php(racine))
    print()

    print("-" * 70)
    print("templates/controle_pre_presse/index.html.twig")
    print("-" * 70)
    resultats.append(corriger_twig(racine))
    print()

    if resultats[0]:
        try:
            resultat = subprocess.run(
                ["php", "-l", os.path.join(racine, "src/Controller/ControlePrePresseController.php")],
                capture_output=True, text=True, timeout=30
            )
            print("php -l ControlePrePresseController.php : " + resultat.stdout.strip() + resultat.stderr.strip())
        except Exception:
            pass

    print()
    print("=" * 70)
    print("RESUME")
    print("=" * 70)

    if all(resultats):
        print("Tout est en place. Lancez maintenant :")
        print("  php bin/console cache:clear")
        print()
        print("Les lignes necessitant un controle prepresse mais sans")
        print("fichier attache apparaissent maintenant dans la liste,")
        print("avec un badge rouge « Fichier manquant » et un bouton")
        print("« Ajouter le fichier » qui ouvre directement la commande")
        print("pour joindre le fichier du client.")
    else:
        print("Un ou plusieurs fichiers n'ont pas pu etre modifies (voir [ECHEC] ci-dessus).")
        print("Recopiez-moi TOUT ce resume, je corrige avant de vous renvoyer le script.")


if __name__ == "__main__":
    main()
