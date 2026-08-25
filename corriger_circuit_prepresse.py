#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrige le circuit de traitement : une ligne de commande en impression
directe (prePresseNecessaire = false, deja gere correctement au niveau
de l'entite CommandesDetails) ne doit jamais apparaitre dans la file
d'attente prepresse, meme si un fichier y est rattache.

Cause reelle : la requete de la file d'attente prepresse
(ControlePrePresseController::index()) et celle de l'alerte sonore
(verifierNouveaux()) filtraient uniquement sur "a un fichier actif",
sans jamais verifier le champ prePresseNecessaire de la ligne.

Ce script :
  1) ajoute le filtre manquant sur les 2 requetes ;
  2) bloque aussi l'acces direct par URL a l'ecran de controle pour
     une ligne en impression directe (redirection + message).

Usage:
    python3 corriger_circuit_prepresse.py /chemin/vers/successImprim
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


BLOC_1_ANCIEN = """        /*
         * Affiche uniquement les lignes ayant au moins un fichier.
         */
        $details = $detailsRepository
            ->createQueryBuilder('detail')
            ->addSelect('commande', 'produit', 'fichier')
            ->innerJoin('detail.commande', 'commande')
            ->leftJoin('detail.produit', 'produit')
            ->innerJoin('detail.fichiers', 'fichier')
            ->andWhere('fichier.actif = :actif')
            ->setParameter('actif', true)
            ->orderBy('commande.dateCommande', 'DESC')
            ->addOrderBy('detail.id', 'DESC')
            ->distinct()
            ->getQuery()
            ->getResult();"""

BLOC_1_NOUVEAU = """        /*
         * Affiche uniquement les lignes ayant au moins un fichier
         * ET nécessitant réellement un contrôle prépresse : une
         * ligne en impression directe (prePresseNecessaire = false)
         * ne doit jamais apparaître ici, même si un fichier y est
         * rattaché.
         */
        $details = $detailsRepository
            ->createQueryBuilder('detail')
            ->addSelect('commande', 'produit', 'fichier')
            ->innerJoin('detail.commande', 'commande')
            ->leftJoin('detail.produit', 'produit')
            ->innerJoin('detail.fichiers', 'fichier')
            ->andWhere('fichier.actif = :actif')
            ->andWhere('detail.prePresseNecessaire = :prepresseNecessaire')
            ->setParameter('actif', true)
            ->setParameter('prepresseNecessaire', true)
            ->orderBy('commande.dateCommande', 'DESC')
            ->addOrderBy('detail.id', 'DESC')
            ->distinct()
            ->getQuery()
            ->getResult();"""

BLOC_2_ANCIEN = """        $ids = $detailsRepository
            ->createQueryBuilder('detail')
            ->select('detail.id')
            ->innerJoin('detail.fichiers', 'fichier')
            ->leftJoin('detail.controlesPrePresse', 'controle')
            ->andWhere('fichier.actif = :actif')
            ->andWhere('controle.id IS NULL')
            ->setParameter('actif', true)
            ->distinct()
            ->getQuery()
            ->getResult();"""

BLOC_2_NOUVEAU = """        $ids = $detailsRepository
            ->createQueryBuilder('detail')
            ->select('detail.id')
            ->innerJoin('detail.fichiers', 'fichier')
            ->leftJoin('detail.controlesPrePresse', 'controle')
            ->andWhere('fichier.actif = :actif')
            ->andWhere('controle.id IS NULL')
            ->andWhere('detail.prePresseNecessaire = :prepresseNecessaire')
            ->setParameter('actif', true)
            ->setParameter('prepresseNecessaire', true)
            ->distinct()
            ->getQuery()
            ->getResult();"""

BLOC_3_ANCIEN = """    if ($detail->getFichiers()->isEmpty()) {
        $this->addFlash(
            'warning',
            'Cette ligne de commande ne contient aucun fichier.'
        );

        return $this->redirectToRoute(
            'app_controle_pre_presse_index'
        );
    }"""

BLOC_3_NOUVEAU = """    if ($detail->getFichiers()->isEmpty()) {
        $this->addFlash(
            'warning',
            'Cette ligne de commande ne contient aucun fichier.'
        );

        return $this->redirectToRoute(
            'app_controle_pre_presse_index'
        );
    }


    /*
     * ============================================================
     * IMPRESSION DIRECTE : PAS DE PRÉPRESSE
     * ============================================================
     */

    if (!$detail->isPrePresseNecessaire()) {
        $this->addFlash(
            'warning',
            'Cette ligne de commande est en impression directe et ne nécessite pas de contrôle prépresse.'
        );

        return $this->redirectToRoute(
            'app_controle_pre_presse_index'
        );
    }"""

MARQUEUR = "IMPRESSION DIRECTE : PAS DE PRÉPRESSE"


def main():
    racine = sys.argv[1] if len(sys.argv) >= 2 else "."
    verifier_racine(racine)

    if not PHP_LINT_DISPONIBLE:
        print("(info : commande 'php' introuvable ici, le controle 'php -l' sera saute)")
        print()

    chemin_relatif = "src/Controller/ControlePrePresseController.php"
    chemin_absolu = os.path.join(racine, chemin_relatif)

    print("-" * 70)
    print("Correction du circuit prépresse / impression directe (" + chemin_relatif + ")")
    print("-" * 70)

    if not os.path.isfile(chemin_absolu):
        print("[ABSENT] " + chemin_relatif + " n'existe pas du tout sur le disque.")
        sys.exit(1)

    with open(chemin_absolu, "r", encoding="utf-8") as f:
        contenu = f.read()

    if MARQUEUR in contenu:
        print("[SKIP] Le correctif est deja applique.")
        return

    blocs = [
        (BLOC_1_ANCIEN, BLOC_1_NOUVEAU),
        (BLOC_2_ANCIEN, BLOC_2_NOUVEAU),
        (BLOC_3_ANCIEN, BLOC_3_NOUVEAU),
    ]

    for idx, (ancien, nouveau) in enumerate(blocs, start=1):
        occurrences = contenu.count(ancien)
        if occurrences != 1:
            print("[ECHEC] Bloc " + str(idx) + "/" + str(len(blocs)) +
                  " trouve " + str(occurrences) + " fois au lieu de 1 -> abandon (rien ecrit).")
            print("  Extrait attendu (debut) : " + repr(ancien[:150]))
            print()
            print("Recopiez-moi ce message : le fichier a peut-etre change entre-temps.")
            sys.exit(1)
        contenu = contenu.replace(ancien, nouveau, 1)

    with open(chemin_absolu, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
        f.flush()
        os.fsync(f.fileno())

    with open(chemin_absolu, "r", encoding="utf-8", newline="") as f:
        relu = f.read()

    if relu != contenu:
        print("[ECHEC VERIFICATION] le contenu relu ne correspond pas a ce qui etait attendu.")
        sys.exit(1)

    print("[OK VERIFIE] " + chemin_relatif + " (3 correctif(s) applique(s))")
    print("  Chemin reel : " + os.path.realpath(chemin_absolu))
    lint_php_si_possible(chemin_absolu)
    print()
    print("Tout est en place. Lancez maintenant :")
    print("  php bin/console cache:clear")
    print("puis verifiez qu'une ligne de commande en impression directe")
    print("(avec un fichier rattache) n'apparait plus dans la file prepresse,")
    print("et va directement en production.")


if __name__ == "__main__":
    main()
