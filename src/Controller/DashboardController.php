<?php

namespace App\Controller;

use App\Repository\ClientsRepository;
use App\Repository\CommandesRepository;
use App\Service\EvolutionFinanciereService;
use App\Service\EvolutionTemporelleService;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

final class DashboardController extends AbstractController
{
    private const PERIODES_VALIDES = ['jour', 'semaine', 'mois', 'annee', 'tout'];

    #[Route('/', name: 'app_home')]
    public function index(
        Request $request,
        CommandesRepository $commandesRepository,
        ClientsRepository $clientsRepository,
        EvolutionTemporelleService $evolutionTemporelleService,
        EvolutionFinanciereService $evolutionFinanciereService
    ): Response {
        /*
         * Un livreur n'a accès qu'aux livraisons : il n'a rien
         * à faire sur le tableau de bord général.
         */
        if ($this->isGranted('ROLE_LIVREUR') && !$this->isGranted('ROLE_ADMIN')) {
            return $this->redirectToRoute('app_livraisons_index');
        }

        $periode = $request->query->get('periode', 'mois');

        if (!\in_array($periode, self::PERIODES_VALIDES, true)) {
            $periode = 'mois';
        }

        $granulariteEvolution = $evolutionTemporelleService->normaliserGranularite(
            $request->query->get('granularite')
        );

        [$debut, $fin] = $this->calculerPeriode($periode);

        $statsParAgent = $commandesRepository->statistiquesParAgent($debut, $fin);

        $totalCommandes = array_sum(array_column($statsParAgent, 'nbCommandes'));
        $totalCa = array_sum(array_column($statsParAgent, 'caGenere'));
        $meilleurCa = $statsParAgent === [] ? 0 : max(array_column($statsParAgent, 'caGenere'));

        return $this->render('dashboard/index.html.twig', [
            'statsParAgent' => $statsParAgent,
            'totalCommandes' => $totalCommandes,
            'totalCa' => $totalCa,
            'meilleurCa' => $meilleurCa,
            'totalClients' => $clientsRepository->compterClients(),
            'periode' => $periode,
            'granulariteEvolution' => $granulariteEvolution,
            'evolution' => $evolutionFinanciereService->calculer($granulariteEvolution),
        ]);
    }

    /**
     * @return array{0: ?\DateTimeImmutable, 1: ?\DateTimeImmutable}
     */
    private function calculerPeriode(string $periode): array
    {
        $fin = new \DateTimeImmutable('now');

        $debut = match ($periode) {
            'jour' => $fin->setTime(0, 0),
            'semaine' => $fin->modify('monday this week')->setTime(0, 0),
            'annee' => $fin->modify('first day of january this year')->setTime(0, 0),
            'tout' => null,
            default => $fin->modify('first day of this month')->setTime(0, 0),
        };

        return [$debut, $fin];
    }
}
