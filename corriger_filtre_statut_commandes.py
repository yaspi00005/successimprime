#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrige la liste des commandes :

  1. Retire le filtre "Statut de paiement" : il est mort depuis
     longtemps (la variable "statuts" n'est jamais transmise par le
     contrôleur, donc ce menu ne propose jamais que "Tous les
     statuts" et ne filtre jamais rien). Le vrai filtre de paiement
     est "Situation financière" (Non payée / Paiement partiel /
     Entièrement payée), qui reste inchangé et fonctionne
     correctement.

  2. Corrige une faute de casse (montantAPayer au lieu de
     montantApayer) qui faisait planter le tri "Reste à payer
     décroissant" sur la liste des commandes.

Fichiers concernes :
  - templates/commandes/index.html.twig
  - src/Repository/CommandesRepository.php

Usage:
    python3 corriger_filtre_statut_commandes.py /chemin/vers/successImprim
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


def corriger(chemin_relatif, racine, ancien, nouveau, description):
    chemin_absolu = os.path.join(racine, chemin_relatif)

    if not os.path.isfile(chemin_absolu):
        print("[ABSENT] " + chemin_relatif + " n'existe pas du tout sur le disque.")
        return False

    with open(chemin_absolu, "r", encoding="utf-8") as f:
        contenu = f.read()

    if ancien not in contenu:
        if nouveau in contenu:
            print("[SKIP] " + chemin_relatif + " : " + description + " (deja applique)")
            return True

        print("[ECHEC] " + chemin_relatif + " : " + description + " -> bloc de reference introuvable.")
        return False

    if contenu.count(ancien) > 1:
        print("[ECHEC] " + chemin_relatif + " : " + description + " -> bloc trouve plusieurs fois, abandon.")
        return False

    contenu_corrige = contenu.replace(ancien, nouveau, 1)

    with open(chemin_absolu, "w", encoding="utf-8", newline="") as f:
        f.write(contenu_corrige)
        f.flush()
        os.fsync(f.fileno())

    with open(chemin_absolu, "r", encoding="utf-8", newline="") as f:
        relu = f.read()

    if relu != contenu_corrige:
        print("[ECHEC VERIFICATION] " + chemin_relatif + " : le contenu relu ne correspond pas.")
        return False

    print("[OK VERIFIE] " + chemin_relatif + " : " + description)
    print("  Chemin reel : " + os.path.realpath(chemin_absolu))
    return True


TMPL_ANCIEN = '\t\t\t\t\t\t\t<div class="form-group">\n\t\t\t\t\t\t\t\t<label class="form-label">Statut de paiement</label>\n\t\t\t\t\t\t\t\t<select name="statut" class="form-control custom-select">\n\t\t\t\t\t\t\t\t\t<option value="">Tous les statuts</option>\n\t\t\t\t\t\t\t\t\t{% for statut in statuts|default([]) %}\n\t\t\t\t\t\t\t\t\t\t<option value="{{ statut.id }}" {{ filtres.statut|default(\'\') == statut.id ? \'selected\' : \'\' }}>\n\t\t\t\t\t\t\t\t\t\t\t{{ statut }}\n\t\t\t\t\t\t\t\t\t\t</option>\n\t\t\t\t\t\t\t\t\t{% endfor %}\n\t\t\t\t\t\t\t\t</select>\n\t\t\t\t\t\t\t</div>\n\n\t\t\t\t\t\t\t<div class="form-group">\n\t\t\t\t\t\t\t\t<label class="form-label">État des travaux</label>'
TMPL_NOUVEAU = '\t\t\t\t\t\t\t<div class="form-group">\n\t\t\t\t\t\t\t\t<label class="form-label">État des travaux</label>'

REPO_ANCIEN = "'(c.totalTtc - COALESCE(c.montantAPayer, 0))\n                     AS HIDDEN resteAPayer'"
REPO_NOUVEAU = "'(c.totalTtc - COALESCE(c.montantApayer, 0))\n                     AS HIDDEN resteAPayer'"


def main():
    racine = sys.argv[1] if len(sys.argv) >= 2 else "."
    verifier_racine(racine)

    resultats = []

    print("-" * 70)
    print("templates/commandes/index.html.twig")
    print("-" * 70)
    resultats.append(corriger(
        "templates/commandes/index.html.twig", racine,
        TMPL_ANCIEN, TMPL_NOUVEAU,
        "retrait du filtre mort 'Statut de paiement'"
    ))
    print()

    print("-" * 70)
    print("src/Repository/CommandesRepository.php")
    print("-" * 70)
    resultats.append(corriger(
        "src/Repository/CommandesRepository.php", racine,
        REPO_ANCIEN, REPO_NOUVEAU,
        "correction montantAPayer -> montantApayer (tri reste a payer)"
    ))
    print()

    chemin_repo = os.path.join(racine, "src/Repository/CommandesRepository.php")
    try:
        resultat = subprocess.run(
            ["php", "-l", chemin_repo],
            capture_output=True, text=True, timeout=30
        )
        print("php -l CommandesRepository.php : " + resultat.stdout.strip() + resultat.stderr.strip())
    except Exception:
        pass

    print()
    print("=" * 70)
    print("RESUME")
    print("=" * 70)

    if all(resultats):
        print("Tout est en place.")
        print()
        print("Il ne reste que le filtre 'Situation financière' (Non payee /")
        print("Paiement partiel / Entierement payee) sur la liste des")
        print("commandes -- c'est le seul qui a toujours fonctionne.")
    else:
        print("Un ou plusieurs fichiers n'ont pas pu etre modifies (voir [ECHEC] ci-dessus).")
        print("Recopiez-moi TOUT ce resume, je corrige avant de vous renvoyer le script.")


if __name__ == "__main__":
    main()