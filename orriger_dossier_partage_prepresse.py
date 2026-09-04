#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrige le "dossier partage" livre precedemment :

  1. Crash "return value must be of type App\Controller\Response"
     sur /commande-fichiers/dossier-partage : l'import de la classe
     Symfony\Component\HttpFoundation\Response manquait dans
     FichierUploadController.php.

  2. Deplace la fonctionnalite de Parametres (reserve aux admins)
     vers Prepresse : la page et le bouton "Lancer l'import" sont
     maintenant accessibles a ROLE_PREPRESSE (les administrateurs
     y ont toujours acces, par heritage de role).

Fichiers concernes :
  - src/Controller/FichierUploadController.php
  - templates/base.html.twig
  - templates/commande_fichiers/dossier_partage.html.twig

Usage:
    python3 corriger_dossier_partage_prepresse.py /chemin/vers/successImprim
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
        '<a href="{{ path( \'app_controle_pre_presse_index\' ) }}" class="\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tslide-item\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t{{\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\trouteCourante\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tstarts with\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\'app_controle_pre_presse_\'\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t? \'active\'\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t: \'\'\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t}}\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t">\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t<i class="\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tfa\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tfa-check-square-o\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tmr-2\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t"></i>\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tPrépresse\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t</a>',
        '<a href="{{ path( \'app_controle_pre_presse_index\' ) }}" class="\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tslide-item\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t{{\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\trouteCourante\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tstarts with\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\'app_controle_pre_presse_\'\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t? \'active\'\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t: \'\'\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t}}\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t">\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t<i class="\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tfa\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tfa-check-square-o\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tmr-2\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t"></i>\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tPrépresse\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t</a>\n\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t<a href="{{ path( \'app_fichier_dossier_partage\' ) }}" class="\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tslide-item\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t{{\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\trouteCourante\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tstarts with\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\'app_fichier_dossier_partage\'\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t? \'active\'\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t: \'\'\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t}}\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t">\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t<i class="\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tfa\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tfa-folder-open-o\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tmr-2\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t"></i>\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tDossier partagé\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t</a>',
        "lien deplace de Parametres vers Prepresse"
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
        print("  - Le lien 'Dossier partage' est maintenant dans le menu")
        print("    Prepresse (plus dans Parametres).")
        print("  - Accessible aux comptes ROLE_PREPRESSE (les admins")
        print("    y ont toujours acces).")
    else:
        print("Un ou plusieurs fichiers n'ont pas pu etre modifies (voir [ECHEC] ci-dessus).")
        print("Recopiez-moi TOUT ce resume, je corrige avant de vous renvoyer le script.")


if __name__ == "__main__":
    main()
    