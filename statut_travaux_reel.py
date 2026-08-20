#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrige le badge "Travaux" de la liste des commandes, qui affichait
toujours "En production" quelle que soit la situation reelle.

Cause : le badge etait base sur Commandes::$etat, un champ booleen
jamais mis a jour apres la creation de la commande (comme l'etait
Commandes::$statut pour le paiement, deja corrige) -- il reste bloque
a true pour toujours.

Corrections :
1) Nouvelle methode Commandes::getStatutTravaux(), calculee a partir
   du statut de production reel de chaque ligne : "preparation" (pas
   encore pret a livrer), "livraison" (pret ou en cours de livraison),
   "livree" (tout livre), "annulee" ou "vide".
2) Liste des commandes : le badge utilise ce nouveau statut reel.
3) Meme cause plus profonde corrigee dans le filtre par defaut
   "Commandes actives" : il utilisait aussi ce $etat toujours vrai en
   "OU", ce qui faisait reapparaitre TOUTES les commandes (meme deja
   livrees et payees) dans la liste par defaut. Remplace par le
   meme calcul reel a partir des lignes.

Executer depuis la racine du projet :
    python3 statut_travaux_reel.py
"""

import sys


def appliquer(chemin, ancien, nouveau, label):
    try:
        with open(chemin, "r", encoding="utf-8") as f:
            contenu = f.read()
    except FileNotFoundError:
        print(f"[ERREUR] Fichier introuvable : {chemin}")
        return False

    if nouveau in contenu:
        print(f"[SKIP] {label} : deja applique.")
        return True

    occurrences = contenu.count(ancien)

    if occurrences != 1:
        print(
            f"[ERREUR] {label} : {occurrences} occurrence(s) trouvee(s) "
            f"dans {chemin} (1 attendue)"
        )
        return False

    contenu = contenu.replace(ancien, nouveau)

    with open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)

    print(f"[OK] {label}")
    return True


resultats = []

resultats.append(appliquer(
    "src/Entity/Commandes.php",
'    public function setEtat(bool $etat): static\n    {\n        $this->etat = $etat;\n\n        return $this;\n    }\n\n    /**\n     * @return Collection<int, CommandesDetails>\n     */\n    public function getCommandesDetails(): Collection',
'    public function setEtat(bool $etat): static\n    {\n        $this->etat = $etat;\n\n        return $this;\n    }\n\n    /**\n     * Résumé de l\'avancement des travaux, calculé à partir du\n     * statut réel de chaque ligne (contrairement à $etat, qui est\n     * un simple booléen jamais mis à jour après la création).\n     *\n     * Valeurs possibles :\n     * "vide", "preparation", "livraison", "livree", "annulee".\n     */\n    public function getStatutTravaux(): string\n    {\n        $lignesActives = $this->commandesDetails->filter(\n            static fn (CommandesDetails $ligne): bool =>\n                $ligne->getStatutProduction()\n                !== CommandesDetails::PRODUCTION_ANNULEE\n        );\n\n        if ($lignesActives->isEmpty()) {\n            return $this->commandesDetails->isEmpty()\n                ? \'vide\'\n                : \'annulee\';\n        }\n\n        $enPreparation = [\n            CommandesDetails::PRODUCTION_A_PRODUIRE,\n            CommandesDetails::PRODUCTION_EN_COURS,\n            CommandesDetails::PRODUCTION_TERMINEE,\n            CommandesDetails::PRODUCTION_NON_REQUISE,\n        ];\n\n        $enLivraison = [\n            CommandesDetails::PRODUCTION_PRETE_LIVRAISON,\n            CommandesDetails::PRODUCTION_EN_LIVRAISON,\n        ];\n\n        $toutesLivrees = true;\n\n        foreach ($lignesActives as $ligne) {\n            $statut = $ligne->getStatutProduction();\n\n            if (in_array($statut, $enPreparation, true)) {\n                return \'preparation\';\n            }\n\n            if (in_array($statut, $enLivraison, true)) {\n                $toutesLivrees = false;\n            }\n        }\n\n        return $toutesLivrees ? \'livree\' : \'livraison\';\n    }\n\n    /**\n     * @return Collection<int, CommandesDetails>\n     */\n    public function getCommandesDetails(): Collection',
    "1) Commandes : ajoute getStatutTravaux()",
))

resultats.append(appliquer(
    "templates/commandes/index.html.twig",
'\t\t\t\t\t\t\t\t\t\t{# 3. Travaux #}\n\t\t\t\t\t\t\t\t\t\t<td>\n\t\t\t\t\t\t\t\t\t\t\t{% if commande.etat %}\n\t\t\t\t\t\t\t\t\t\t\t\t<span class="badge badge-info">\n\t\t\t\t\t\t\t\t\t\t\t\t\tEn production\n\t\t\t\t\t\t\t\t\t\t\t\t</span>\n\t\t\t\t\t\t\t\t\t\t\t{% else %}\n\t\t\t\t\t\t\t\t\t\t\t\t<span class="badge badge-secondary">\n\t\t\t\t\t\t\t\t\t\t\t\t\tTerminée\n\t\t\t\t\t\t\t\t\t\t\t\t</span>\n\t\t\t\t\t\t\t\t\t\t\t{% endif %}',
'\t\t\t\t\t\t\t\t\t\t{# 3. Travaux #}\n\t\t\t\t\t\t\t\t\t\t<td>\n\t\t\t\t\t\t\t\t\t\t\t{% set statutTravaux = commande.statutTravaux %}\n\n\t\t\t\t\t\t\t\t\t\t\t{% if statutTravaux == \'livree\' %}\n\t\t\t\t\t\t\t\t\t\t\t\t<span class="badge badge-success">\n\t\t\t\t\t\t\t\t\t\t\t\t\tLivrée\n\t\t\t\t\t\t\t\t\t\t\t\t</span>\n\t\t\t\t\t\t\t\t\t\t\t{% elseif statutTravaux == \'livraison\' %}\n\t\t\t\t\t\t\t\t\t\t\t\t<span class="badge badge-warning">\n\t\t\t\t\t\t\t\t\t\t\t\t\tEn livraison\n\t\t\t\t\t\t\t\t\t\t\t\t</span>\n\t\t\t\t\t\t\t\t\t\t\t{% elseif statutTravaux == \'annulee\' %}\n\t\t\t\t\t\t\t\t\t\t\t\t<span class="badge badge-secondary">\n\t\t\t\t\t\t\t\t\t\t\t\t\tAnnulée\n\t\t\t\t\t\t\t\t\t\t\t\t</span>\n\t\t\t\t\t\t\t\t\t\t\t{% elseif statutTravaux == \'vide\' %}\n\t\t\t\t\t\t\t\t\t\t\t\t<span class="badge badge-light">\n\t\t\t\t\t\t\t\t\t\t\t\t\tAucun travail\n\t\t\t\t\t\t\t\t\t\t\t\t</span>\n\t\t\t\t\t\t\t\t\t\t\t{% else %}\n\t\t\t\t\t\t\t\t\t\t\t\t<span class="badge badge-info">\n\t\t\t\t\t\t\t\t\t\t\t\t\tEn préparation\n\t\t\t\t\t\t\t\t\t\t\t\t</span>\n\t\t\t\t\t\t\t\t\t\t\t{% endif %}',
    "2) index.html.twig : badge Travaux base sur le statut reel",
))

resultats.append(appliquer(
    "src/Repository/CommandesRepository.php",
'use App\\Entity\\Clients;\nuse App\\Entity\\Commandes;\nuse App\\Entity\\User;',
'use App\\Entity\\Clients;\nuse App\\Entity\\Commandes;\nuse App\\Entity\\CommandesDetails;\nuse App\\Entity\\User;',
    "3) CommandesRepository : import CommandesDetails",
))

resultats.append(appliquer(
    "src/Repository/CommandesRepository.php",
'        /*\n         * Affichage par défaut :\n         * paiement en attente OU travaux en cours.\n         *\n         * Le champ booléen c.statut n\'est jamais mis à jour après la\n         * création de la commande (aucun setStatut() n\'est appelé\n         * ailleurs dans le code) : il reste bloqué à true pour\n         * toujours, ce qui rendait ce filtre inopérant et laissait\n         * apparaître les commandes déjà payées. Le paiement réel est\n         * donc recalculé ici à partir de montantAPayer/totalTtc,\n         * comme pour le filtre "paiement" plus bas.\n         */\n        if (!$rechercheActive && $affichage !== \'toutes\') {\n            $qb\n                ->andWhere(\n                    $qb->expr()->orX(\n                        \'COALESCE(c.montantApayer, 0) < c.totalTtc\',\n                        \'c.etat = :etatActif\'\n                    )\n                )\n                ->setParameter(\'etatActif\', true);\n        }',
'        /*\n         * Affichage par défaut :\n         * paiement en attente OU travaux en cours.\n         *\n         * Les champs booléens c.statut et c.etat ne sont jamais mis à\n         * jour après la création de la commande (aucun setStatut()\n         * ni setEtat() n\'est appelé ailleurs dans le code) : ils\n         * restent bloqués à true pour toujours, ce qui rendait ce\n         * filtre inopérant et laissait apparaître indéfiniment les\n         * commandes déjà payées et déjà livrées. Le paiement réel est\n         * recalculé à partir de montantAPayer/totalTtc (comme pour le\n         * filtre "paiement" plus bas), et les travaux réels à partir\n         * du statut de production des lignes (comme pour\n         * Commandes::getStatutTravaux()).\n         */\n        if (!$rechercheActive && $affichage !== \'toutes\') {\n            $qb\n                ->andWhere(\n                    $qb->expr()->orX(\n                        \'COALESCE(c.montantApayer, 0) < c.totalTtc\',\n                        $qb->expr()->andX(\n                            \'d.statutProduction IS NOT NULL\',\n                            \'d.statutProduction NOT IN (:statutsTermines)\'\n                        )\n                    )\n                )\n                ->setParameter(\n                    \'statutsTermines\',\n                    [\n                        CommandesDetails::PRODUCTION_LIVREE,\n                        CommandesDetails::PRODUCTION_ANNULEE,\n                    ]\n                );\n        }',
    "4) CommandesRepository : filtre \"Commandes actives\" base sur le statut reel",
))


echecs = resultats.count(False)

print()
if echecs:
    print(f"Termine avec {echecs} erreur(s). Voir les [ERREUR] ci-dessus.")
    sys.exit(1)
else:
    print("Termine sans erreur.")
