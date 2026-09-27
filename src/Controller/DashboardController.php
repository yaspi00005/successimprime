<?php

namespace App\Controller;

use App\Entity\Commandes;
use App\Entity\MouvementTresorerie;
use App\Entity\Paiements;
use App\Repository\ClientsRepository;
use App\Repository\CommandesRepository;
use Doctrine\ORM\EntityManagerInterface;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

final class DashboardController extends AbstractController
{
    private const PERIODES_VALIDES = ['jour', 'semaine', 'mois', 'annee', 'tout'];

    private const GRANULARITES_VALIDES = ['jour', 'semaine', 'mois', 'annee'];

    /**
     * Nombre de points affichés sur le graphique d'évolution, selon
     * la granularité choisie.
     */
    private const NOMBRE_POINTS = [
        'jour' => 30,
        'semaine' => 12,
        'mois' => 12,
        'annee' => 5,
    ];

    #[Route('/', name: 'app_home')]
    public function index(
        Request $request,
        CommandesRepository $commandesRepository,
        ClientsRepository $clientsRepository,
        EntityManagerInterface $entityManager
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

        $granulariteEvolution = $request->query->get('granularite', 'mois');

        if (!\in_array($granulariteEvolution, self::GRANULARITES_VALIDES, true)) {
            $granulariteEvolution = 'mois';
        }

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
            'evolution' => $this->construireEvolution($entityManager, $granulariteEvolution),
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
     * Le calcul se fait en PHP (une requête par indicateur sur toute
     * la fenêtre, puis répartition dans les paniers) plutôt qu'en
     * SQL group-by-date, pour rester indépendant du moteur de base
     * de données -- même approche que les autres écrans de
     * statistiques de l'application.
     *
     * @return array{labels: list<string>, ca: list<int>, commandes: list<int>, encaissements: list<int>, decaissements: list<int>}
     */
    private function construireEvolution(
        EntityManagerInterface $entityManager,
        string $granularite
    ): array {
        $nombrePoints = self::NOMBRE_POINTS[$granularite];

        [$cles, $labels, $debutFenetre] = $this->genererPaniers($granularite, $nombrePoints);

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

            $cle = $this->clePourDate($commande->getDateCommande(), $granularite);

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

            $cle = $this->clePourDate($paiement->getDate(), $granularite);

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

            $cle = $this->clePourDate($mouvement->getDateOperation(), $granularite);

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

    /**
     * @return array{0: list<string>, 1: list<string>, 2: \DateTimeImmutable}
     */
    private function genererPaniers(string $granularite, int $nombrePoints): array
    {
        $maintenant = new \DateTimeImmutable('now');
        $cles = [];
        $labels = [];

        for ($i = $nombrePoints - 1; $i >= 0; --$i) {
            $date = match ($granularite) {
                'jour' => $maintenant->modify('-' . $i . ' days'),
                'semaine' => $maintenant->modify('-' . $i . ' weeks'),
                'annee' => $maintenant->modify('-' . $i . ' years'),
                default => $maintenant->modify('-' . $i . ' months'),
            };

            $cles[] = $this->clePourDate($date, $granularite);
            $labels[] = $this->libellePourDate($date, $granularite);
        }

        $debutFenetre = match ($granularite) {
            'jour' => $maintenant->modify('-' . ($nombrePoints - 1) . ' days')->setTime(0, 0),
            'semaine' => $maintenant->modify('-' . ($nombrePoints - 1) . ' weeks')->modify('monday this week')->setTime(0, 0),
            'annee' => $maintenant->modify('-' . ($nombrePoints - 1) . ' years')->modify('first day of january this year')->setTime(0, 0),
            default => $maintenant->modify('-' . ($nombrePoints - 1) . ' months')->modify('first day of this month')->setTime(0, 0),
        };

        return [$cles, $labels, $debutFenetre];
    }

    private function clePourDate(\DateTimeInterface $date, string $granularite): string
    {
        return match ($granularite) {
            'jour' => $date->format('Y-m-d'),
            'semaine' => $date->format('o-\WW'),
            'annee' => $date->format('Y'),
            default => $date->format('Y-m'),
        };
    }

    private function libellePourDate(\DateTimeInterface $date, string $granularite): string
    {
        static $moisCourts = [
            1 => 'Jan', 2 => 'Fév', 3 => 'Mar', 4 => 'Avr',
            5 => 'Mai', 6 => 'Juin', 7 => 'Juil', 8 => 'Août',
            9 => 'Sep', 10 => 'Oct', 11 => 'Nov', 12 => 'Déc',
        ];

        return match ($granularite) {
            'jour' => $date->format('d/m'),
            'semaine' => 'S' . $date->format('W'),
            'annee' => $date->format('Y'),
            default => $moisCourts[(int) $date->format('n')] . ' ' . $date->format('y'),
        };
    }
}
