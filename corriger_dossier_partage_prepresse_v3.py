#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrige et finalise le "dossier partage" :

  1. Crash "return value must be of type App\Controller\Response"
     (deja corrige precedemment si vous avez lance le script d'avant).

  2. Retire le lien en double sous Parametres.

  3. Ajoute le lien sous Prepresse (version courte et fiable, sans
     dependre de l'indentation exacte du fichier).

Fichiers concernes :
  - src/Controller/FichierUploadController.php
  - templates/base.html.twig
  - templates/commande_fichiers/dossier_partage.html.twig

Usage:
    python3 corriger_dossier_partage_prepresse_v3.py /chemin/vers/successImprim
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


def lire(chemin):
    with open(chemin, "r", encoding="utf-8") as f:
        return f.read()


def ecrire(chemin, contenu):
    with open(chemin, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
        f.flush()
        os.fsync(f.fileno())

    with open(chemin, "r", encoding="utf-8", newline="") as f:
        relu = f.read()

    return relu == contenu


def appliquer_paires(racine, chemin_relatif, paires):
    chemin_absolu = os.path.join(racine, chemin_relatif)

    if not os.path.isfile(chemin_absolu):
        print("[ABSENT] " + chemin_relatif + " n'existe pas du tout sur le disque.")
        return False

    contenu = lire(chemin_absolu)
    contenu_original = contenu
    tout_ok = True

    for ancien, nouveau, description in paires:
        if nouveau in contenu:
            print("  [SKIP] " + description + " (deja applique)")
            continue

        if ancien not in contenu:
            print("  [ECHEC] " + description + " : bloc de reference introuvable.")
            tout_ok = False
            continue

        if contenu.count(ancien) > 1:
            print("  [ECHEC] " + description + " : bloc de reference trouve plusieurs fois, abandon par prudence.")
            tout_ok = False
            continue

        contenu = contenu.replace(ancien, nouveau, 1)
        print("  [OK] " + description)

    if contenu == contenu_original:
        return tout_ok

    if not ecrire(chemin_absolu, contenu):
        print("[ECHEC VERIFICATION] " + chemin_relatif + " : le contenu relu ne correspond pas.")
        return False

    print("[OK VERIFIE] " + chemin_relatif)
    print("  Chemin reel : " + os.path.realpath(chemin_absolu))
    return tout_ok


CTRL_PAIRES = [
    (
        'use Symfony\\Component\\HttpFoundation\\ResponseHeaderBag;\nuse Symfony\\Component\\HttpKernel\\KernelInterface;\n',
        'use Symfony\\Component\\HttpFoundation\\Response;\nuse Symfony\\Component\\HttpFoundation\\ResponseHeaderBag;\nuse Symfony\\Component\\HttpKernel\\KernelInterface;\n',
        "import de Response manquant"
    ),
    (
        "    public function dossierPartage(): Response\n    {\n        $this->denyAccessUnlessGranted('ROLE_ADMIN');",
        "    public function dossierPartage(): Response\n    {\n        $this->denyAccessUnlessGranted('ROLE_PREPRESSE');",
        "role ROLE_PREPRESSE sur dossierPartage()"
    ),
    (
        "    ): Response {\n        $this->denyAccessUnlessGranted('ROLE_ADMIN');\n\n        if (!$this->isCsrfTokenValid(\n            'dossier-partage-importer',",
        "    ): Response {\n        $this->denyAccessUnlessGranted('ROLE_PREPRESSE');\n\n        if (!$this->isCsrfTokenValid(\n            'dossier-partage-importer',",
        "role ROLE_PREPRESSE sur importerDossierPartage()"
    ),
]

BASE_PAIRES = [
    (
        '<a href="{{ path( \'app_lot_etiquette_index\' ) }}" class="slide-item">\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\tLots d\'étiquettes\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t</a>\n\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t<a href="{{ path( \'app_fichier_dossier_partage\' ) }}" class="slide-item">\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\tDossier partagé (import fichiers)\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t</a>',
        '<a href="{{ path( \'app_lot_etiquette_index\' ) }}" class="slide-item">\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\tLots d\'étiquettes\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t</a>',
        "retrait du lien en double sous Parametres"
    ),
    (
        'Prépresse\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t</a>',
        'Prépresse\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t</a>\n\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t<a href="{{ path( \'app_fichier_dossier_partage\' ) }}" class="slide-item {{ routeCourante starts with \'app_fichier_dossier_partage\' ? \'active\' : \'\' }}">\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t<i class="fa fa-folder-open-o mr-2"></i>\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tDossier partagé\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t</a>',
        "ajout du lien sous Prepresse"
    ),
]

TMPL_PAIRES = [
    (
        '<li class="breadcrumb-item">\n\t\t\t\t\t<a href="#">Paramètres</a>\n\t\t\t\t</li>',
        '<li class="breadcrumb-item">\n\t\t\t\t\t<a href="{{ path(\'app_controle_pre_presse_index\') }}">Prépresse</a>\n\t\t\t\t</li>',
        "fil d'ariane Prepresse au lieu de Parametres"
    ),
]


def main():
    racine = sys.argv[1] if len(sys.argv) >= 2 else "."
    verifier_racine(racine)

    resultats = []

    print("-" * 70)
    print("src/Controller/FichierUploadController.php")
    print("-" * 70)
    resultats.append(appliquer_paires(racine, "src/Controller/FichierUploadController.php", CTRL_PAIRES))
    print()

    print("-" * 70)
    print("templates/base.html.twig")
    print("-" * 70)
    resultats.append(appliquer_paires(racine, "templates/base.html.twig", BASE_PAIRES))
    print()

    print("-" * 70)
    print("templates/commande_fichiers/dossier_partage.html.twig")
    print("-" * 70)
    resultats.append(appliquer_paires(racine, "templates/commande_fichiers/dossier_partage.html.twig", TMPL_PAIRES))
    print()

    chemin_controller = os.path.join(racine, "src/Controller/FichierUploadController.php")
    try:
        resultat = subprocess.run(
            ["php", "-l", chemin_controller],
            capture_output=True, text=True, timeout=30
        )
        print("php -l FichierUploadController.php : " + resultat.stdout.strip() + resultat.stderr.strip())
    except Exception:
        pass

    print()
    print("=" * 70)
    print("RESUME")
    print("=" * 70)

    if all(resultats):
        print("Tout est en place.")
        print()
        print("Derniere etape :")
        print("  php bin/console cache:clear")
        print()
        print("Changement :")
        print("  - Le lien 'Dossier partage' est maintenant UNIQUEMENT dans")
        print("    le menu Prepresse (retire de Parametres).")
        print("  - Accessible aux comptes ROLE_PREPRESSE (les admins")
        print("    y ont toujours acces).")
    else:
        print("Un ou plusieurs fichiers n'ont pas pu etre modifies (voir [ECHEC] ci-dessus).")
        print("Recopiez-moi TOUT ce resume, je corrige avant de vous renvoyer le script.")


if __name__ == "__main__":
    main()
    