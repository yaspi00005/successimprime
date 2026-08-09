<?php

namespace App\Controller;

use App\Entity\MouvementTresorerie;
use App\Form\MouvementTresorerieType;
use App\Repository\MouvementTresorerieRepository;
use App\Service\MouvementTresorerieService;
use Doctrine\DBAL\Exception\UniqueConstraintViolationException;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;
use Symfony\Component\Security\Http\Attribute\IsGranted;
use Doctrine\ORM\EntityManagerInterface;
use App\Repository\CompteTresorerieRepository;
use App\Repository\UserRepository;


#[Route(
    '/gestion/tresorerie/mouvements',
    name: 'app_mouvement_tresorerie_'
)]
#[IsGranted('ROLE_SAISIE_TRESORERIE')]
class MouvementTresorerieController extends AbstractController
{
    
#[Route('', name: 'index', methods: ['GET'])]
public function index(
    Request $request,
    MouvementTresorerieRepository $repository,
    CompteTresorerieRepository $compteRepository,
    UserRepository $userRepository
): Response {
    $user = $this->getUser();

    if (!$user instanceof \App\Entity\User) {
        throw $this->createAccessDeniedException(
            'Utilisateur non authentifié.'
        );
    }

    $estAssistante = $this->isGranted(
        'ROLE_ASSISTANTE_COMMERCIALE'
    );

    $filtres = [
        'recherche' => trim(
            (string) $request->query->get('recherche', '')
        ),
        'compte' => $request->query->get('compte'),
        'agent' => $request->query->get('agent'),
        'type' => $request->query->get('type'),
        'statut' => $request->query->get('statut'),
        'modePaiement' => $request->query->get('modePaiement'),
        'dateDebut' => $request->query->get('dateDebut'),
        'dateFin' => $request->query->get('dateFin'),
    ];

    /*
     * Une assistante ne peut jamais consulter les opérations
     * d’un autre agent, même en modifiant l’URL.
     */
    if ($estAssistante) {
        $filtres['agent'] = $user->getId();

        /*
         * Si elle tente de demander les transferts dans l’URL,
         * le filtre est supprimé. Les transferts seront aussi
         * retirés après la requête.
         */
        if ($filtres['type'] === 'transfert') {
            $filtres['type'] = null;
        }
    }

    $periode = (string) $request->query->get(
        'periode',
        ''
    );

    $maintenant = new \DateTimeImmutable();

    switch ($periode) {
        case 'aujourdhui':
            $filtres['dateDebut'] = $maintenant->format('Y-m-d');
            $filtres['dateFin'] = $maintenant->format('Y-m-d');
            break;

        case 'hier':
            $hier = $maintenant->modify('-1 day');

            $filtres['dateDebut'] = $hier->format('Y-m-d');
            $filtres['dateFin'] = $hier->format('Y-m-d');
            break;

        case 'semaine':
            $filtres['dateDebut'] = $maintenant
                ->modify('monday this week')
                ->format('Y-m-d');

            $filtres['dateFin'] = $maintenant
                ->modify('sunday this week')
                ->format('Y-m-d');
            break;

        case 'mois':
            $filtres['dateDebut'] = $maintenant
                ->modify('first day of this month')
                ->format('Y-m-d');

            $filtres['dateFin'] = $maintenant
                ->modify('last day of this month')
                ->format('Y-m-d');
            break;

        case 'annee':
            $annee = $maintenant->format('Y');

            $filtres['dateDebut'] = $annee . '-01-01';
            $filtres['dateFin'] = $annee . '-12-31';
            break;
    }

    $mouvements = $repository->rechercherAvecFiltres(
        $filtres
    );

    
    

    /*
     * Deuxième protection : aucun transfert n’est transmis
     * au Twig de l’assistante.
     */
    if ($estAssistante) {
        $mouvements = array_values(
            array_filter(
                $mouvements,
                static fn (
                    MouvementTresorerie $mouvement
                ): bool => in_array(
                    $mouvement->getType(),
                    ['encaissement', 'decaissement'],
                    true
                )
            )
        );
    }

    $totaux = [
        'encaissements' => 0,
        'decaissements' => 0,
        'transferts' => 0,
        'nombre' => count($mouvements),
        'soldeNet' => 0,
    ];

    foreach ($mouvements as $mouvement) {
        if ($mouvement->getStatut() !== 'valide') {
            continue;
        }

        $montant = (int) $mouvement->getMontant();

        switch ($mouvement->getType()) {
            case 'encaissement':
                $totaux['encaissements'] += $montant;
                break;

            case 'decaissement':
                $totaux['decaissements'] += $montant;
                break;

            case 'transfert':
                if (!$estAssistante) {
                    $totaux['transferts'] += $montant;
                }
                break;
        }
    }

    $totaux['soldeNet'] =
        $totaux['encaissements']
        - $totaux['decaissements'];

    return $this->render(
        'mouvement_tresorerie/index.html.twig',
        [
            'mouvements' => $mouvements,

            'comptes' => $compteRepository->findBy(
                ['actif' => true],
                ['nom' => 'ASC']
            ),

            /*
             * L’assistante ne reçoit pas la liste des agents.
             */
            'agents' => $estAssistante
                ? []
                : $userRepository->findBy(
                    ['actif' => true],
                    ['username' => 'ASC']
                ),

            'filtres' => $filtres,
            'periode' => $periode,
            'totaux' => $totaux,
            'estAssistante' => $estAssistante,
        ]
    );
}

#[Route('/nouveau', name: 'new', methods: ['GET', 'POST'])]
public function new(
    Request $request,
    EntityManagerInterface $entityManager,
    MouvementTresorerieRepository $repository
): Response {
    $user = $this->getUser();

    if (!$user instanceof \App\Entity\User) {
        throw $this->createAccessDeniedException(
            'Utilisateur non authentifié.'
        );
    }

    $estAssistante = $this->isGranted(
        'ROLE_ASSISTANTE_COMMERCIALE'
    );

    $mouvement = new MouvementTresorerie();

    $mouvement->setReference(
        $this->genererReference($repository)
    );

    $mouvement->setDateOperation(
        new \DateTimeImmutable()
    );

    // L’agent connecté est toujours imposé par le serveur.
    $mouvement->setAgent($user);

    $form = $this->createForm(
        MouvementTresorerieType::class,
        $mouvement
    );

    $form->handleRequest($request);

    if ($form->isSubmitted()) {
        /*
         * Protection contre une modification manuelle
         * du champ agent dans le formulaire HTML.
         */
        $mouvement->setAgent($user);

        if (
            $estAssistante
            && !in_array(
                $mouvement->getType(),
                ['encaissement', 'decaissement'],
                true
            )
        ) {
            $this->addFlash(
                'error',
                'Vous n’êtes pas autorisée à effectuer ce type de mouvement.'
            );

            return $this->redirectToRoute(
                'app_mouvement_tresorerie_new'
            );
        }

        if ($form->isValid()) {
            try {
                $entityManager->wrapInTransaction(
                    function (
                        EntityManagerInterface $entityManager
                    ) use ($mouvement): void {
                        $mouvement->setStatut('valide');

                        $this->appliquerMouvementAuxComptes(
                            $mouvement
                        );

                        $entityManager->persist($mouvement);
                        $entityManager->flush();
                    }
                );

                $this->addFlash(
                    'success',
                    'Le mouvement a été enregistré et le compte a été mis à jour.'
                );

                return $this->redirectToRoute(
                    'app_mouvement_tresorerie_index'
                );
            } catch (UniqueConstraintViolationException) {
                /*
                 * Une nouvelle référence est préparée pour
                 * le prochain affichage du formulaire.
                 */
                $mouvement->setReference(
                    $this->genererReference($repository)
                );

                $this->addFlash(
                    'error',
                    'La référence existe déjà. Veuillez recommencer.'
                );
            } catch (\LogicException $exception) {
                $message = $estAssistante
                    ? 'Opération impossible. Le compte sélectionné ne permet pas cette opération.'
                    : $exception->getMessage();

                $this->addFlash(
                    'error',
                    $message
                );
            } catch (\Throwable $exception) {
                $this->addFlash(
                    'error',
                    'Impossible d’enregistrer le mouvement de trésorerie.'
                );
            }
        } else {
            $this->addFlash(
                'error',
                'Veuillez corriger les informations du formulaire.'
            );
        }
    }

    return $this->render(
        'mouvement_tresorerie/new.html.twig',
        [
            'mouvement' => $mouvement,
            'form' => $form->createView(),
            'estAssistante' => $estAssistante,
        ]
    );
}
    

    #[Route(
        '/{id}',
        name: 'show',
        requirements: ['id' => '\d+'],
        methods: ['GET']
    )]
    public function show(
        MouvementTresorerie $mouvement
    ): Response {
        return $this->render(
            'mouvement_tresorerie/show.html.twig',
            [
                'mouvement' => $mouvement,
            ]
        );
    }

    #[Route(
        '/{id}/valider',
        name: 'validate',
        requirements: ['id' => '\d+'],
        methods: ['POST']
    )]
    #[IsGranted('ROLE_RESPONSABLE_GESTION')]
    public function validateMovement(
        Request $request,
        MouvementTresorerie $mouvement,
        MouvementTresorerieService $service
    ): Response {
        if (!$this->isCsrfTokenValid(
            'validate-mouvement-' . $mouvement->getId(),
            (string) $request->request->get('_token')
        )) {
            $this->addFlash(
                'error',
                'Le jeton de sécurité est invalide.'
            );

            return $this->redirectToRoute(
                'app_mouvement_tresorerie_show',
                [
                    'id' => $mouvement->getId(),
                ]
            );
        }

        try {
            $service->valider($mouvement);

            $this->addFlash(
                'success',
                'Le mouvement a été validé et les soldes ont été mis à jour.'
            );
        } catch (
            \InvalidArgumentException
            | \LogicException $exception
        ) {
            $this->addFlash(
                'error',
                $exception->getMessage()
            );
        }

        return $this->redirectToRoute(
            'app_mouvement_tresorerie_show',
            [
                'id' => $mouvement->getId(),
            ]
        );
    }

    #[Route(
        '/{id}/annuler',
        name: 'cancel',
        requirements: ['id' => '\d+'],
        methods: ['POST']
    )]
    public function cancel(
        Request $request,
        MouvementTresorerie $mouvement,
        MouvementTresorerieService $service
    ): Response {
        if (!$this->isCsrfTokenValid(
            'cancel-mouvement-' . $mouvement->getId(),
            (string) $request->request->get('_token')
        )) {
            $this->addFlash(
                'error',
                'Le jeton de sécurité est invalide.'
            );

            return $this->redirectToRoute(
                'app_mouvement_tresorerie_show',
                [
                    'id' => $mouvement->getId(),
                ]
            );
        }

        $motif = trim(
            (string) $request->request->get('motif', '')
        );

        if ($motif === '') {
            $this->addFlash(
                'error',
                'Le motif d’annulation est obligatoire.'
            );

            return $this->redirectToRoute(
                'app_mouvement_tresorerie_show',
                [
                    'id' => $mouvement->getId(),
                ]
            );
        }

        try {
            $service->annulerEnAttente(
                $mouvement,
                $motif
            );

            $this->addFlash(
                'success',
                'Le mouvement en attente a été annulé.'
            );
        } catch (
            \InvalidArgumentException
            | \LogicException $exception
        ) {
            $this->addFlash(
                'error',
                $exception->getMessage()
            );
        }

        return $this->redirectToRoute(
            'app_mouvement_tresorerie_show',
            [
                'id' => $mouvement->getId(),
            ]
        );
    }
    private function appliquerMouvementAuxComptes(
        MouvementTresorerie $mouvement
    ): void {
        $montant = (int) $mouvement->getMontant();

        if ($montant <= 0) {
            throw new \LogicException(
                'Le montant du mouvement doit être supérieur à zéro.'
            );
        }

        switch ($mouvement->getType()) {
            case 'encaissement':
                $compteDestination = $mouvement->getCompteDestination();

                if ($compteDestination === null) {
                    throw new \LogicException(
                        'Le compte destination est obligatoire pour un encaissement.'
                    );
                }

                $nouveauSolde =
                    (int) $compteDestination->getSoldeActuel()
                    + $montant;

                $compteDestination->setSoldeActuel($nouveauSolde);
                break;

            case 'decaissement':
                $compteSource = $mouvement->getCompteSource();

                if ($compteSource === null) {
                    throw new \LogicException(
                        'Le compte source est obligatoire pour un décaissement.'
                    );
                }

                if (
                    (int) $compteSource->getSoldeActuel()
                    < $montant
                ) {
                    throw new \LogicException(
                        'Le solde du compte source est insuffisant.'
                    );
                }

                $nouveauSolde =
                    (int) $compteSource->getSoldeActuel()
                    - $montant;

                $compteSource->setSoldeActuel($nouveauSolde);
                break;

            case 'transfert':
                $compteSource = $mouvement->getCompteSource();
                $compteDestination = $mouvement->getCompteDestination();

                if (
                    $compteSource === null
                    || $compteDestination === null
                ) {
                    throw new \LogicException(
                        'Les comptes source et destination sont obligatoires pour un transfert.'
                    );
                }

                if ($compteSource === $compteDestination) {
                    throw new \LogicException(
                        'Les comptes source et destination doivent être différents.'
                    );
                }

                if (
                    (int) $compteSource->getSoldeActuel()
                    < $montant
                ) {
                    throw new \LogicException(
                        'Le solde du compte source est insuffisant.'
                    );
                }

                $compteSource->setSoldeActuel(
                    (int) $compteSource->getSoldeActuel()
                        - $montant
                );

                $compteDestination->setSoldeActuel(
                    (int) $compteDestination->getSoldeActuel()
                        + $montant
                );
                break;

            default:
                throw new \LogicException(
                    'Le type de mouvement est invalide.'
                );
        }
    }
    private function genererReference(
        MouvementTresorerieRepository $repository
    ): string {
        do {
            $reference = sprintf(
                'MVT-%s-%04d',
                (new \DateTimeImmutable())->format('YmdHis'),
                random_int(1, 9999)
            );
        } while ($repository->referenceExiste($reference));

        return $reference;
    }
}
