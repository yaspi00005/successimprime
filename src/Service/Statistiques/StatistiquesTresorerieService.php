<?php

namespace App\Service\Statistiques;

use App\Entity\MouvementTresorerie;
use App\Entity\Paiements;
use Doctrine\ORM\EntityManagerInterface;

/**
 * Totaux encaisses/decaisses et repartition des charges par
 * categorie sur un intervalle donne. Utilise par la page
 * "Statistiques de tresorerie" et par l'onglet Accueil.
 */
final class StatistiquesTresorerieService
{
    public function __construct(
        private readonly EntityManagerInterface $entityManager
    ) {
    }

    public function totalEncaisse(\DateTimeImmutable $debut, \DateTimeImmutable $fin): int
    {
        $paiements = $this->entityManager
            ->getRepository(Paiements::class)
            ->createQueryBuilder('p')
            ->andWhere('p.date BETWEEN :debut AND :fin')
            ->setParameter('debut', $debut)
            ->setParameter('fin', $fin)
            ->getQuery()
            ->getResult();

        $total = 0;

        foreach ($paiements as $paiement) {
            if (!$paiement instanceof Paiements || $paiement->estAnnule()) {
                continue;
            }

            $total += (int) $paiement->getMontant();
        }

        return $total;
    }

    public function totalDecaisse(\DateTimeImmutable $debut, \DateTimeImmutable $fin): int
    {
        $total = 0;

        foreach ($this->decaissementsValides($debut, $fin) as $mouvement) {
            $total += (int) $mouvement->getMontant();
        }

        return $total;
    }

    /**
     * @return list<array{categorie: string, nombre: int, montant: int}>
     */
    public function chargesParCategorie(\DateTimeImmutable $debut, \DateTimeImmutable $fin): array
    {
        $parCategorie = [];

        foreach ($this->decaissementsValides($debut, $fin) as $mouvement) {
            $cle = $mouvement->getCategorie();

            $parCategorie[$cle] ??= [
                'categorie' => $mouvement->getCategorieLabel(),
                'nombre' => 0,
                'montant' => 0,
            ];

            ++$parCategorie[$cle]['nombre'];
            $parCategorie[$cle]['montant'] += (int) $mouvement->getMontant();
        }

        usort($parCategorie, static fn (array $a, array $b): int => $b['montant'] <=> $a['montant']);

        return array_values($parCategorie);
    }

    /**
     * @return list<MouvementTresorerie>
     */
    private function decaissementsValides(\DateTimeImmutable $debut, \DateTimeImmutable $fin): array
    {
        $resultats = $this->entityManager
            ->getRepository(MouvementTresorerie::class)
            ->createQueryBuilder('m')
            ->andWhere('m.dateOperation BETWEEN :debut AND :fin')
            ->andWhere('m.type = :type')
            ->setParameter('debut', $debut)
            ->setParameter('fin', $fin)
            ->setParameter('type', MouvementTresorerie::TYPE_DECAISSEMENT)
            ->getQuery()
            ->getResult();

        return array_values(array_filter(
            $resultats,
            static fn ($mouvement): bool =>
                $mouvement instanceof MouvementTresorerie && $mouvement->isValide()
        ));
    }
}
