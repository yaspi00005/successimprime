<?php

namespace App\Repository;

use App\Entity\Clients;
use App\Entity\Commandes;
use App\Entity\User;
use Doctrine\Bundle\DoctrineBundle\Repository\ServiceEntityRepository;
use Doctrine\Persistence\ManagerRegistry;

final class CommandesRepository extends ServiceEntityRepository
{
    public function __construct(ManagerRegistry $registry)
    {
        parent::__construct($registry, Commandes::class);
    }

    /**
     * Sans recherche :
     * - statut = true : paiement en attente ;
     * - ou etat = true : travaux en cours.
     *
     * Avec une recherche active, toutes les commandes peuvent être retrouvées.
     */
    public function rechercherPourIndex(array $filtres): array
    {
        $qb = $this->createQueryBuilder('c')
            ->leftJoin('c.clients', 'cl')
            ->addSelect('cl')
            ->leftJoin('c.commandesDetails', 'd')
            ->addSelect('d')
            ->distinct();

        $rechercheActive = $this->rechercheEstActive($filtres);
        $affichage = $filtres['affichage'] ?? 'actives';

        /*
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
                        'COALESCE(c.montantApayer, 0) < c.totalTtc',
                        'c.etat = :etatActif'
                    )
                )
                ->setParameter('etatActif', true);
        }

        /*
         * Recherche par numéro de commande,
         * nom du client ou téléphone.
         */
        $q = trim((string) ($filtres['q'] ?? ''));

        if ($q !== '') {
            $recherche = $qb->expr()->orX(
                'LOWER(cl.nom) LIKE LOWER(:q)',
                'cl.telephone LIKE :q'
            );

            if (ctype_digit($q)) {
                $recherche->add('c.id = :commandeId');
                $qb->setParameter('commandeId', (int) $q);
            }

            $qb
                ->andWhere($recherche)
                ->setParameter('q', '%' . $q . '%');
        }

        /*
         * Filtre par client.
         */
        if (!empty($filtres['client'])) {
            $qb
                ->andWhere('cl.id = :client')
                ->setParameter('client', (int) $filtres['client']);
        }

        /*
         * Filtre par statut de paiement.
         *
         * 1 = paiement en attente
         * 0 = paiement terminé
         */
        if (($filtres['statut'] ?? '') !== '') {
            $qb
                ->andWhere('c.statut = :statut')
                ->setParameter(
                    'statut',
                    (string) $filtres['statut'] === '1'
                );
        }

        /*
         * Filtre par état des travaux.
         *
         * 1 = travaux en cours
         * 0 = travaux terminés
         */
        if (($filtres['etat'] ?? '') !== '') {
            $qb
                ->andWhere('c.etat = :etat')
                ->setParameter(
                    'etat',
                    (string) $filtres['etat'] === '1'
                );
        }

        /*
         * Filtre par situation réelle du paiement.
         */
        match ($filtres['paiement'] ?? '') {
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
        };

        /*
         * Période.
         *
         * Remplace createdAt si ta propriété de date
         * possède un autre nom dans Commandes.
         */
        if (!empty($filtres['date_debut'])) {
            try {
                $dateDebut = new \DateTimeImmutable(
                    $filtres['date_debut'] . ' 00:00:00'
                );

                $qb
                    ->andWhere('c.createdAt >= :dateDebut')
                    ->setParameter('dateDebut', $dateDebut);
            } catch (\Exception) {
                // La date invalide est ignorée.
            }
        }

        if (!empty($filtres['date_fin'])) {
            try {
                $dateFin = new \DateTimeImmutable(
                    $filtres['date_fin'] . ' 23:59:59'
                );

                $qb
                    ->andWhere('c.createdAt <= :dateFin')
                    ->setParameter('dateFin', $dateFin);
            } catch (\Exception) {
                // La date invalide est ignorée.
            }
        }

        /*
         * Montants.
         */
        if (
            isset($filtres['montant_min'])
            && $filtres['montant_min'] !== ''
        ) {
            $qb
                ->andWhere('c.totalTtc >= :montantMin')
                ->setParameter(
                    'montantMin',
                    (int) $filtres['montant_min']
                );
        }

        if (
            isset($filtres['montant_max'])
            && $filtres['montant_max'] !== ''
        ) {
            $qb
                ->andWhere('c.totalTtc <= :montantMax')
                ->setParameter(
                    'montantMax',
                    (int) $filtres['montant_max']
                );
        }

        /*
         * Tri des résultats.
         */
        match ($filtres['tri'] ?? 'recent') {
            'ancien' => $qb->orderBy('c.id', 'ASC'),

            'montant_desc' => $qb
                ->orderBy('c.totalTtc', 'DESC'),

            'reste_desc' => $qb
                ->addSelect(
                    '(c.totalTtc - COALESCE(c.montantAPayer, 0))
                     AS HIDDEN resteAPayer'
                )
                ->orderBy('resteAPayer', 'DESC'),

            default => $qb->orderBy('c.id', 'DESC'),
        };

        return $qb->getQuery()->getResult();
    }

    /**
     * Commandes traitées et chiffre d'affaires généré, groupés par agent.
     *
     * Doctrine n'autorise pas de mélanger une entité complète et des
     * fonctions d'agrégation (COUNT/SUM) dans un même SELECT sans
     * sélectionner aussi l'alias racine : on sélectionne donc les
     * champs de l'agent un par un plutôt que l'entité User entière.
     *
     * @return array<int, array{
     *     agentId: int,
     *     agentUsername: string,
     *     agentNom: ?string,
     *     agentPrenom: ?string,
     *     agentPhotos: ?string,
     *     nbCommandes: int,
     *     caGenere: int
     * }>
     */
    public function statistiquesParAgent(
        ?\DateTimeInterface $debut = null,
        ?\DateTimeInterface $fin = null
    ): array {
        $qb = $this->createQueryBuilder('c')
            ->select('a.id AS agentId')
            ->addSelect('a.username AS agentUsername')
            ->addSelect('e.nom AS agentNom')
            ->addSelect('e.prenom AS agentPrenom')
            ->addSelect('e.photos AS agentPhotos')
            ->addSelect('COUNT(c.id) AS nbCommandes')
            ->addSelect('COALESCE(SUM(c.totalTtc), 0) AS caGenere')
            ->join('c.agents', 'a')
            ->leftJoin('a.employe', 'e')
            ->andWhere('c.deleted = false')
            ->groupBy('a.id')
            ->addGroupBy('e.id')
            ->orderBy('caGenere', 'DESC');

        if ($debut) {
            $qb
                ->andWhere('c.dateCommande >= :debut')
                ->setParameter('debut', $debut);
        }

        if ($fin) {
            $qb
                ->andWhere('c.dateCommande <= :fin')
                ->setParameter('fin', $fin);
        }

        $resultats = $qb->getQuery()->getResult();

        foreach ($resultats as &$ligne) {
            $ligne['agentId'] = (int) $ligne['agentId'];
            $ligne['nbCommandes'] = (int) $ligne['nbCommandes'];
            $ligne['caGenere'] = (int) $ligne['caGenere'];
        }

        return $resultats;
    }

    /**
     * Nombre de commandes (non supprimées) sur une période.
     */
    public function compterCommandes(
        ?\DateTimeInterface $debut = null,
        ?\DateTimeInterface $fin = null
    ): int {
        $qb = $this->createQueryBuilder('c')
            ->select('COUNT(c.id)')
            ->andWhere('c.deleted = false');

        if ($debut) {
            $qb
                ->andWhere('c.dateCommande >= :debut')
                ->setParameter('debut', $debut);
        }

        if ($fin) {
            $qb
                ->andWhere('c.dateCommande <= :fin')
                ->setParameter('fin', $fin);
        }

        return (int) $qb->getQuery()->getSingleScalarResult();
    }

    /**
     * Détecte un doublon probable : même agent, même client,
     * même montant TTC, enregistré il y a moins de $secondes.
     *
     * Sert de filet de sécurité côté serveur contre un double
     * clic ou une double soumission du formulaire.
     */
    public function trouverDoublonRecent(
        User $agent,
        Clients $client,
        int $totalTtc,
        \DateTimeInterface $depuis
    ): ?Commandes {
        return $this->createQueryBuilder('c')
            ->andWhere('c.deleted = false')
            ->andWhere('c.agents = :agent')
            ->andWhere('c.clients = :client')
            ->andWhere('c.totalTtc = :totalTtc')
            ->andWhere('c.dateCommande >= :depuis')
            ->setParameter('agent', $agent)
            ->setParameter('client', $client)
            ->setParameter('totalTtc', $totalTtc)
            ->setParameter('depuis', $depuis)
            ->orderBy('c.dateCommande', 'DESC')
            ->setMaxResults(1)
            ->getQuery()
            ->getOneOrNullResult();
    }

    private function rechercheEstActive(array $filtres): bool
    {
        $champsRecherche = [
            'q',
            'client',
            'statut',
            'etat',
            'paiement',
            'date_debut',
            'date_fin',
            'montant_min',
            'montant_max',
        ];

        foreach ($champsRecherche as $nom) {
            $valeur = $filtres[$nom] ?? null;

            /*
             * Attention : la chaîne "0" est une valeur valide
             * pour statut et etat.
             */
            if ($valeur !== null && $valeur !== '') {
                return true;
            }
        }

        return false;
    }
}