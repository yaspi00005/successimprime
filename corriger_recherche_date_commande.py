#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrige l'erreur DQL "La classe App\\Entity\\Commandes ne possède
aucun champ ni association nommé createdAt" lors d'une recherche de
commandes par date (filtres "Du" / "Au").

Cause : le filtre de periode dans CommandesRepository utilisait le
nom de champ generique "createdAt" (un placeholder laisse par erreur,
avec un commentaire "Remplace createdAt si ta propriété de date
possède un autre nom dans Commandes"), alors que le vrai champ de
date sur l'entite Commandes s'appelle "dateCommande" (comme utilise
partout ailleurs dans ce meme fichier).

Usage:
    python3 corriger_recherche_date_commande.py /chemin/vers/successImprim
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


ANCIEN_BLOC = """        /*
         * Période.
         *
         * Remplace createdAt si ta propriété de date
         * possède un autre nom dans Commandes.
         */
        if (!empty($filtres['date_debut'])) {
            try {
                $dateDebut = new \\DateTimeImmutable(
                    $filtres['date_debut'] . ' 00:00:00'
                );

                $qb
                    ->andWhere('c.createdAt >= :dateDebut')
                    ->setParameter('dateDebut', $dateDebut);
            } catch (\\Exception) {
                // La date invalide est ignorée.
            }
        }

        if (!empty($filtres['date_fin'])) {
            try {
                $dateFin = new \\DateTimeImmutable(
                    $filtres['date_fin'] . ' 23:59:59'
                );

                $qb
                    ->andWhere('c.createdAt <= :dateFin')
                    ->setParameter('dateFin', $dateFin);
            } catch (\\Exception) {
                // La date invalide est ignorée.
            }
        }"""

NOUVEAU_BLOC = """        /*
         * Période.
         */
        if (!empty($filtres['date_debut'])) {
            try {
                $dateDebut = new \\DateTimeImmutable(
                    $filtres['date_debut'] . ' 00:00:00'
                );

                $qb
                    ->andWhere('c.dateCommande >= :dateDebut')
                    ->setParameter('dateDebut', $dateDebut);
            } catch (\\Exception) {
                // La date invalide est ignorée.
            }
        }

        if (!empty($filtres['date_fin'])) {
            try {
                $dateFin = new \\DateTimeImmutable(
                    $filtres['date_fin'] . ' 23:59:59'
                );

                $qb
                    ->andWhere('c.dateCommande <= :dateFin')
                    ->setParameter('dateFin', $dateFin);
            } catch (\\Exception) {
                // La date invalide est ignorée.
            }
        }"""

MARQUEUR = "c.dateCommande >= :dateDebut"


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

    if ANCIEN_BLOC not in contenu:
        print("[ECHEC] " + chemin_relatif + " : bloc introuvable -> abandon (rien ecrit).")
        print("  Votre fichier reel differe probablement du brouillon a cet endroit.")
        print("  Copiez-moi le resultat de :")
        print("    grep -n -B5 -A25 \"createdAt\" " + chemin_relatif)
        return False

    contenu_corrige = contenu.replace(ANCIEN_BLOC, NOUVEAU_BLOC, 1)

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

    chemin_relatif = "src/Repository/CommandesRepository.php"

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
        print("La recherche de commandes par date ('Du' / 'Au') doit")
        print("fonctionner sans erreur maintenant.")
    else:
        print("Le fichier n'a pas pu etre modifie (voir [ECHEC] ci-dessus).")
        print("Recopiez-moi TOUT ce resume, je corrige avant de vous renvoyer le script.")


if __name__ == "__main__":
    main()
