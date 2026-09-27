<?php

namespace App\Controller;

use App\Service\Statistiques\StatistiquesGlobalesService;
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
        StatistiquesGlobalesService $statistiquesGlobalesService
    ): Response {
        [$debut, $fin, $filtres] = $this->resoudrePeriode($request);

        return $this->render('statistiques/globales.html.twig', [
            'parAgent' => $statistiquesGlobalesService->ventesParAgent($debut, $fin),
            'parCaissiere' => $statistiquesGlobalesService->encaissementsParCaissiere($debut, $fin),
            'parProduction' => $statistiquesGlobalesService->productionParAgent($debut, $fin),
            'parMachine' => $statistiquesGlobalesService->rendementParMachine($debut, $fin),
            'topProduits' => $statistiquesGlobalesService->topProduits($debut, $fin),
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
}
