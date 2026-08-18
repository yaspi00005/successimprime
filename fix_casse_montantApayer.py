"""
Corrige une erreur DQL : "La classe App\\Entity\\Commandes ne possède
aucun champ ni association nommé montantAPayer".

Le champ de l'entité s'appelle en réalité montantApayer (p
minuscule), pas montantAPayer. Le filtre par défaut de la liste des
commandes (livré dans fix_commandes_payees_liste.py) utilisait la
mauvaise casse — et le filtre "paiement" (impayée/partielle/payée)
un peu plus bas dans le même fichier avait exactement le même bug
latent, jamais déclenché jusqu'ici.

Modifie :
- src/Repository/CommandesRepository.php

A executer a la racine du dépôt : python3 fix_casse_montantApayer.py
"""

import sys

path = "src/Repository/CommandesRepository.php"


def appliquer(old, new, label):
    with open(path, encoding="utf-8") as f:
        content = f.read()

    if new in content:
        print(f"[SKIP] {label} : déjà présent")
        return

    count = content.count(old)
    if count != 1:
        print(f"[ERREUR] {label} : {count} occurrence(s) trouvée(s) (1 attendue)")
        sys.exit(1)

    content = content.replace(old, new)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[OK] {label}")


appliquer(
    """        if (!$rechercheActive && $affichage !== 'toutes') {
            $qb
                ->andWhere(
                    $qb->expr()->orX(
                        'COALESCE(c.montantAPayer, 0) < c.totalTtc',
                        'c.etat = :etatActif'
                    )
                )
                ->setParameter('etatActif', true);
        }""",
    """        if (!$rechercheActive && $affichage !== 'toutes') {
            $qb
                ->andWhere(
                    $qb->expr()->orX(
                        'COALESCE(c.montantApayer, 0) < c.totalTtc',
                        'c.etat = :etatActif'
                    )
                )
                ->setParameter('etatActif', true);
        }""",
    "Casse montantApayer (filtre par défaut de la liste)",
)

appliquer(
    """        match ($filtres['paiement'] ?? '') {
            'impayee' => $qb->andWhere(
                'COALESCE(c.montantAPayer, 0) = 0'
            ),

            'partielle' => $qb->andWhere(
                'COALESCE(c.montantAPayer, 0) > 0
                 AND COALESCE(c.montantAPayer, 0) < c.totalTtc'
            ),

            'payee' => $qb->andWhere(
                'COALESCE(c.montantAPayer, 0) >= c.totalTtc'
            ),

            default => null,
        };""",
    """        match ($filtres['paiement'] ?? '') {
            'impayee' => $qb->andWhere(
                'COALESCE(c.montantApayer, 0) = 0'
            ),

            'partielle' => $qb->andWhere(
                'COALESCE(c.montantApayer, 0) > 0
                 AND COALESCE(c.montantApayer, 0) < c.totalTtc'
            ),

            'payee' => $qb->andWhere(
                'COALESCE(c.montantApayer, 0) >= c.totalTtc'
            ),

            default => null,
        };""",
    "Casse montantApayer (filtre 'paiement')",
)

print("\nTerminé.")
