<?php

namespace App\Controller;

use App\Entity\Commandes;
use App\Entity\MouvementTresorerie;
use App\Entity\Paiements;
use App\Repository\ClientsRepository;
use App\Repository\CommandesRepository;
use App\Service\EvolutionTemporelleService;
use Doctrine\ORM\EntityManagerInterface;
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
        EntityManagerInterface $entityManager,
        EvolutionTemporelleService $evolutionService
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

        $granulariteEvolution = $evolutionService->normaliserGranularite(
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
            'evolution' => $this->construireEvolution($entityManager, $evolutionService, $granulariteEvolution),
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

    /**
     * Construit les points du graphique d'évolution (chiffre
     * d'affaires, nombre de commandes, encaissements, décaissements)
     * sur les N dernières périodes de la granularité choisie.
     *
     * @return array{labels: list<string>, ca: list<int>, commandes: list<int>, encaissements: list<int>, decaissements: list<int>}
     */
    private function construireEvolution(
        EntityManagerInterface $entityManager,
        EvolutionTemporelleService $evolutionService,
        string $granularite
    ): array {
        [$cles, $labels, $debutFenetre] = $evolutionService->genererPaniers($granularite);

        $ca = array_fill_keys($cles, 0);
        $commandes = array_fill_keys($cles, 0);
        $encaissements = array_fill_keys($cles, 0);
        $decaissements = array_fill_keys($cles, 0);

        /*
         * ============================================================
         * CHIFFRE D'AFFAIRES / COMMANDES
         * ============================================================
         */

        $listeCommandes = $entityManager
            ->getRepository(Commandes::class)
            ->createQueryBuilder('c')
            ->andWhere('c.dateCommande >= :debut')
            ->andWhere('c.deleted = false')
            ->setParameter('debut', $debutFenetre)
            ->getQuery()
            ->getResult();

        foreach ($listeCommandes as $commande) {
            if (!$commande instanceof Commandes) {
                continue;
            }

            if ($commande->getStatutTravaux() === 'annulee') {
                continue;
            }

            $cle = $evolutionService->clePourDate($commande->getDateCommande(), $granularite);

            if (!isset($ca[$cle])) {
                continue;
            }

            ++$commandes[$cle];
            $ca[$cle] += (int) $commande->getTotalTtc();
        }

        /*
         * ============================================================
         * ENCAISSEMENTS
         * ============================================================
         */

        $listePaiements = $entityManager
            ->getRepository(Paiements::class)
            ->createQueryBuilder('p')
            ->andWhere('p.date >= :debut')
            ->setParameter('debut', $debutFenetre)
            ->getQuery()
            ->getResult();

        foreach ($listePaiements as $paiement) {
            if (!$paiement instanceof Paiements) {
                continue;
            }

            if ($paiement->estAnnule()) {
                continue;
            }

            $cle = $evolutionService->clePourDate($paiement->getDate(), $granularite);

            if (!isset($encaissements[$cle])) {
                continue;
            }

            $encaissements[$cle] += (int) $paiement->getMontant();
        }

        /*
         * ============================================================
         * DÉCAISSEMENTS (DÉPENSES)
         * ============================================================
         */

        $listeMouvements = $entityManager
            ->getRepository(MouvementTresorerie::class)
            ->createQueryBuilder('m')
            ->andWhere('m.dateOperation >= :debut')
            ->andWhere('m.type = :type')
            ->setParameter('debut', $debutFenetre)
            ->setParameter('type', MouvementTresorerie::TYPE_DECAISSEMENT)
            ->getQuery()
            ->getResult();

        foreach ($listeMouvements as $mouvement) {
            if (!$mouvement instanceof MouvementTresorerie) {
                continue;
            }

            if (!$mouvement->isValide()) {
                continue;
            }

            $cle = $evolutionService->clePourDate($mouvement->getDateOperation(), $granularite);

            if (!isset($decaissements[$cle])) {
                continue;
            }

            $decaissements[$cle] += (int) $mouvement->getMontant();
        }

        return [
            'labels' => $labels,
            'ca' => array_values($ca),
            'commandes' => array_values($commandes),
            'encaissements' => array_values($encaissements),
            'decaissements' => array_values($decaissements),
        ];
    }
}
