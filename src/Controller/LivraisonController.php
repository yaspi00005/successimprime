<?php

namespace App\Controller;

use App\Entity\CommandesDetails;
use App\Entity\User;
use App\Repository\CommandesDetailsRepository;
use App\Entity\StockSorties;
use App\Service\StockService;
use Doctrine\ORM\EntityManagerInterface;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

#[Route(
    '/livraisons',
    name: 'app_livraisons_'
)]
final class LivraisonController extends AbstractController
{
    /*
     * ============================================================
     * LISTE DES LIVRAISONS
     * ============================================================
     *
     * Affiche :
     * - les lignes prêtes à livrer ;
     * - les lignes en livraison ;
     * - éventuellement les lignes déjà livrées.
     *
     * Filtres :
     * - recherche ;
     * - statut ;
     * - origine ;
     * - dates.
     * ============================================================
     */
    #[Route(
        '/',
        name: 'index',
        methods: ['GET']
    )]
    public function index(
        Request $request,
        CommandesDetailsRepository $commandesDetailsRepository
    ): Response {
        /*
         * --------------------------------------------------------
         * FILTRES
         * --------------------------------------------------------
         */
        $recherche = trim(
            (string) $request->query->get(
                'q',
                ''
            )
        );

        $statut = trim(
            (string) $request->query->get(
                'statut',
                ''
            )
        );

        $origine = trim(
            (string) $request->query->get(
                'origine',
                ''
            )
        );

        $dateDebut = trim(
            (string) $request->query->get(
                'date_debut',
                ''
            )
        );

        $dateFin = trim(
            (string) $request->query->get(
                'date_fin',
                ''
            )
        );

        /*
         * --------------------------------------------------------
         * QUERY BUILDER
         * --------------------------------------------------------
         */
        $qb = $commandesDetailsRepository
            ->createQueryBuilder('detail');

        $qb
            ->leftJoin(
                'detail.commande',
                'commande'
            )
            ->addSelect('commande')

            ->leftJoin(
                'detail.produit',
                'produit'
            )
            ->addSelect('produit')

            ->leftJoin(
                'detail.support',
                'support'
            )
            ->addSelect('support')

            ->leftJoin(
                'detail.machine',
                'machine'
            )
            ->addSelect('machine')

            ->andWhere(
                'detail.statutProduction IN (:statutsLivraison)'
            )
            ->setParameter(
                'statutsLivraison',
                [
                    CommandesDetails::PRODUCTION_PRETE_LIVRAISON,
                    CommandesDetails::PRODUCTION_EN_LIVRAISON,
                    CommandesDetails::PRODUCTION_LIVREE,
                ]
            );

        /*
         * --------------------------------------------------------
         * RECHERCHE TEXTE
         * --------------------------------------------------------
         */
        if ($recherche !== '') {
            $qb
                ->andWhere(
                    $qb->expr()->orX(
                        'LOWER(detail.designation) LIKE LOWER(:recherche)',
                        'LOWER(produit.nom) LIKE LOWER(:recherche)'
                    )
                )
                ->setParameter(
                    'recherche',
                    '%' . $recherche . '%'
                );
        }

        /*
         * --------------------------------------------------------
         * FILTRE STATUT
         * --------------------------------------------------------
         */
        $statutsAutorises = [
            CommandesDetails::PRODUCTION_PRETE_LIVRAISON,
            CommandesDetails::PRODUCTION_EN_LIVRAISON,
            CommandesDetails::PRODUCTION_LIVREE,
        ];

        if (
            $statut !== ''
            && in_array(
                $statut,
                $statutsAutorises,
                true
            )
        ) {
            $qb
                ->andWhere(
                    'detail.statutProduction = :statut'
                )
                ->setParameter(
                    'statut',
                    $statut
                );
        }

        /*
         * --------------------------------------------------------
         * FILTRE ORIGINE
         * --------------------------------------------------------
         *
         * production :
         * productionNecessaire = true
         *
         * directe :
         * productionNecessaire = false
         * --------------------------------------------------------
         */
        if ($origine === 'production') {
            $qb->andWhere(
                'detail.productionNecessaire = true'
            );
        }

        if ($origine === 'directe') {
            $qb->andWhere(
                'detail.productionNecessaire = false'
            );
        }

        /*
         * --------------------------------------------------------
         * FILTRE DATE
         * --------------------------------------------------------
         *
         * Pour le moment, on utilise la date de fin de production.
         *
         * Plus tard, lorsqu'on ajoutera une vraie entité Livraison,
         * nous aurons :
         * - date préparation ;
         * - date départ ;
         * - date livraison.
         * --------------------------------------------------------
         */
        if ($dateDebut !== '') {
            try {
                $debut = new \DateTimeImmutable(
                    $dateDebut . ' 00:00:00'
                );

                $qb
                    ->andWhere(
                        'detail.productionTermineeLe >= :dateDebut'
                    )
                    ->setParameter(
                        'dateDebut',
                        $debut
                    );
            } catch (\Throwable) {
                // Date invalide ignorée.
            }
        }

        if ($dateFin !== '') {
            try {
                $fin = new \DateTimeImmutable(
                    $dateFin . ' 23:59:59'
                );

                $qb
                    ->andWhere(
                        'detail.productionTermineeLe <= :dateFin'
                    )
                    ->setParameter(
                        'dateFin',
                        $fin
                    );
            } catch (\Throwable) {
                // Date invalide ignorée.
            }
        }

        /*
         * --------------------------------------------------------
         * TRI
         * --------------------------------------------------------
         *
         * Les lignes encore à traiter doivent apparaître avant
         * l'historique livré.
         * --------------------------------------------------------
         */
        $qb
            ->addOrderBy(
                'CASE
                    WHEN detail.statutProduction = :prete THEN 1
                    WHEN detail.statutProduction = :enLivraison THEN 2
                    WHEN detail.statutProduction = :livree THEN 3
                    ELSE 4
                END',
                'ASC'
            )
            ->setParameter(
                'prete',
                CommandesDetails::PRODUCTION_PRETE_LIVRAISON
            )
            ->setParameter(
                'enLivraison',
                CommandesDetails::PRODUCTION_EN_LIVRAISON
            )
            ->setParameter(
                'livree',
                CommandesDetails::PRODUCTION_LIVREE
            )
            ->addOrderBy(
                'detail.id',
                'DESC'
            );

        $livraisons = $qb
            ->getQuery()
            ->getResult();

        /*
         * --------------------------------------------------------
         * COMPTEURS
         * --------------------------------------------------------
         */
        $compteurs = [
            'prete' => 0,
            'en_livraison' => 0,
            'livree' => 0,
            'production' => 0,
            'directe' => 0,
        ];

        foreach ($livraisons as $detail) {
            if (
                $detail->getStatutProduction()
                === CommandesDetails::PRODUCTION_PRETE_LIVRAISON
            ) {
                ++$compteurs['prete'];
            }

            if (
                $detail->getStatutProduction()
                === CommandesDetails::PRODUCTION_EN_LIVRAISON
            ) {
                ++$compteurs['en_livraison'];
            }

            if (
                $detail->getStatutProduction()
                === CommandesDetails::PRODUCTION_LIVREE
            ) {
                ++$compteurs['livree'];
            }

            if ($detail->isProductionNecessaire()) {
                ++$compteurs['production'];
            } else {
                ++$compteurs['directe'];
            }
        }

        return $this->render(
            'livraisons/index.html.twig',
            [
                'livraisons' => $livraisons,

                'compteurs' => $compteurs,

                'filtres' => [
                    'q' => $recherche,
                    'statut' => $statut,
                    'origine' => $origine,
                    'date_debut' => $dateDebut,
                    'date_fin' => $dateFin,
                ],
            ]
        );
    }

    /*
     * ============================================================
     * FICHE D'UNE LIVRAISON
     * ============================================================
     */
    #[Route(
        '/{id}',
        name: 'show',
        requirements: [
            'id' => '\d+',
        ],
        methods: ['GET']
    )]
    public function show(
        CommandesDetails $detail
    ): Response {
        /*
         * On ne doit pas accéder à la vue Livraison
         * pour une ligne encore en production.
         */
        if (
            !in_array(
                $detail->getStatutProduction(),
                [
                    CommandesDetails::PRODUCTION_PRETE_LIVRAISON,
                    CommandesDetails::PRODUCTION_EN_LIVRAISON,
                    CommandesDetails::PRODUCTION_LIVREE,
                ],
                true
            )
        ) {
            throw $this->createNotFoundException(
                'Cette ligne de commande n’est pas disponible pour la livraison.'
            );
        }

        return $this->render(
            'livraisons/show.html.twig',
            [
                'detail' => $detail,
            ]
        );
    }

    /*
     * ============================================================
     * PASSER EN LIVRAISON
     * ============================================================
     */
    #[Route(
        '/{id}/demarrer',
        name: 'demarrer',
        requirements: [
            'id' => '\d+',
        ],
        methods: ['POST']
    )]
    public function demarrer(
        CommandesDetails $detail,
        Request $request,
        EntityManagerInterface $em
    ): Response {
        $this->verifierJeton(
            $request,
            'livraison_demarrer_' . $detail->getId()
        );

        try {
            /*
             * La méthode de l'entité vérifie déjà que
             * le statut est PRETE_LIVRAISON.
             */
            $detail->marquerEnLivraison();

            $em->flush();

            $this->addFlash(
                'success',
                sprintf(
                    'La livraison de « %s » a démarré.',
                    $detail->getDesignation()
                )
            );
        } catch (\LogicException $e) {
            $this->addFlash(
                'error',
                $e->getMessage()
            );
        }

        return $this->redirectToRoute(
            'app_livraisons_show',
            [
                'id' => $detail->getId(),
            ]
        );
    }

    /*
     * ============================================================
     * MARQUER COMME LIVRÉE
     * ============================================================
     */
   #[Route(
    '/{id}/livrer',
    name: 'livrer',
    requirements: [
        'id' => '\d+',
    ],
    methods: ['POST']
)]
public function livrer(
    CommandesDetails $detail,
    Request $request,
    EntityManagerInterface $em,
    StockService $stockService
): Response {
    $this->verifierJeton(
        $request,
        'livraison_livrer_' . $detail->getId()
    );

    try {
        /*
         * La ligne doit déjà être en livraison.
         */
        if (
            $detail->getStatutProduction()
            !== CommandesDetails::PRODUCTION_EN_LIVRAISON
        ) {
            throw new \LogicException(
                'La ligne doit être en livraison avant d’être confirmée.'
            );
        }


        /*
         * ========================================================
         * VENTE DIRECTE D'ARTICLE
         * ========================================================
         */
        if (
            $detail->getTypeLigne()
            === CommandesDetails::TYPE_ARTICLE
        ) {
            $article =
                $detail->getArticle();

            if ($article === null) {
                throw new \LogicException(
                    'Aucun article en stock n’est associé à cette ligne.'
                );
            }


            $quantite =
                (float) $detail->getQuantite();

            if ($quantite <= 0) {
                throw new \LogicException(
                    'La quantité à livrer est invalide.'
                );
            }


            /*
             * Référence stable pour éviter
             * une double sortie de stock.
             */
            $reference =
                sprintf(
                    'LIV-DIRECT-%06d',
                    (int) $detail->getId()
                );


            /*
             * Sortie de stock.
             */
            $stockService->consommerPourDetail(
                $detail,
                StockSorties::ORIGINE_LIVRAISON,
                $reference,
                $quantite
            );


            /*
             * Passage au statut livré.
             */
            $detail->marquerLivree();


            $em->flush();


            $this->addFlash(
                'success',
                sprintf(
                    '« %s » a été livré. La sortie de stock a été enregistrée.',
                    $detail->getDesignation()
                )
            );


            return $this->redirectToRoute(
                'app_livraisons_show',
                [
                    'id' => $detail->getId(),
                ]
            );
        }


        /*
         * ========================================================
         * AUTRES TYPES
         * ========================================================
         */
        throw new \LogicException(
            sprintf(
                'La ligne « %s » doit être livrée à partir d’un bon de livraison.',
                $detail->getDesignation()
            )
        );

    } catch (
        \LogicException |
        \RuntimeException |
        \DomainException $e
    ) {
        $this->addFlash(
            'error',
            $e->getMessage()
        );
    }


    return $this->redirectToRoute(
        'app_livraisons_show',
        [
            'id' => $detail->getId(),
        ]
    );
}

    /*
     * ============================================================
     * LIVRAISON DIRECTE
     * ============================================================
     *
     * Cette route peut être utilisée après validation d'une
     * commande pour un consommable/support qui ne nécessite
     * aucune production.
     * ============================================================
     */
    #[Route(
        '/{id}/preparer-directement',
        name: 'preparer_directement',
        requirements: [
            'id' => '\d+',
        ],
        methods: ['POST']
    )]
    public function preparerDirectement(
        CommandesDetails $detail,
        Request $request,
        EntityManagerInterface $em
    ): Response {
        $this->verifierJeton(
            $request,
            'livraison_directe_' . $detail->getId()
        );

        try {
            if ($detail->isProductionNecessaire()) {
                throw new \LogicException(
                    'Cette ligne nécessite une production et ne peut pas être envoyée directement en livraison.'
                );
            }

            $detail->marquerPreteLivraison();

            $em->flush();

            $this->addFlash(
                'success',
                sprintf(
                    '« %s » est prêt pour la livraison.',
                    $detail->getDesignation()
                )
            );
        } catch (\LogicException $e) {
            $this->addFlash(
                'error',
                $e->getMessage()
            );
        }

        return $this->redirectToRoute(
            'app_livraisons_index'
        );
    }

    /*
     * ============================================================
     * UTILISATEUR CONNECTÉ
     * ============================================================
     *
     * On l'utilisera ensuite lorsque nous ajouterons à Livraison :
     * - préparé par ;
     * - livré par ;
     * - réceptionné par ;
     * - dates ;
     * - signature.
     * ============================================================
     */
    private function utilisateurConnecte(): User
    {
        $utilisateur = $this->getUser();

        if (!$utilisateur instanceof User) {
            throw $this->createAccessDeniedException(
                'Utilisateur non authentifié.'
            );
        }

        return $utilisateur;
    }

    /*
     * ============================================================
     * VÉRIFICATION CSRF
     * ============================================================
     */
    private function verifierJeton(
        Request $request,
        string $identifiant
    ): void {
        $token = (string) $request->request->get(
            '_token',
            ''
        );

        if (
            !$this->isCsrfTokenValid(
                $identifiant,
                $token
            )
        ) {
            throw $this->createAccessDeniedException(
                'Jeton de sécurité invalide.'
            );
        }
    }
}