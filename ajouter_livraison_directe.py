#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ajoute la possibilite de marquer directement une ligne de vente
directe (article en stock, ex. kakemono deja imprime -- pas de
fabrication) comme livree, en un clic.

PROBLEME CORRIGE :

  - Ces lignes restaient bloquees "En preparation" pour toujours,
    meme quand elles avaient ete livrees en realite (remises au
    client sans jamais etre marquees dans le logiciel) ;

  - Le stock reserve au moment de la commande restait "reserve"
    indefiniment, jamais consomme, car aucune action de l'interface
    ne permettait de faire avancer ces lignes.

Cause technique : le mecanisme existait deja dans le code
(marquerPreteLivraison / marquerEnLivraison / marquerLivree +
consommation du stock reserve), mais aucun bouton nulle part ne
l'utilisait pour ce cas de figure. De plus, la premiere etape du
mecanisme existant (preparerDirectement) etait elle-meme cassee :
elle ne savait pas basculer une ligne fraichement creee (statut par
defaut "a_produire") vers l'etat "non_requise" avant de continuer.

Ce script :
  1. corrige preparerDirectement() dans LivraisonController.php ;
  2. ajoute une nouvelle action livrerDirectement() qui enchaine tout
     le circuit en un seul clic (preparation, mise en livraison,
     sortie de stock, livraison) ;
  3. ajoute le bouton correspondant dans commandes/show.html.twig,
     visible uniquement sur les lignes de vente directe non encore
     livrees.

Usage:
    python3 ajouter_livraison_directe.py /chemin/vers/successImprim
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
# FICHIER 1 : src/Controller/LivraisonController.php
# ============================================================

ANCIEN_PREPARER = """        try {
            if ($detail->isProductionNecessaire()) {
                throw new \\LogicException(
                    'Cette ligne nécessite une production et ne peut pas être envoyée directement en livraison.'
                );
            }

            $detail->marquerPreteLivraison();

            $em->flush();

            $this->addFlash(
                'success',
                sprintf(
                    '« %s » est prêt pour la livraison.',
                    $detail->getDesignation()
                )
            );
        } catch (\\LogicException $e) {
            $this->addFlash(
                'error',
                $e->getMessage()
            );
        }

        return $this->redirectToRoute(
            'app_livraisons_index'
        );
    }"""

NOUVEAU_PREPARER = """        try {
            if ($detail->isProductionNecessaire()) {
                throw new \\LogicException(
                    'Cette ligne nécessite une production et ne peut pas être envoyée directement en livraison.'
                );
            }

            /*
             * Une ligne fraîchement créée (vente directe ou saisie
             * libre) reste au statut par défaut "a_produire" tant
             * que personne ne l'a explicitement basculée : on le
             * fait ici avant de la préparer pour la livraison.
             */
            if (
                $detail->getStatutProduction()
                === CommandesDetails::PRODUCTION_A_PRODUIRE
            ) {
                $detail->marquerProductionNonRequise();
            }

            $detail->marquerPreteLivraison();

            $em->flush();

            $this->addFlash(
                'success',
                sprintf(
                    '« %s » est prêt pour la livraison.',
                    $detail->getDesignation()
                )
            );
        } catch (\\LogicException $e) {
            $this->addFlash(
                'error',
                $e->getMessage()
            );
        }

        return $this->redirectToRoute(
            'app_livraisons_index'
        );
    }

    /*
     * ============================================================
     * LIVRAISON DIRECTE EN UN CLIC
     * ============================================================
     *
     * Pour une ligne de vente directe (article en stock ou saisie
     * libre, sans fabrication), enchaîne en une seule action tout
     * le circuit (préparation, mise en livraison, sortie de stock
     * et livraison), pour éviter de faire naviguer l'utilisateur
     * entre plusieurs écrans pour un cas aussi simple.
     * ============================================================
     */
    #[Route(
        '/{id}/livrer-directement',
        name: 'livrer_directement',
        requirements: [
            'id' => '\\d+',
        ],
        methods: ['POST']
    )]
    public function livrerDirectement(
        CommandesDetails $detail,
        Request $request,
        EntityManagerInterface $em,
        StockService $stockService
    ): Response {
        $this->verifierJeton(
            $request,
            'livraison_direct_' . $detail->getId()
        );

        try {
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

            $detail->marquerLivree();

            $em->flush();

            $this->addFlash(
                'success',
                sprintf(
                    '« %s » a été marqué comme livré.',
                    $detail->getDesignation()
                )
            );
        } catch (\\LogicException $e) {
            $this->addFlash(
                'error',
                $e->getMessage()
            );
        }

        return $this->redirectToRoute(
            'app_commandes_show',
            [
                'id' => $detail->getCommande()?->getId(),
            ]
        );
    }"""

MARQUEUR_PHP = "livrer_directement"


# ============================================================
# FICHIER 2 : templates/commandes/show.html.twig
# ============================================================

ANCIEN_TWIG = (
    ("\t" * 13) + "FCFA\n"
    "\n"
    + ("\t" * 12) + "</strong>\n"
    "\n"
    + ("\t" * 11) + "</div>\n"
    "\n"
    + ("\t" * 10) + "</div>\n"
    "\n"
    + ("\t" * 9) + "</div>\n"
    "\n"
    + ("\t" * 8) + "</div>\n"
    "\n"
    + ("\t" * 7) + "{% endfor %}"
)

BLOC_BOUTON = (
    ("\t" * 10) + "<div class=\"row mt-3\">\n"
    "\n"
    + ("\t" * 11) + "<div class=\"col-12\">\n"
    "\n"
    + ("\t" * 12) + "{% if (is_granted('ROLE_LIVRAISON') or estAdmin) "
    "and detail.estLivraisonDirecte "
    "and detail.statutProduction != 'livree' %}\n"
    "\n"
    + ("\t" * 13) + "<form method=\"post\" action=\"{{ path( 'app_livraisons_livrer_directement', { id: detail.id } ) }}\" class=\"js-confirm-form\" data-message=\"Marquer « {{ detail.designation|default('ce travail') }} » comme livré ? Le stock réservé sera définitivement sorti.\">\n"
    "\n"
    + ("\t" * 14) + "<input type=\"hidden\" name=\"_token\" value=\"{{ csrf_token( 'livraison_direct_' ~ detail.id ) }}\">\n"
    "\n"
    + ("\t" * 14) + "<button type=\"submit\" class=\"btn btn-sm btn-success\">\n"
    + ("\t" * 15) + "<i class=\"fe fe-truck mr-1\"></i>\n"
    + ("\t" * 15) + "Marquer comme livré\n"
    + ("\t" * 14) + "</button>\n"
    "\n"
    + ("\t" * 13) + "</form>\n"
    "\n"
    + ("\t" * 12) + "{% endif %}\n"
    "\n"
    + ("\t" * 11) + "</div>\n"
    "\n"
    + ("\t" * 10) + "</div>\n"
    "\n"
)

NOUVEAU_TWIG = (
    ("\t" * 13) + "FCFA\n"
    "\n"
    + ("\t" * 12) + "</strong>\n"
    "\n"
    + ("\t" * 11) + "</div>\n"
    "\n"
    + ("\t" * 10) + "</div>\n"
    "\n"
    + BLOC_BOUTON
    + ("\t" * 9) + "</div>\n"
    "\n"
    + ("\t" * 8) + "</div>\n"
    "\n"
    + ("\t" * 7) + "{% endfor %}"
)

MARQUEUR_TWIG = "app_livraisons_livrer_directement"


def corriger_fichier(racine, chemin_relatif, marqueur, ancien, nouveau, diagnostic):
    chemin_absolu = os.path.join(racine, chemin_relatif)

    if not os.path.isfile(chemin_absolu):
        print("[ABSENT] " + chemin_relatif + " n'existe pas du tout sur le disque.")
        return False

    with open(chemin_absolu, "r", encoding="utf-8") as f:
        contenu = f.read()

    if marqueur in contenu:
        print("[SKIP] " + chemin_relatif + " contient deja '" + marqueur + "' (deja applique).")
        return True

    if ancien not in contenu:
        print("[ECHEC] " + chemin_relatif + " : bloc de reference introuvable -> abandon (rien ecrit).")
        print("  Copiez-moi le resultat de :")
        print("    " + diagnostic)
        return False

    occurrences = contenu.count(ancien)

    if occurrences > 1:
        print("[ECHEC] " + chemin_relatif + " : bloc de reference trouve " + str(occurrences) + " fois (attendu 1) -> abandon par prudence (rien ecrit).")
        print("  Copiez-moi le resultat de :")
        print("    " + diagnostic)
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
    resultats.append(
        corriger_fichier(
            racine,
            "src/Controller/LivraisonController.php",
            MARQUEUR_PHP,
            ANCIEN_PREPARER,
            NOUVEAU_PREPARER,
            "grep -n -A25 \"function preparerDirectement\" src/Controller/LivraisonController.php",
        )
    )
    print()

    print("-" * 70)
    print("templates/commandes/show.html.twig")
    print("-" * 70)
    resultats.append(
        corriger_fichier(
            racine,
            "templates/commandes/show.html.twig",
            MARQUEUR_TWIG,
            ANCIEN_TWIG,
            NOUVEAU_TWIG,
            "sed -n '1095,1145p' templates/commandes/show.html.twig | cat -et",
        )
    )
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
        print("Sur la fiche d'une commande, les lignes de vente directe")
        print("(articles en stock, sans fabrication -- ex. kakemono) qui")
        print("ne sont pas encore livrees affichent maintenant un bouton")
        print("« Marquer comme livre ». Cliquer dessus fait avancer la")
        print("commande hors de « En preparation » ET sort le stock")
        print("reserve (il n'apparaitra plus comme « reserve »).")
    else:
        print("Un ou plusieurs fichiers n'ont pas pu etre modifies (voir [ECHEC] ci-dessus).")
        print("Recopiez-moi TOUT ce resume, je corrige avant de vous renvoyer le script.")


if __name__ == "__main__":
    main()
