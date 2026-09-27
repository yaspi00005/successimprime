<?php

namespace App\Controller;

use App\Entity\Commandes;
use App\Repository\CommandesRepository;
use App\Service\EvolutionFinanciereService;
use App\Service\EvolutionTemporelleService;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

/**
 * Statistiques detaillees des commandes : evolution dans le temps
 * (jour/semaine/mois/annee) et suivi des commandes non soldees
 * (impayees ou partiellement payees), classees par anciennete.
 */
#[Route('/statistiques/commandes', name: 'app_statistiques_commandes_')]
final class StatistiquesCommandesController extends AbstractController
{
    /**
     * Tranches d'ancienneté (en jours depuis la date de commande)
     * pour regrouper les impayés par urgence.
     */
    private const TRANCHES_ANCIENNETE = [
        ['libelle' => '0 à 7 jours', 'min' => 0, 'max' => 7],
        ['libelle' => '8 à 30 jours', 'min' => 8, 'max' => 30],
        ['libelle' => '31 à 90 jours', 'min' => 31, 'max' => 90],
        ['libelle' => 'Plus de 90 jours', 'min' => 91, 'max' => null],
    ];

    #[Route('', name: 'index', methods: ['GET'])]
    public function index(
        Request $request,
        CommandesRepository $commandesRepository,
        EvolutionTemporelleService $evolutionTemporelleService,
        EvolutionFinanciereService $evolutionFinanciereService
    ): Response {
        $granularite = $evolutionTemporelleService->normaliserGranularite(
            $request->query->get('granularite')
        );

        [$commandesNonSoldees, $parTranche] = $this->construireCommandesNonSoldees(
            $commandesRepository
        );

        return $this->render('statistiques/commandes.html.twig', [
            'evolution' => $evolutionFinanciereService->calculer($granularite),
            'granulariteEvolution' => $granularite,
            'commandesNonSoldees' => $commandesNonSoldees,
            'parTranche' => $parTranche,
            'totalReste' => array_sum(array_column($commandesNonSoldees, 'reste')),
        ]);
    }

    /**
     * @return array{0: list<array{commande: Commandes, reste: int, jours: int}>, 1: list<array{libelle: string, nombre: int, montant: int}>}
     */
    private function construireCommandesNonSoldees(
        CommandesRepository $commandesRepository
    ): array {
        $commandes = $commandesRepository->findToutesNonSoldees();

        $maintenant = new \DateTimeImmutable('today');

        $lignes = [];

        foreach ($commandes as $commande) {
            if (!$commande instanceof Commandes) {
                continue;
            }

            if ($commande->getStatutTravaux() === 'annulee') {
                continue;
            }

            $paye = 0;

            foreach ($commande->getPaiements() as $paiement) {
                if ($paiement->estAnnule()) {
                    continue;
                }

                $paye += (int) $paiement->getMontant();
            }

            $reste = max(0, (int) $commande->getTotalTtc() - $paye);

            if ($reste <= 0) {
                continue;
            }

            $dateCommande = \DateTimeImmutable::createFromInterface($commande->getDateCommande());
            $jours = max(0, $dateCommande->diff($maintenant)->days);

            $lignes[] = [
                'commande' => $commande,
                'reste' => $reste,
                'jours' => $jours,
            ];
        }

        usort(
            $lignes,
            static fn (array $a, array $b): int => $b['jours'] <=> $a['jours']
        );

        $parTranche = [];

        foreach (self::TRANCHES_ANCIENNETE as $tranche) {
            $parTranche[] = [
                'libelle' => $tranche['libelle'],
                'nombre' => 0,
                'montant' => 0,
            ];
        }

        foreach ($lignes as $ligne) {
            foreach (self::TRANCHES_ANCIENNETE as $index => $tranche) {
                $dansLaTranche = $ligne['jours'] >= $tranche['min']
                    && ($tranche['max'] === null || $ligne['jours'] <= $tranche['max']);

                if ($dansLaTranche) {
                    ++$parTranche[$index]['nombre'];
                    $parTranche[$index]['montant'] += $ligne['reste'];

                    break;
                }
            }
        }

        return [array_slice($lignes, 0, 100), $parTranche];
    }
}
