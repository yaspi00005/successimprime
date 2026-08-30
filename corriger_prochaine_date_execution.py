#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrige l'erreur "La colonne prochaine_date_execution ne peut pas
etre nulle" a la creation d'une charge recurrente.

Cause : il manquait l'annotation Doctrine #[ORM\HasLifecycleCallbacks]
sur la classe DecaissementRecurrent. Sans elle, Doctrine n'appelle
jamais la methode initialiser() (marquee #[ORM\PrePersist]) qui
calcule automatiquement la premiere echeance -> la colonne reste
vide et la base de donnees refuse l'enregistrement.

Usage:
    python3 corriger_prochaine_date_execution.py /chemin/vers/successImprim
"""

import os
import sys
import shutil
import subprocess


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


PHP_LINT_DISPONIBLE = shutil.which("php") is not None


def lint_php_si_possible(chemin_absolu):
    if not PHP_LINT_DISPONIBLE:
        return
    try:
        resultat = subprocess.run(
            ["php", "-l", chemin_absolu],
            capture_output=True, text=True, timeout=10,
        )
        sortie = (resultat.stdout + resultat.stderr).strip()
        if resultat.returncode == 0:
            print("  php -l : OK")
        else:
            print("  [ATTENTION] php -l a signale un probleme :")
            print("  " + sortie.replace("\n", "\n  "))
    except Exception as exc:
        print("  (php -l ignore : " + repr(exc) + ")")


ANCIEN = """#[ORM\\Entity(repositoryClass: DecaissementRecurrentRepository::class)]
#[ORM\\Table(name: 'decaissement_recurrent')]
class DecaissementRecurrent
{"""

NOUVEAU = """#[ORM\\Entity(repositoryClass: DecaissementRecurrentRepository::class)]
#[ORM\\Table(name: 'decaissement_recurrent')]
#[ORM\\HasLifecycleCallbacks]
class DecaissementRecurrent
{"""

MARQUEUR = "HasLifecycleCallbacks"


def main():
    racine = sys.argv[1] if len(sys.argv) >= 2 else "."
    verifier_racine(racine)

    chemin_relatif = "src/Entity/DecaissementRecurrent.php"
    chemin_absolu = os.path.join(racine, chemin_relatif)

    print("-" * 70)
    print("Correction de " + chemin_relatif)
    print("-" * 70)

    if not os.path.isfile(chemin_absolu):
        print("[ABSENT] " + chemin_relatif + " n'existe pas -> avez-vous bien applique")
        print("ajouter_decaissements_recurrents.py avant celui-ci ?")
        sys.exit(1)

    with open(chemin_absolu, "r", encoding="utf-8") as f:
        contenu = f.read()

    if MARQUEUR in contenu:
        print("[SKIP] Deja corrige.")
        return

    occurrences = contenu.count(ANCIEN)
    if occurrences != 1:
        print("[ECHEC] Repere introuvable (trouve " + str(occurrences) + " fois au lieu de 1) -> abandon (rien ecrit).")
        print("Recopiez-moi ce message.")
        sys.exit(1)

    contenu_nouveau = contenu.replace(ANCIEN, NOUVEAU, 1)

    with open(chemin_absolu, "w", encoding="utf-8", newline="") as f:
        f.write(contenu_nouveau)
        f.flush()
        os.fsync(f.fileno())

    with open(chemin_absolu, "r", encoding="utf-8", newline="") as f:
        relu = f.read()

    if relu != contenu_nouveau:
        print("[ECHEC VERIFICATION] le contenu relu ne correspond pas.")
        sys.exit(1)

    print("[OK VERIFIE] " + chemin_relatif)
    print("  Chemin reel : " + os.path.realpath(chemin_absolu))
    lint_php_si_possible(chemin_absolu)
    print()
    print("Tout est en place. Lancez maintenant :")
    print("  php bin/console cache:clear")
    print("puis reessayez de creer une charge recurrente.")


if __name__ == "__main__":
    main()
