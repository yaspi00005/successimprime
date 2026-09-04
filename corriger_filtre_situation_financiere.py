#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrige le filtre "Situation financière" (impayee/partielle/payee)
sur la liste des commandes.

Cause du bug (trop peu de resultats, ou des resultats incorrects) :
le filtre comparait c.montantApayer, un champ fige copie une seule
fois depuis le devis d'origine et JAMAIS mis a jour ensuite (aucun
appel a setMontantApayer() apres la creation de la commande). Le
vrai champ tenu a jour a chaque paiement valide est c.statutPaiement
(impayee / partielle / payee) -- c'est lui qu'il faut utiliser.

Fichier concerne :
  - src/Repository/CommandesRepository.php

Usage:
    python3 corriger_filtre_situation_financiere.py /chemin/vers/successImprim
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
            print("[SKIP] " + description + " (deja applique)")
            return True

        print("[ECHEC] " + description + " -> bloc de reference introuvable.")
        return False

    if contenu.count(ancien) > 1:
        print("[ECHEC] " + description + " -> bloc trouve plusieurs fois, abandon.")
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

    print("[OK VERIFIE] " + description)
    return True


ANCIEN1 = '        /*\n         * Affichage par défaut :\n         * paiement en attente OU travaux en cours.\n         *\n         * Les champs booléens c.statut et c.etat ne sont jamais mis à\n         * jour après la création de la commande (aucun setStatut()\n         * ni setEtat() n\'est appelé ailleurs dans le code) : ils\n         * restent bloqués à true pour toujours, ce qui rendait ce\n         * filtre inopérant et laissait apparaître indéfiniment les\n         * commandes déjà payées et déjà livrées. Le paiement réel est\n         * recalculé à partir de montantAPayer/totalTtc (comme pour le\n         * filtre "paiement" plus bas), et les travaux réels à partir\n         * du statut de production des lignes (comme pour\n         * Commandes::getStatutTravaux()).\n         */\n        if (!$rechercheActive && $affichage !== \'toutes\') {\n            $qb\n                ->andWhere(\n                    $qb->expr()->orX(\n                        \'COALESCE(c.montantApayer, 0) < c.totalTtc\',\n                        $qb->expr()->andX(\n                            \'d.statutProduction IS NOT NULL\',\n                            \'d.statutProduction NOT IN (:statutsTermines)\'\n                        )\n                    )\n                )\n                ->setParameter(\n                    \'statutsTermines\',\n                    [\n                        CommandesDetails::PRODUCTION_LIVREE,\n                        CommandesDetails::PRODUCTION_ANNULEE,\n                    ]\n                );\n        }'
NOUVEAU1 = "        /*\n         * Affichage par défaut :\n         * paiement en attente OU travaux en cours.\n         *\n         * Les champs booléens c.statut et c.etat ne sont jamais mis à\n         * jour après la création de la commande (aucun setStatut()\n         * ni setEtat() n'est appelé ailleurs dans le code) : ils\n         * restent bloqués à true pour toujours, ce qui rendait ce\n         * filtre inopérant et laissait apparaître indéfiniment les\n         * commandes déjà payées et déjà livrées. Le paiement réel est\n         * lu depuis c.statutPaiement (mis à jour à chaque validation\n         * de paiement, voir CommandesController), et les travaux\n         * réels à partir du statut de production des lignes (comme\n         * pour Commandes::getStatutTravaux()).\n         */\n        if (!$rechercheActive && $affichage !== 'toutes') {\n            $qb\n                ->andWhere(\n                    $qb->expr()->orX(\n                        'c.statutPaiement != :statutPayeDefaut',\n                        $qb->expr()->andX(\n                            'd.statutProduction IS NOT NULL',\n                            'd.statutProduction NOT IN (:statutsTermines)'\n                        )\n                    )\n                )\n                ->setParameter('statutPayeDefaut', Commandes::PAIEMENT_PAYE)\n                ->setParameter(\n                    'statutsTermines',\n                    [\n                        CommandesDetails::PRODUCTION_LIVREE,\n                        CommandesDetails::PRODUCTION_ANNULEE,\n                    ]\n                );\n        }"

ANCIEN2 = "        /*\n         * Filtre par situation réelle du paiement.\n         */\n        match ($filtres['paiement'] ?? '') {\n            'impayee' => $qb->andWhere(\n                'COALESCE(c.montantApayer, 0) = 0'\n            ),\n\n            'partielle' => $qb->andWhere(\n                'COALESCE(c.montantApayer, 0) > 0\n                 AND COALESCE(c.montantApayer, 0) < c.totalTtc'\n            ),\n\n            'payee' => $qb->andWhere(\n                'COALESCE(c.montantApayer, 0) >= c.totalTtc'\n            ),\n\n            default => null,\n        };"
NOUVEAU2 = "        /*\n         * Filtre par situation réelle du paiement, lue directement\n         * depuis c.statutPaiement (impayee/partielle/payee), mise à\n         * jour à chaque validation de paiement. Le champ\n         * c.montantApayer utilisé auparavant ici n'est qu'une copie\n         * figée du devis d'origine, jamais mise à jour ensuite : le\n         * filtre ne retournait donc presque aucun résultat correct.\n         */\n        if (\n            in_array(\n                $filtres['paiement'] ?? '',\n                [\n                    Commandes::PAIEMENT_IMPAYE,\n                    Commandes::PAIEMENT_PARTIEL,\n                    Commandes::PAIEMENT_PAYE,\n                ],\n                true\n            )\n        ) {\n            $qb\n                ->andWhere('c.statutPaiement = :statutPaiementFiltre')\n                ->setParameter(\n                    'statutPaiementFiltre',\n                    $filtres['paiement']\n                );\n        }"


def main():
    racine = sys.argv[1] if len(sys.argv) >= 2 else "."
    verifier_racine(racine)

    chemin_relatif = "src/Repository/CommandesRepository.php"

    print("-" * 70)
    print(chemin_relatif)
    print("-" * 70)

    resultats = []
    resultats.append(corriger(
        chemin_relatif, racine, ANCIEN1, NOUVEAU1,
        "affichage par defaut base sur statutPaiement"
    ))
    resultats.append(corriger(
        chemin_relatif, racine, ANCIEN2, NOUVEAU2,
        "filtre Situation financiere base sur statutPaiement"
    ))
    print()

    chemin_absolu = os.path.join(racine, chemin_relatif)
    try:
        resultat = subprocess.run(
            ["php", "-l", chemin_absolu],
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
        print("Tout est en place. Le filtre 'Situation financiere' (Non payee /")
        print("Paiement partiel / Entierement payee) doit maintenant retourner")
        print("les bonnes commandes.")
    else:
        print("Un ou plusieurs blocs n'ont pas pu etre modifies (voir [ECHEC] ci-dessus).")
        print("Recopiez-moi TOUT ce resume, je corrige avant de vous renvoyer le script.")


if __name__ == "__main__":
    main()