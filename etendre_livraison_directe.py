#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Etend le bouton "Marquer comme livre" (ajoute par
ajouter_livraison_directe.py) a TOUTES les lignes de commande, et pas
seulement aux ventes directes (articles en stock sans fabrication).

Demande : pouvoir marquer une ligne comme livree directement meme
quand elle nécessite normalement une fabrication/un controle
prepresse (kakemono deja traite/remis au client en dehors du
logiciel), sans avoir a joindre de fichier ni a passer par les etapes
de production.

Ce script :
  1. dans LivraisonController::livrerDirectement(), retire la
     condition qui bloquait le bouton aux seules lignes sans
     fabrication, et rend la sortie de stock generique (fonctionne
     aussi bien pour un article de vente directe que pour un produit
     dont la gestion de stock est activee) ;
  2. dans commandes/show.html.twig, retire la meme restriction sur
     l'affichage du bouton, et clarifie le message de confirmation
     (precise que ca saute le controle prepresse et la production).

Usage:
    python3 etendre_livraison_directe.py /chemin/vers/successImprim
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


# ============================================================
# PRE-REQUIS : le script ajouter_livraison_directe.py doit avoir
# deja ete applique (sinon les blocs de reference n'existeront pas).
# ============================================================

MARQUEUR_PREREQUIS_PHP = "livrer_directement"
MARQUEUR_PREREQUIS_TWIG = "app_livraisons_livrer_directement"


# ============================================================
# FICHIER 1 : src/Controller/LivraisonController.php
# ============================================================

ANCIEN_PHP = """        try {
            if ($detail->isProductionNecessaire()) {
                throw new \\LogicException(
                    'Cette ligne nécessite une production et ne peut pas être livrée directement.'
                );
            }

            if (
                $detail->getStatutProduction()
                === CommandesDetails::PRODUCTION_A_PRODUIRE
            ) {
                $detail->marquerProductionNonRequise();
            }

            if (
                $detail->getStatutProduction()
                === CommandesDetails::PRODUCTION_NON_REQUISE
            ) {
                $detail->marquerPreteLivraison();
            }

            if (
                $detail->getStatutProduction()
                === CommandesDetails::PRODUCTION_PRETE_LIVRAISON
            ) {
                $detail->marquerEnLivraison();
            }

            if (
                $detail->getStatutProduction()
                !== CommandesDetails::PRODUCTION_EN_LIVRAISON
            ) {
                throw new \\LogicException(
                    'Cette ligne n’est pas dans un état permettant une livraison directe.'
                );
            }

            if (
                $detail->getTypeLigne()
                === CommandesDetails::TYPE_ARTICLE
            ) {
                $article = $detail->getArticle();

                $quantite = (float) $detail->getQuantite();

                if ($article !== null && $quantite > 0) {
                    $stockService->consommerPourDetail(
                        $detail,
                        StockSorties::ORIGINE_LIVRAISON,
                        sprintf(
                            'LIV-DIRECT-%06d',
                            (int) $detail->getId()
                        ),
                        $quantite
                    );
                }
            }

            $detail->marquerLivree();"""

NOUVEAU_PHP = """        try {
            /*
             * Bouton de secours : permet de fermer n'importe quelle
             * ligne (avec ou sans fabrication, avec ou sans contrôle
             * prépresse) quand elle a déjà été traitée/remise au
             * client en dehors du logiciel. On force donc le passage
             * à "non requise" si la production n'a pas encore
             * démarré, quel que soit le type de ligne.
             */
            if (
                $detail->getStatutProduction()
                === CommandesDetails::PRODUCTION_A_PRODUIRE
            ) {
                $detail->marquerProductionNonRequise();
            }

            if (
                $detail->getStatutProduction()
                === CommandesDetails::PRODUCTION_NON_REQUISE
            ) {
                $detail->marquerPreteLivraison();
            }

            if (
                $detail->getStatutProduction()
                === CommandesDetails::PRODUCTION_PRETE_LIVRAISON
            ) {
                $detail->marquerEnLivraison();
            }

            if (
                $detail->getStatutProduction()
                !== CommandesDetails::PRODUCTION_EN_LIVRAISON
            ) {
                throw new \\LogicException(
                    'Cette ligne n’est pas dans un état permettant une livraison directe.'
                );
            }

            /*
             * Sortie de stock quel que soit le type de ligne :
             * calculerBesoinsDetail() sait determiner s'il y a
             * reellement une reservation a consommer (article de
             * vente directe, ou produit dont la gestion de stock est
             * activee) et ne fait rien sinon.
             */
            $quantite = (float) $detail->getQuantite();

            if ($quantite > 0) {
                $stockService->consommerPourDetail(
                    $detail,
                    StockSorties::ORIGINE_LIVRAISON,
                    sprintf(
                        'LIV-DIRECT-%06d',
                        (int) $detail->getId()
                    ),
                    $quantite
                );
            }

            $detail->marquerLivree();"""

MARQUEUR_PHP = "Bouton de secours"


def corriger_php(racine):
    chemin_relatif = "src/Controller/LivraisonController.php"
    chemin_absolu = os.path.join(racine, chemin_relatif)

    if not os.path.isfile(chemin_absolu):
        print("[ABSENT] " + chemin_relatif + " n'existe pas du tout sur le disque.")
        return False

    with open(chemin_absolu, "r", encoding="utf-8") as f:
        contenu = f.read()

    if MARQUEUR_PHP in contenu:
        print("[SKIP] " + chemin_relatif + " contient deja le correctif (deja applique).")
        return True

    if MARQUEUR_PREREQUIS_PHP not in contenu:
        print("[ECHEC] " + chemin_relatif + " : le script ajouter_livraison_directe.py ne semble pas avoir ete applique -> abandon.")
        print("  Lancez d'abord ajouter_livraison_directe.py.")
        return False

    if ANCIEN_PHP not in contenu:
        print("[ECHEC] " + chemin_relatif + " : bloc de reference introuvable -> abandon (rien ecrit).")
        print("  Copiez-moi le resultat de :")
        print("    grep -n -A20 \"function livrerDirectement\" " + chemin_relatif)
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
# FICHIER 2 : templates/commandes/show.html.twig
# ============================================================

ANCIEN_TWIG = (
    ("\t" * 12) + "{% if (is_granted('ROLE_LIVRAISON') or estAdmin) and detail.estLivraisonDirecte and detail.statutProduction != 'livree' %}\n"
    "\n"
    + ("\t" * 13) + "<form method=\"post\" action=\"{{ path( 'app_livraisons_livrer_directement', { id: detail.id } ) }}\" class=\"js-confirm-form\" data-message=\"Marquer « {{ detail.designation|default('ce travail') }} » comme livré ? Le stock réservé sera définitivement sorti.\">"
)

NOUVEAU_TWIG = (
    ("\t" * 12) + "{% if (is_granted('ROLE_LIVRAISON') or estAdmin) and detail.statutProduction != 'livree' %}\n"
    "\n"
    + ("\t" * 13) + "<form method=\"post\" action=\"{{ path( 'app_livraisons_livrer_directement', { id: detail.id } ) }}\" class=\"js-confirm-form\" data-message=\"Marquer « {{ detail.designation|default('ce travail') }} » comme livré, sans passer par le contrôle prépresse ni la production ? Le stock réservé sera définitivement sorti.\">"
)

MARQUEUR_TWIG = "sans passer par le contrôle prépresse"


def corriger_twig(racine):
    chemin_relatif = "templates/commandes/show.html.twig"
    chemin_absolu = os.path.join(racine, chemin_relatif)

    if not os.path.isfile(chemin_absolu):
        print("[ABSENT] " + chemin_relatif + " n'existe pas du tout sur le disque.")
        return False

    with open(chemin_absolu, "r", encoding="utf-8") as f:
        contenu = f.read()

    if MARQUEUR_TWIG in contenu:
        print("[SKIP] " + chemin_relatif + " contient deja le correctif (deja applique).")
        return True

    if MARQUEUR_PREREQUIS_TWIG not in contenu:
        print("[ECHEC] " + chemin_relatif + " : le script ajouter_livraison_directe.py ne semble pas avoir ete applique -> abandon.")
        print("  Lancez d'abord ajouter_livraison_directe.py.")
        return False

    if ANCIEN_TWIG not in contenu:
        print("[ECHEC] " + chemin_relatif + " : bloc de reference introuvable -> abandon (rien ecrit).")
        print("  Copiez-moi le resultat de :")
        print("    grep -n -B2 -A3 \"app_livraisons_livrer_directement\" " + chemin_relatif)
        return False

    if contenu.count(ANCIEN_TWIG) > 1:
        print("[ECHEC] " + chemin_relatif + " : bloc de reference trouve plusieurs fois -> abandon par prudence.")
        return False

    contenu_corrige = contenu.replace(ANCIEN_TWIG, NOUVEAU_TWIG, 1)

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
    print("src/Controller/LivraisonController.php")
    print("-" * 70)
    resultats.append(corriger_php(racine))
    print()

    print("-" * 70)
    print("templates/commandes/show.html.twig")
    print("-" * 70)
    resultats.append(corriger_twig(racine))
    print()

    if resultats[0]:
        try:
            resultat = subprocess.run(
                ["php", "-l", os.path.join(racine, "src/Controller/LivraisonController.php")],
                capture_output=True, text=True, timeout=30
            )
            print("php -l LivraisonController.php : " + resultat.stdout.strip() + resultat.stderr.strip())
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
        print("Le bouton « Marquer comme livré » apparait maintenant sur")
        print("TOUTES les lignes non encore livrees (kakemono en")
        print("fabrication compris), pas seulement les ventes directes.")
        print("Il saute le controle prepresse et la production, et sort")
        print("quand meme le stock reserve s'il y en a un.")
    else:
        print("Un ou plusieurs fichiers n'ont pas pu etre modifies (voir [ECHEC] ci-dessus).")
        print("Recopiez-moi TOUT ce resume, je corrige avant de vous renvoyer le script.")


if __name__ == "__main__":
    main()
