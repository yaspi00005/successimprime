#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrige "Échec de l'envoi : Informations du fichier invalides." lors
de l'envoi par morceaux d'un gros fichier TIFF en pre-presse.

Cause : le plafond de taille de l'envoi par morceaux etait reste a
600 Mo (herite de l'ancien envoi en un seul bloc), alors que l'envoi
par morceaux ne depend plus des limites PHP et peut accepter des
fichiers bien plus gros. Un TIFF prepresse depasse facilement 600 Mo.

Ce script :
  - remonte le plafond a 5 Go (juste une protection contre un envoi
    anormalement enorme, plus une vraie limite technique) ;
  - separe le message d'erreur generique en messages precis (taille
    depassee / nombre de morceaux excessif), pour un diagnostic plus
    simple si ca se reproduit.

Usage:
    python3 augmenter_plafond_taille_morceaux.py /chemin/vers/successImprim
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


ANCIEN_CONST = """     */
    private const TAILLE_MAX_MORCEAUX = 600 * 1024 * 1024;
    private const NOMBRE_MORCEAUX_MAX = 10000;"""

NOUVEAU_CONST = """     *
     * Le plafond ci-dessous ne dépend plus des limites PHP
     * (upload_max_filesize/post_max_size, prévues pour un envoi en un
     * seul bloc) : chaque morceau est petit quelle que soit la taille
     * totale du fichier. Il protège seulement l'espace disque du
     * serveur contre un envoi anormalement énorme — les fichiers
     * prépresse de plusieurs gigaoctets (TIFF haute résolution, grand
     * format) restent donc acceptés.
     */
    private const TAILLE_MAX_MORCEAUX = 5 * 1024 * 1024 * 1024;
    private const NOMBRE_MORCEAUX_MAX = 10000;"""

ANCIENNE_VALIDATION = """        if (
            $nomOriginal === ''
            || $taille <= 0
            || $taille > self::TAILLE_MAX_MORCEAUX
            || $nombreMorceaux <= 0
            || $nombreMorceaux > self::NOMBRE_MORCEAUX_MAX
        ) {
            return $this->json(
                ['message' => 'Informations du fichier invalides.'],
                Response::HTTP_UNPROCESSABLE_ENTITY
            );
        }"""

NOUVELLE_VALIDATION = """        if ($nomOriginal === '' || $taille <= 0 || $nombreMorceaux <= 0) {
            return $this->json(
                ['message' => 'Informations du fichier invalides.'],
                Response::HTTP_UNPROCESSABLE_ENTITY
            );
        }

        if ($taille > self::TAILLE_MAX_MORCEAUX) {
            return $this->json(
                ['message' => sprintf(
                    'Le fichier dépasse la taille maximale autorisée de %d Go.',
                    (int) (self::TAILLE_MAX_MORCEAUX / 1024 / 1024 / 1024)
                )],
                Response::HTTP_UNPROCESSABLE_ENTITY
            );
        }

        if ($nombreMorceaux > self::NOMBRE_MORCEAUX_MAX) {
            return $this->json(
                ['message' => 'Le fichier est trop volumineux pour être envoyé par morceaux.'],
                Response::HTTP_UNPROCESSABLE_ENTITY
            );
        }"""

MARQUEUR = "TAILLE_MAX_MORCEAUX = 5 * 1024 * 1024 * 1024"


def corriger_fichier(racine, chemin_relatif):
    chemin_absolu = os.path.join(racine, chemin_relatif)

    if not os.path.isfile(chemin_absolu):
        print("[ABSENT] " + chemin_relatif + " n'existe pas du tout sur le disque.")
        return False

    with open(chemin_absolu, "r", encoding="utf-8") as f:
        contenu = f.read()

    if MARQUEUR in contenu:
        print("[SKIP] " + chemin_relatif + " contient deja le plafond de 5 Go (deja applique).")
        return True

    if ANCIEN_CONST not in contenu:
        print("[ECHEC] " + chemin_relatif + " : constantes TAILLE_MAX_MORCEAUX/NOMBRE_MORCEAUX_MAX introuvables -> abandon (rien ecrit).")
        print("  Copiez-moi le resultat de :")
        print("    grep -n \"TAILLE_MAX_MORCEAUX\\|NOMBRE_MORCEAUX_MAX\" " + chemin_relatif)
        return False

    if ANCIENNE_VALIDATION not in contenu:
        print("[ECHEC] " + chemin_relatif + " : bloc de validation introuvable -> abandon (rien ecrit).")
        print("  Copiez-moi le resultat de :")
        print("    grep -n -A10 \"Informations du fichier invalides\" " + chemin_relatif)
        return False

    contenu_corrige = contenu.replace(ANCIEN_CONST, NOUVEAU_CONST, 1)
    contenu_corrige = contenu_corrige.replace(ANCIENNE_VALIDATION, NOUVELLE_VALIDATION, 1)

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

    chemin_relatif = "src/Controller/ControlePrePresseController.php"

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
        print("Le plafond de l'envoi par morceaux est maintenant de 5 Go")
        print("au lieu de 600 Mo. Reessayez votre fichier TIFF.")
    else:
        print("Le fichier n'a pas pu etre modifie (voir [ECHEC] ci-dessus).")
        print("Recopiez-moi TOUT ce resume, je corrige avant de vous renvoyer le script.")


if __name__ == "__main__":
    main()
