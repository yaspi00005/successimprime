<?php

namespace App\Controller;

use App\Entity\CompteTresorerie;
use App\Repository\CompteTresorerieRepository;
use App\Repository\MouvementTresorerieRepository;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;
use Symfony\Component\Security\Http\Attribute\IsGranted;

#[Route('/gestion/tresorerie/journal-caisse')]
#[IsGranted('ROLE_RESPONSABLE_GESTION')]
class JournalCaisseController extends AbstractController
{
    #[Route('', name: 'app_journal_caisse_index', methods: ['GET'])]
    public function index(
        Request $request,
        CompteTresorerieRepository $compteRepository,
        MouvementTresorerieRepository $mouvementRepository
    ): Response {
        /*
         * Par défaut, le journal affiche le mois en cours.
         */
        $aujourdhui = new \DateTimeImmutable();

        $dateDebutValeur = trim(
            (string) $request->query->get(
                'dateDebut',
                $aujourdhui->format('Y-m-01')
            )
        );

        $dateFinValeur = trim(
            (string) $request->query->get(
                'dateFin',
                $aujourdhui->format('Y-m-d')
            )
        );

        $compteId = $request->query->getInt('compte');

        /*
         * Seuls les comptes actifs de type caisse
         * sont proposés dans le journal.
         *
         * Si votre propriété s’appelle "type" au lieu de
         * "typeCompte", remplacez typeCompte par type.
         */
        $caisses = $compteRepository->findBy(
            [
                'type' => 'caisse',
                'actif' => true,
            ],
            [
                'nom' => 'ASC',
            ]
        );

        $compteSelectionne = null;
        $journal = $this->journalVide();

        /*
         * Conversion et validation des dates.
         */
        try {
            $dateDebut = new \DateTimeImmutable(
                $dateDebutValeur . ' 00:00:00'
            );
        } catch (\Throwable) {
            $dateDebut = $aujourdhui->modify(
                'first day of this month'
            )->setTime(0, 0);

            $dateDebutValeur = $dateDebut->format('Y-m-d');

            $this->addFlash(
                'warning',
                'La date de début était invalide et a été corrigée.'
            );
        }

        try {
            $dateFin = new \DateTimeImmutable(
                $dateFinValeur . ' 23:59:59'
            );
        } catch (\Throwable) {
            $dateFin = $aujourdhui->setTime(23, 59, 59);

            $dateFinValeur = $dateFin->format('Y-m-d');

            $this->addFlash(
                'warning',
                'La date de fin était invalide et a été corrigée.'
            );
        }

        if ($dateDebut > $dateFin) {
            $this->addFlash(
                'error',
                'La date de début ne peut pas être postérieure à la date de fin.'
            );
        }  elseif ($compteId > 0) {
    /*
     * La caisse est recherchée directement avec toutes
     * les conditions nécessaires.
     */
    $compteSelectionne = $compteRepository->findOneBy([
        'id' => $compteId,
        'type' => 'caisse',
        'actif' => true,
    ]);

    if (!$compteSelectionne instanceof CompteTresorerie) {
        $this->addFlash(
            'error',
            'La caisse sélectionnée est introuvable ou inactive.'
        );
    } else {
        $journal = $mouvementRepository->construireJournalCompte(
            $compteSelectionne,
            $dateDebut,
            $dateFin
        );
    }
}

        return $this->render(
            'journal_caisse/index.html.twig',
            [
                'caisses' => $caisses,
                'compteSelectionne' => $compteSelectionne,
                'journal' => $journal,
                'filtres' => [
                    'compte' => $compteId > 0
                        ? $compteId
                        : null,
                    'dateDebut' => $dateDebutValeur,
                    'dateFin' => $dateFinValeur,
                ],
            ]
        );
    }

    /**
     * Structure utilisée lorsqu’aucune caisse
     * n’est encore sélectionnée.
     *
     * @return array{
     *     lignes: array,
     *     soldeOuverture: int,
     *     totalEntrees: int,
     *     totalSorties: int,
     *     soldeCloture: int,
     *     nombre: int
     * }
     */
    private function journalVide(): array
    {
        return [
            'lignes' => [],
            'soldeOuverture' => 0,
            'totalEntrees' => 0,
            'totalSorties' => 0,
            'soldeCloture' => 0,
            'nombre' => 0,
        ];
    }
}