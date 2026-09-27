<?php

namespace App\Controller;

use App\Entity\Clients;
use App\Entity\Commandes;
use App\Service\EvolutionTemporelleService;
use Doctrine\ORM\EntityManagerInterface;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

/**
 * Statistiques detaillees des clients : chiffre d'affaires genere
 * par client, et evolution du nombre de nouveaux clients enregistres
 * dans le temps.
 */
#[Route('/statistiques/clients', name: 'app_statistiques_clients_')]
final class StatistiquesClientsController extends AbstractController
{
    #[Route('', name: 'index', methods: ['GET'])]
    public function index(
        Request $request,
        EntityManagerInterface $entityManager,
        EvolutionTemporelleService $evolutionTemporelleService
    ): Response {
        $granularite = $evolutionTemporelleService->normaliserGranularite(
            $request->query->get('granularite')
        );

        [$debut, $fin, $filtres] = $this->resoudrePeriode($request);

        return $this->render('statistiques/clients.html.twig', [
            'caParClient' => $this->caParClient($entityManager, $debut, $fin),
            'filtres' => $filtres,
            'nouveauxClients' => $this->nouveauxClientsParPeriode($entityManager, $evolutionTemporelleService, $granularite),
            'granulariteEvolution' => $granularite,
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
                : new \DateTimeImmutable('first day of january this year 00:00:00');
        } catch (\Exception) {
            $debut = new \DateTimeImmutable('first day of january this year 00:00:00');
        }

        try {
            $fin = $dateFinBrute !== ''
                ? new \DateTimeImmutable($dateFinBrute . ' 23:59:59')
                : new \DateTimeImmutable('now');
        } catch (\Exception) {
            $fin = new \DateTimeImmutable('now');
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
     * Chiffre d'affaires par client sur la période (commandes
     * entièrement annulées exclues). Limité aux 30 meilleurs
     * clients pour rester lisible.
     *
     * @return list<array{nom: string, nombre: int, montant: int}>
     */
    private function caParClient(
        EntityManagerInterface $entityManager,
        \DateTimeImmutable $debut,
        \DateTimeImmutable $fin
    ): array {
        $commandes = $entityManager
            ->getRepository(Commandes::class)
            ->createQueryBuilder('c')
            ->leftJoin('c.clients', 'client')
            ->addSelect('client')
            ->andWhere('c.dateCommande BETWEEN :debut AND :fin')
            ->andWhere('c.deleted = false')
            ->setParameter('debut', $debut)
            ->setParameter('fin', $fin)
            ->getQuery()
            ->getResult();

        $parClient = [];

        foreach ($commandes as $commande) {
            if (!$commande instanceof Commandes) {
                continue;
            }

            if ($commande->getStatutTravaux() === 'annulee') {
                continue;
            }

            $client = $commande->getClients();
            $cle = $client?->getId() ?? 0;

            $parClient[$cle] ??= [
                'nom' => $client?->getNomComplet() ?? 'Client supprimé',
                'nombre' => 0,
                'montant' => 0,
            ];

            ++$parClient[$cle]['nombre'];
            $parClient[$cle]['montant'] += (int) $commande->getTotalTtc();
        }

        usort(
            $parClient,
            static fn (array $a, array $b): int => $b['montant'] <=> $a['montant']
        );

        return array_slice(array_values($parClient), 0, 30);
    }

    /**
     * @return array{labels: list<string>, valeurs: list<int>}
     */
    private function nouveauxClientsParPeriode(
        EntityManagerInterface $entityManager,
        EvolutionTemporelleService $evolutionTemporelleService,
        string $granularite
    ): array {
        [$cles, $labels, $debutFenetre] = $evolutionTemporelleService->genererPaniers($granularite);

        $compteurs = array_fill_keys($cles, 0);

        $clients = $entityManager
            ->getRepository(Clients::class)
            ->createQueryBuilder('c')
            ->andWhere('c.createdAt >= :debut')
            ->setParameter('debut', $debutFenetre)
            ->getQuery()
            ->getResult();

        foreach ($clients as $client) {
            if (!$client instanceof Clients || $client->getCreatedAt() === null) {
                continue;
            }

            $cle = $evolutionTemporelleService->clePourDate($client->getCreatedAt(), $granularite);

            if (!isset($compteurs[$cle])) {
                continue;
            }

            ++$compteurs[$cle];
        }

        return [
            'labels' => $labels,
            'valeurs' => array_values($compteurs),
        ];
    }
}
