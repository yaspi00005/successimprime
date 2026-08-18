"""
Corrige l'affichage par defaut de la liste des commandes : les
commandes deja payees n'y apparaissent plus (elles restent
consultables via la recherche/les filtres, ou l'affichage "Toutes").

Cause : le champ booleen Commandes::$statut ("paiement en attente")
n'est jamais mis a jour apres la creation de la commande (aucun
setStatut() bool n'est appele nulle part dans le code) : il reste
bloque a true pour toujours. Le filtre par defaut
"c.statut = true OU c.etat = true" etait donc toujours vrai, quel
que soit le paiement reel, et affichait toutes les commandes.

Corrige en recalculant le paiement reel a partir de
montantAPayer/totalTtc (comme le fait deja le filtre "paiement" plus
bas dans le meme fichier), au lieu de se fier au champ mort.

Modifie :
- src/Repository/CommandesRepository.php

A executer a la racine du dépôt : python3 fix_commandes_payees_liste.py
"""

import sys

path = "src/Repository/CommandesRepository.php"

old = """        /*
         * Affichage par défaut :
         * paiement en attente OU travaux en cours.
         */
        if (!$rechercheActive && $affichage !== 'toutes') {
            $qb
                ->andWhere(
                    $qb->expr()->orX(
                        'c.statut = :statutActif',
                        'c.etat = :etatActif'
                    )
                )
                ->setParameter('statutActif', true)
                ->setParameter('etatActif', true);
        }"""

new = """        /*
         * Affichage par défaut :
         * paiement en attente OU travaux en cours.
         *
         * Le champ booléen c.statut n'est jamais mis à jour après la
         * création de la commande (aucun setStatut() n'est appelé
         * ailleurs dans le code) : il reste bloqué à true pour
         * toujours, ce qui rendait ce filtre inopérant et laissait
         * apparaître les commandes déjà payées. Le paiement réel est
         * donc recalculé ici à partir de montantAPayer/totalTtc,
         * comme pour le filtre "paiement" plus bas.
         */
        if (!$rechercheActive && $affichage !== 'toutes') {
            $qb
                ->andWhere(
                    $qb->expr()->orX(
                        'COALESCE(c.montantAPayer, 0) < c.totalTtc',
                        'c.etat = :etatActif'
                    )
                )
                ->setParameter('etatActif', true);
        }"""

with open(path, encoding="utf-8") as f:
    content = f.read()

if new in content:
    print("Déjà présent - rien à faire.")
else:
    count = content.count(old)
    if count != 1:
        print(f"[ERREUR] {count} occurrence(s) trouvée(s) (1 attendue)")
        sys.exit(1)

    content = content.replace(old, new)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    print("OK - les commandes payées ne s'affichent plus par défaut dans la liste.")
