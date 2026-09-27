<?php

namespace App\Controller;

use App\Entity\Commandes;
use App\Entity\CommandesDetails;
use App\Entity\Paiements;
use Doctrine\ORM\EntityManagerInterface;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

/**
 * Tableaux de bord chiffrés pour l'administrateur : qui vend, qui
 * encaisse, qui produit, sur une période donnée. Les accès sont
 * définis dans security.yaml (ROLE_STATS_GLOBAL, réservé à
 * ROLE_ADMIN via la hiérarchie des rôles).
 */
#[Route('/statistiques/globales', name: 'app_statistiques_globales_')]
final class StatistiquesController extends AbstractController
{
    #[Route('', name: 'index', methods: ['GET'])]
    public function globales(
        Request $request,
        EntityManagerInterface $entityManager
    ): Response {
        [$debut, $fin, $filtres] = $this->resoudrePeriode($request);

        return $this->render('statistiques/globales.html.twig', [
            'parAgent' => $this->ventesParAgent($entityManager, $debut, $fin),
            'parCaissiere' => $this->encaissementsParCaissiere($entityManager, $debut, $fin),
            'parProduction' => $this->productionParAgent($entityManager, $debut, $fin),
            'filtres' => $filtres,
        ]);
    }

    /**
     * @return array{0: \DateTimeImmutable, 1: \DateTimeImmutable, 2: array<string, string>}
     */
    private function resoudrePeriode(Request $request): array
    {
        $dateDebutBrute = trim((string) $request->query->get('date_debut', ''));
        $dateFinBrute = trim((string) $request->query->get('date_fin', ''));

        try {
            $debut = $dateDebutBrute !== ''
                ? new \DateTimeImmutable($dateDebutBrute . ' 00:00:00')
                : new \DateTimeImmutable('first day of this month 00:00:00');
        } catch (\Exception) {
            $debut = new \DateTimeImmutable('first day of this month 00:00:00');
        }

        try {
            $fin = $dateFinBrute !== ''
                ? new \DateTimeImmutable($dateFinBrute . ' 23:59:59')
                : new \DateTimeImmutable('last day of this month 23:59:59');
        } catch (\Exception) {
            $fin = new \DateTimeImmutable('last day of this month 23:59:59');
        }

        if ($fin < $debut) {
            $fin = $debut;
        }

        return [
            $debut,
            $fin,
            [
                'date_debut' => $debut->format('Y-m-d'),
                'date_fin' => $fin->format('Y-m-d'),
            ],
        ];
    }

    /**
     * Nombre de commandes et chiffre d'affaires par agent, sur la
     * période. Une commande entièrement annulée ne compte pas (même
     * règle que sur la liste des commandes et la fiche client).
     *
     * @return list<array{nom: string, nombre: int, montant: int}>
     */
    private function ventesParAgent(
        EntityManagerInterface $entityManager,
        \DateTimeImmutable $debut,
        \DateTimeImmutable $fin
    ): array {
        $commandes = $entityManager
            ->getRepository(Commandes::class)
            ->createQueryBuilder('c')
            ->leftJoin('c.agents', 'agent')
            ->addSelect('agent')
            ->leftJoin('c.commandesDetails', 'detail')
            ->addSelect('detail')
            ->andWhere('c.dateCommande BETWEEN :debut AND :fin')
            ->setParameter('debut', $debut)
            ->setParameter('fin', $fin)
            ->getQuery()
            ->getResult();

        $parAgent = [];

        foreach ($commandes as $commande) {
            if (!$commande instanceof Commandes) {
                continue;
            }

            if ($commande->getStatutTravaux() === 'annulee') {
                continue;
            }

            $agent = $commande->getAgents();
            $cle = $agent?->getId() ?? 0;

            $parAgent[$cle] ??= [
                'nom' => $agent?->getUsername() ?? 'Non attribué',
                'nombre' => 0,
                'montant' => 0,
            ];

            ++$parAgent[$cle]['nombre'];
            $parAgent[$cle]['montant'] += (int) $commande->getTotalTtc();
        }

        usort(
            $parAgent,
            static fn (array $a, array $b): int => $b['montant'] <=> $a['montant']
        );

        return array_values($parAgent);
    }

    /**
     * Montant encaissé par caissière, sur la période. Un paiement
     * annulé ne compte pas.
     *
     * @return list<array{nom: string, nombre: int, montant: int}>
     */
    private function encaissementsParCaissiere(
        EntityManagerInterface $entityManager,
        \DateTimeImmutable $debut,
        \DateTimeImmutable $fin
    ): array {
        $paiements = $entityManager
            ->getRepository(Paiements::class)
            ->createQueryBuilder('p')
            ->leftJoin('p.encaissePar', 'utilisateur')
            ->addSelect('utilisateur')
            ->andWhere('p.date BETWEEN :debut AND :fin')
            ->setParameter('debut', $debut)
            ->setParameter('fin', $fin)
            ->getQuery()
            ->getResult();

        $parCaissiere = [];

        foreach ($paiements as $paiement) {
            if (!$paiement instanceof Paiements) {
                continue;
            }

            if ($paiement->estAnnule()) {
                continue;
            }

            $utilisateur = $paiement->getEncaissePar();
            $cle = $utilisateur?->getId() ?? 0;

            $parCaissiere[$cle] ??= [
                'nom' => $utilisateur?->getUsername() ?? 'Non attribué',
                'nombre' => 0,
                'montant' => 0,
            ];

            ++$parCaissiere[$cle]['nombre'];
            $parCaissiere[$cle]['montant'] += (int) $paiement->getMontant();
        }

        usort(
            $parCaissiere,
            static fn (array $a, array $b): int => $b['montant'] <=> $a['montant']
        );

        return array_values($parCaissiere);
    }

    /**
     * Nombre de travaux dont la production a été terminée par
     * agent, sur la période (lignes annulées exclues).
     *
     * @return list<array{nom: string, nombre: int}>
     */
    private function productionParAgent(
        EntityManagerInterface $entityManager,
        \DateTimeImmutable $debut,
        \DateTimeImmutable $fin
    ): array {
        $details = $entityManager
            ->getRepository(CommandesDetails::class)
            ->createQueryBuilder('d')
            ->leftJoin('d.productionTermineePar', 'utilisateur')
            ->addSelect('utilisateur')
            ->andWhere('d.productionTermineeLe BETWEEN :debut AND :fin')
            ->andWhere('d.statutProduction != :annulee')
            ->setParameter('debut', $debut)
            ->setParameter('fin', $fin)
            ->setParameter('annulee', CommandesDetails::PRODUCTION_ANNULEE)
            ->getQuery()
            ->getResult();

        $parAgent = [];

        foreach ($details as $detail) {
            if (!$detail instanceof CommandesDetails) {
                continue;
            }

            $utilisateur = $detail->getProductionTermineePar();
            $cle = $utilisateur?->getId() ?? 0;

            $parAgent[$cle] ??= [
                'nom' => $utilisateur?->getUsername() ?? 'Non attribué',
                'nombre' => 0,
            ];

            ++$parAgent[$cle]['nombre'];
        }

        usort(
            $parAgent,
            static fn (array $a, array $b): int => $b['nombre'] <=> $a['nombre']
        );

        return array_values($parAgent);
    }
}
