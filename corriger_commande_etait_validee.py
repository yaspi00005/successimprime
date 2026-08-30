#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrige l'avertissement "Variable non definie $commandeEtaitValidee"
lors de la modification d'une commande.

Cause : dans src/Controller/CommandesController.php, la ligne
"$commandeEtaitValidee =" a disparu devant l'appel a
$this->commandeEstValidee($commande), qui devient un appel orphelin
(le resultat est calcule puis jete). La variable n'est donc jamais
definie, d'ou l'avertissement des que le formulaire est soumis (CAS 1,
2, 3 de la logique brouillon/validee juste apres).

Ce script remet la ligne manquante.

Usage:
    python3 corriger_commande_etait_validee.py /chemin/vers/successImprim
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


MOTIF = re.compile(
    r"([ \t]*\n(?:[ \t]*\n)*)"
    r"([ \t]*)(\$this->commandeEstValidee\([ \t]*\n"
    r"[ \t]*\$commande[ \t]*\n"
    r"[ \t]*\);)"
    r"([ \t]*\n(?:[ \t]*\n)*)"
    r"([ \t]*)(\$circuitDejaCommence[ \t]*=)"
)


def _remplacement(m):
    interligne_avant = m.group(1)
    indent_appel = m.group(2)
    appel = m.group(3)
    interligne_milieu = m.group(4)
    indent_circuit = m.group(5)
    circuit = m.group(6)

    return (
        interligne_avant
        + indent_circuit + "$commandeEtaitValidee =\n"
        + indent_appel + appel
        + interligne_milieu
        + indent_circuit + circuit
    )


MARQUEUR = "$commandeEtaitValidee ="


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

    contenu_corrige, nb = MOTIF.subn(_remplacement, contenu, count=1)

    if nb == 0:
        print("[ECHEC] " + chemin_relatif + " : le bloc orphelin est introuvable -> abandon (rien ecrit).")
        print("  Copiez-moi le resultat de :")
        print("    sed -n '540,565p' " + chemin_relatif)
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

    try:
        resultat = subprocess.run(
            ["php", "-l", chemin_absolu],
            capture_output=True, text=True, timeout=30
        )
        print("  php -l : " + resultat.stdout.strip() + resultat.stderr.strip())
    except Exception:
        pass

    return True


def main():
    racine = sys.argv[1] if len(sys.argv) >= 2 else "."
    verifier_racine(racine)

    chemin_relatif = "src/Controller/CommandesController.php"

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
        print("L'avertissement 'Variable non definie $commandeEtaitValidee'")
        print("ne doit plus apparaitre en modifiant une commande (changement")
        print("de quantite ou autre).")
    else:
        print("Le fichier n'a pas pu etre modifie (voir [ECHEC] ci-dessus).")
        print("Recopiez-moi TOUT ce resume, je corrige avant de vous renvoyer le script.")


if __name__ == "__main__":
    main()
