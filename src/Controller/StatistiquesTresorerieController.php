<?php

namespace App\Controller;

use App\Entity\MouvementTresorerie;
use App\Entity\Paiements;
use App\Service\EvolutionFinanciereService;
use App\Service\EvolutionTemporelleService;
use Doctrine\ORM\EntityManagerInterface;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

/**
 * Statistiques detaillees de tresorerie : evolution des
 * encaissements/decaissements dans le temps, et repartition des
 * charges par categorie sur un intervalle de dates libre.
 */
#[Route('/statistiques/tresorerie', name: 'app_statistiques_tresorerie_')]
final class StatistiquesTresorerieController extends AbstractController
{
    #[Route('', name: 'index', methods: ['GET'])]
    public function index(
        Request $request,
        EntityManagerInterface $entityManager,
        EvolutionTemporelleService $evolutionTemporelleService,
        EvolutionFinanciereService $evolutionFinanciereService
    ): Response {
        $granularite = $evolutionTemporelleService->normaliserGranularite(
            $request->query->get('granularite')
        );

        [$debut, $fin, $filtres] = $this->resoudreIntervalle($request);

        return $this->render('statistiques/tresorerie.html.twig', [
            'evolution' => $evolutionFinanciereService->calculer($granularite),
            'granulariteEvolution' => $granularite,
            'filtres' => $filtres,
            'totalEncaisse' => $this->totalEncaisseSurIntervalle($entityManager, $debut, $fin),
            'totalDecaisse' => $this->totalDecaisseSurIntervalle($entityManager, $debut, $fin),
            'chargesParCategorie' => $this->chargesParCategorie($entityManager, $debut, $fin),
        ]);
    }

    /**
     * @return array{0: \DateTimeImmutable, 1: \DateTimeImmutable, 2: array<string, string>}
     */
    private function resoudreIntervalle(Request $request): array
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

    private function totalEncaisseSurIntervalle(
        EntityManagerInterface $entityManager,
        \DateTimeImmutable $debut,
        \DateTimeImmutable $fin
    ): int {
        $paiements = $entityManager
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

    private function totalDecaisseSurIntervalle(
        EntityManagerInterface $entityManager,
        \DateTimeImmutable $debut,
        \DateTimeImmutable $fin
    ): int {
        $mouvements = $this->decaissementsValides($entityManager, $debut, $fin);

        $total = 0;

        foreach ($mouvements as $mouvement) {
            $total += (int) $mouvement->getMontant();
        }

        return $total;
    }

    /**
     * Répartition des décaissements par catégorie (essence, achats,
     * transport, entretien, électricité, loyer, autre charge...) sur
     * l'intervalle choisi.
     *
     * @return list<array{categorie: string, nombre: int, montant: int}>
     */
    private function chargesParCategorie(
        EntityManagerInterface $entityManager,
        \DateTimeImmutable $debut,
        \DateTimeImmutable $fin
    ): array {
        $mouvements = $this->decaissementsValides($entityManager, $debut, $fin);

        $parCategorie = [];

        foreach ($mouvements as $mouvement) {
            $cle = $mouvement->getCategorie();

            $parCategorie[$cle] ??= [
                'categorie' => $mouvement->getCategorieLabel(),
                'nombre' => 0,
                'montant' => 0,
            ];

            ++$parCategorie[$cle]['nombre'];
            $parCategorie[$cle]['montant'] += (int) $mouvement->getMontant();
        }

        usort(
            $parCategorie,
            static fn (array $a, array $b): int => $b['montant'] <=> $a['montant']
        );

        return array_values($parCategorie);
    }

    /**
     * @return list<MouvementTresorerie>
     */
    private function decaissementsValides(
        EntityManagerInterface $entityManager,
        \DateTimeImmutable $debut,
        \DateTimeImmutable $fin
    ): array {
        $resultats = $entityManager
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
