<?php

namespace App\Controller;

use App\Entity\Clients;
use App\Form\ClientsType;
use App\Repository\ClientsRepository;
use Doctrine\ORM\EntityManagerInterface;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\Form\FormError;
use Symfony\Component\Form\FormInterface;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;
use App\Entity\Paiements;
use App\Repository\CommandesRepository;
use App\Repository\DevisRepository;
use Symfony\Bridge\Doctrine\Attribute\MapEntity;
use Doctrine\DBAL\Exception\UniqueConstraintViolationException;

#[Route('/clients')]
final class ClientsController extends AbstractController
{
    #[Route(
        '',
        name: 'app_clients_index',
        methods: ['GET']
    )]
    public function index(): Response
    {
        $nouveauClient = new Clients();

        $formAjout = $this->createForm(
            ClientsType::class,
            $nouveauClient,
            [
                'action' => $this->generateUrl('app_clients_new'),
                'method' => 'POST',
            ]
        );

        return $this->render('clients/index.html.twig', [
            'formAjout' => $formAjout->createView(),
        ]);
    }

    /*
     * Cette route doit rester avant /{id}.
     */
    #[Route(
        '/actions-en-masse',
        name: 'app_clients_mass_action',
        methods: ['POST']
    )]
    public function massAction(
        Request $request,
        ClientsRepository $clientsRepository,
        EntityManagerInterface $entityManager
    ): JsonResponse {
        $data = json_decode(
            $request->getContent(),
            true
        ) ?? [];

        if (!$this->isCsrfTokenValid(
            'clients_mass_action',
            $data['_token'] ?? ''
        )) {
            return $this->json([
                'success' => false,
                'message' => 'Jeton de sécurité invalide.',
            ], Response::HTTP_FORBIDDEN);
        }

        $ids = array_values(array_unique(array_filter(
            array_map(
                'intval',
                is_array($data['ids'] ?? null)
                    ? $data['ids']
                    : []
            )
        )));

        $action = $data['action'] ?? '';

        if ($ids === []) {
            return $this->json([
                'success' => false,
                'message' => 'Sélectionnez au moins un client.',
            ], Response::HTTP_UNPROCESSABLE_ENTITY);
        }

        if (!in_array(
            $action,
            ['bloquer', 'debloquer', 'supprimer'],
            true
        )) {
            return $this->json([
                'success' => false,
                'message' => 'Action non reconnue.',
            ], Response::HTTP_UNPROCESSABLE_ENTITY);
        }

        $clients = $clientsRepository->findBy([
            'id' => $ids,
        ]);

        if ($clients === []) {
            return $this->json([
                'success' => false,
                'message' => 'Aucun client correspondant trouvé.',
            ], Response::HTTP_NOT_FOUND);
        }

        foreach ($clients as $client) {
            if ($action === 'bloquer') {
                $client->setStatut(false);
            } elseif ($action === 'debloquer') {
                $client->setStatut(true);
            } elseif ($action === 'supprimer') {
                $entityManager->remove($client);
            }
        }

        $entityManager->flush();

        $messages = [
            'bloquer' =>
            'Les clients sélectionnés ont été bloqués.',
            'debloquer' =>
            'Les clients sélectionnés ont été débloqués.',
            'supprimer' =>
            'Les clients sélectionnés ont été supprimés.',
        ];

        return $this->json([
            'success' => true,
            'message' => $messages[$action],
        ]);
    }

    #[Route(
        '/new',
        name: 'app_clients_new',
        methods: ['POST']
    )]
    public function new(
        Request $request,
        EntityManagerInterface $entityManager,
        ClientsRepository $clientsRepository
    ): JsonResponse {
        $client = new Clients();

        /*
     * ============================================================
     * CODE PROVISOIRE
     * ============================================================
     *
     * La colonne code est obligatoire et unique.
     * L'identifiant n'existe pas encore avant le premier flush.
     */
        $client->setCode(
            'TMP-' . bin2hex(
                random_bytes(12)
            )
        );


        $form = $this->createForm(
            ClientsType::class,
            $client
        );

        $form->handleRequest($request);


        /*
     * ============================================================
     * FORMULAIRE NON SOUMIS
     * ============================================================
     */

        if (!$form->isSubmitted()) {
            return $this->json(
                [
                    'success' => false,

                    'message' =>
                    'Le formulaire n’a pas été soumis.',
                ],
                Response::HTTP_BAD_REQUEST
            );
        }


        /*
     * ============================================================
     * DROIT B2B
     * ============================================================
     */

        if (
            !$this->isGranted('ROLE_ADMIN')
            &&
            $client->isB2B()
        ) {
            return $this->json(
                [
                    'success' => false,

                    'message' =>
                    'Vous n’êtes pas autorisé à créer un client B2B.',
                ],
                Response::HTTP_FORBIDDEN
            );
        }


        /*
     * ============================================================
     * VALIDATION IDENTITÉ
     * ============================================================
     */

        $this->validerIdentiteClient(
            $form,
            $client
        );


        /*
     * ============================================================
     * VÉRIFICATION TÉLÉPHONE AVANT SQL
     * ============================================================
     */

        $telephone =
            trim(
                (string)
                $client->getTelephone()
            );


        if (
            $telephone !== ''
            &&
            $clientsRepository
            ->telephoneExistePourAutreClient(
                $telephone
            )
        ) {
            /*
         * On attache aussi l'erreur directement
         * au champ téléphone.
         */
            if ($form->has('telephone')) {
                $form
                    ->get('telephone')
                    ->addError(
                        new FormError(
                            'Un client avec ce numéro de téléphone existe déjà.'
                        )
                    );
            }

            return $this->json(
                [
                    'success' => false,

                    'message' =>
                    'Ce numéro de téléphone est déjà utilisé par un autre client.',

                    'errors' => [
                        'telephone' => [
                            'Un client avec ce numéro de téléphone existe déjà.',
                        ],
                    ],
                ],
                Response::HTTP_UNPROCESSABLE_ENTITY
            );
        }


        /*
     * ============================================================
     * VALIDATION SYMFONY
     * ============================================================
     */

        if (!$form->isValid()) {
            return $this->json(
                [
                    'success' => false,

                    'message' =>
                    'Veuillez corriger les champs indiqués.',

                    'errors' =>
                    $this->getFormErrors(
                        $form
                    ),
                ],
                Response::HTTP_UNPROCESSABLE_ENTITY
            );
        }


        /*
     * ============================================================
     * ENREGISTREMENT
     * ============================================================
     */

        try {
            $entityManager->persist(
                $client
            );

            /*
         * Premier flush :
         * génération de l'ID.
         */
            $entityManager->flush();


            /*
         * On transforme :
         *
         * TMP-xxxxxxxx
         *
         * en :
         *
         * CLI-000001
         */
            $client->genererCodeDepuisId();


            /*
         * Deuxième flush :
         * sauvegarde du code définitif.
         */
            $entityManager->flush();
        } catch (
            UniqueConstraintViolationException $e
        ) {
            /*
         * Deuxième sécurité.
         *
         * Même si deux utilisateurs essaient de créer
         * exactement le même téléphone simultanément,
         * la contrainte UNIQUE MySQL reste l'autorité finale.
         */

            return $this->json(
                [
                    'success' => false,

                    'message' =>
                    'Ce numéro de téléphone est déjà utilisé par un autre client.',

                    'errors' => [
                        'telephone' => [
                            'Un client avec ce numéro de téléphone existe déjà.',
                        ],
                    ],
                ],
                Response::HTTP_UNPROCESSABLE_ENTITY
            );
        }


        /*
     * ============================================================
     * SUCCÈS
     * ============================================================
     */

        return $this->json(
            [
                'success' => true,

                'message' => sprintf(
                    'Le client %s a été ajouté avec succès.',
                    $client->getCode()
                ),

                'client' => [
                    'id' =>
                    $client->getId(),

                    'publicId' =>
                    $client
                        ->getPublicId()
                        ->toRfc4122(),

                    'code' =>
                    $client->getCode(),

                    'showUrl' =>
                    $this->generateUrl(
                        'app_clients_show',
                        [
                            'publicId' =>
                            $client
                                ->getPublicId()
                                ->toRfc4122(),
                        ]
                    ),
                ],
            ],
            Response::HTTP_CREATED
        );
    }

    #[Route(
        '/{id}/formulaire-modification',
        name: 'app_clients_edit_form',
        requirements: ['id' => '\d+'],
        methods: ['GET']
    )]
    public function editForm(
        Clients $client
    ): Response {
        $form = $this->createForm(
            ClientsType::class,
            $client,
            [
                'action' => $this->generateUrl(
                    'app_clients_edit',
                    ['id' => $client->getId()]
                ),
                'method' => 'POST',
            ]
        );

        return $this->render(
            'clients/_modal_form.html.twig',
            [
                'form' => $form->createView(),
                'client' => $client,
                'mode' => 'edit',
            ]
        );
    }

    #[Route(
        '/{id}/edit',
        name: 'app_clients_edit',
        requirements: [
            'id' => '\d+',
        ],
        methods: ['POST']
    )]
    public function edit(
        Request $request,
        Clients $client,
        EntityManagerInterface $entityManager,
        ClientsRepository $clientsRepository
    ): JsonResponse {
        $form = $this->createForm(
            ClientsType::class,
            $client
        );

        $form->handleRequest(
            $request
        );


        /*
     * ============================================================
     * FORMULAIRE
     * ============================================================
     */

        if (!$form->isSubmitted()) {
            return $this->json(
                [
                    'success' => false,

                    'message' =>
                    'Le formulaire n’a pas été soumis.',
                ],
                Response::HTTP_BAD_REQUEST
            );
        }


        /*
     * ============================================================
     * DROIT B2B
     * ============================================================
     */

        if (
            !$this->isGranted('ROLE_ADMIN')
            &&
            $client->isB2B()
        ) {
            return $this->json(
                [
                    'success' => false,

                    'message' =>
                    'Vous n’êtes pas autorisé à définir un client en B2B.',
                ],
                Response::HTTP_FORBIDDEN
            );
        }


        /*
     * ============================================================
     * VALIDATION IDENTITÉ
     * ============================================================
     */

        $this->validerIdentiteClient(
            $form,
            $client
        );


        /*
     * ============================================================
     * CONTRÔLE DU TÉLÉPHONE
     * ============================================================
     */

        $telephone =
            trim(
                (string)
                $client->getTelephone()
            );


        if (
            $telephone !== ''
            &&
            $clientsRepository
            ->telephoneExistePourAutreClient(
                $telephone,
                $client->getId()
            )
        ) {
            if ($form->has('telephone')) {
                $form
                    ->get('telephone')
                    ->addError(
                        new FormError(
                            'Un autre client possède déjà ce numéro de téléphone.'
                        )
                    );
            }


            return $this->json(
                [
                    'success' => false,

                    'message' =>
                    'Ce numéro de téléphone est déjà utilisé par un autre client.',

                    'errors' => [
                        'telephone' => [
                            'Un autre client possède déjà ce numéro de téléphone.',
                        ],
                    ],
                ],
                Response::HTTP_UNPROCESSABLE_ENTITY
            );
        }


        /*
     * ============================================================
     * VALIDATION DU FORMULAIRE
     * ============================================================
     */

        if (!$form->isValid()) {
            return $this->json(
                [
                    'success' => false,

                    'message' =>
                    'Veuillez corriger les champs indiqués.',

                    'errors' =>
                    $this->getFormErrors(
                        $form
                    ),
                ],
                Response::HTTP_UNPROCESSABLE_ENTITY
            );
        }


        /*
     * ============================================================
     * SAUVEGARDE
     * ============================================================
     */

        try {
            $entityManager->flush();
        } catch (
            UniqueConstraintViolationException $e
        ) {
            return $this->json(
                [
                    'success' => false,

                    'message' =>
                    'Ce numéro de téléphone est déjà utilisé par un autre client.',

                    'errors' => [
                        'telephone' => [
                            'Un autre client possède déjà ce numéro de téléphone.',
                        ],
                    ],
                ],
                Response::HTTP_UNPROCESSABLE_ENTITY
            );
        }


        /*
     * ============================================================
     * SUCCÈS
     * ============================================================
     */

        return $this->json([
            'success' => true,

            'message' => sprintf(
                'Le client %s a été modifié avec succès.',
                $client->getCode()
            ),
        ]);
    }

    #[Route(
        '/{id}/toggle-statut',
        name: 'app_clients_toggle_statut',
        requirements: ['id' => '\d+'],
        methods: ['POST']
    )]
    public function toggleStatut(
        Clients $client,
        Request $request,
        EntityManagerInterface $entityManager
    ): JsonResponse {
        $data = json_decode(
            $request->getContent(),
            true
        ) ?? [];

        if (!$this->isCsrfTokenValid(
            'toggle_client_' . $client->getId(),
            $data['_token'] ?? ''
        )) {
            return $this->json([
                'success' => false,
                'message' => 'Jeton de sécurité invalide.',
            ], Response::HTTP_FORBIDDEN);
        }

        $client->setStatut(!$client->isStatut());

        $entityManager->flush();

        return $this->json([
            'success' => true,
            'statut' => $client->isStatut(),
            'message' => $client->isStatut()
                ? 'Le client a été débloqué.'
                : 'Le client a été bloqué.',
        ]);
    }

    #[Route(
        '/fiche/{publicId}',
        name: 'app_clients_show',
        methods: ['GET']
    )]
    public function show(
        #[MapEntity(mapping: [
            'publicId' => 'publicId',
        ])]
        Clients $client,
        CommandesRepository $commandesRepository,
        DevisRepository $devisRepository
    ): Response {
        /*
     * Puis tu gardes ici tout le reste
     * de notre méthode show :
     *
     * commandes
     * devis
     * paiements
     * statistiques
     * crédit
     */
        /*
     * ============================================================
     * COMMANDES DU CLIENT
     * ============================================================
     */

        $commandes =
            $commandesRepository->findBy(
                [
                    'clients' => $client,
                    'deleted' => false,
                ],
                [
                    'dateCommande' => 'DESC',
                ]
            );


        /*
     * ============================================================
     * DEVIS DU CLIENT
     * ============================================================
     */

        $devis =
            $devisRepository->findBy(
                [
                    'clients' => $client,
                    'deleted' => false,
                ],
                [
                    'dateDevis' => 'DESC',
                ]
            );


        /*
     * ============================================================
     * STATISTIQUES
     * ============================================================
     */

        $totalCommandes = 0;

        $totalPaye = 0;

        $resteAPayer = 0;

        $nombreCommandes = count($commandes);

        $nombreDevis = count($devis);

        $nombrePaiements = 0;


        /*
     * Tous les paiements du client.
     */
        $paiements = [];


        /*
     * Données détaillées par commande.
     */
        $commandesAvecPaiements = [];


        foreach ($commandes as $commande) {

            $montantCommande =
                (int) $commande->getTotalTtc();


            $totalCommandes +=
                $montantCommande;


            /*
         * ========================================================
         * PAIEMENTS VALIDÉS DE CETTE COMMANDE
         * ========================================================
         *
         * IMPORTANT :
         * on ne compte PAS :
         *
         * - paiement annulé ;
         * - paiement rejeté ;
         * - paiement encore en attente.
         * ========================================================
         */

            $totalPayeCommande = 0;

            $paiementsCommande = [];


            foreach (
                $commande->getPaiements()
                as $paiement
            ) {
                /*
             * On ajoute le paiement dans l'historique,
             * quel que soit son statut.
             */
                $paiements[] =
                    $paiement;

                $paiementsCommande[] =
                    $paiement;


                if (
                    $paiement->getStatut()
                    !==
                    Paiements::STATUT_VALIDE
                ) {
                    continue;
                }


                $montantPaiement =
                    (int) $paiement->getMontant();


                $totalPayeCommande +=
                    $montantPaiement;

                $totalPaye +=
                    $montantPaiement;

                ++$nombrePaiements;
            }


            /*
         * Reste réellement dû sur la commande.
         */
            $resteCommande =
                max(
                    0,
                    $montantCommande
                        -
                        $totalPayeCommande
                );


            $resteAPayer +=
                $resteCommande;


            /*
         * Statut calculé dynamiquement.
         */
            if ($totalPayeCommande <= 0) {
                $statutPaiement =
                    'impayee';
            } elseif (
                $totalPayeCommande
                <
                $montantCommande
            ) {
                $statutPaiement =
                    'partielle';
            } else {
                $statutPaiement =
                    'payee';
            }


            $commandesAvecPaiements[] = [
                'commande' =>
                $commande,

                'totalTtc' =>
                $montantCommande,

                'totalPaye' =>
                $totalPayeCommande,

                'resteAPayer' =>
                $resteCommande,

                'statutPaiement' =>
                $statutPaiement,

                'paiements' =>
                $paiementsCommande,
            ];
        }


        /*
     * ============================================================
     * TRI DES PAIEMENTS
     * ============================================================
     *
     * Plus récent en premier.
     * ============================================================
     */

        usort(
            $paiements,
            static function (
                Paiements $a,
                Paiements $b
            ): int {
                $dateA =
                    $a->getDate()
                    ?->getTimestamp()
                    ?? 0;

                $dateB =
                    $b->getDate()
                    ?->getTimestamp()
                    ?? 0;

                return $dateB <=> $dateA;
            }
        );


        /*
     * ============================================================
     * CRÉDIT CLIENT
     * ============================================================
     */

        $plafondCredit =
            max(
                0,
                (int) $client->getPlafondCredit()
            );


        /*
     * L'encours représente ce que le client
     * doit encore à l'entreprise.
     */
        $encours =
            $resteAPayer;


        /*
     * Crédit encore disponible.
     */
        $creditDisponible =
            max(
                0,
                $plafondCredit
                    -
                    $encours
            );


        /*
     * Montant éventuel de dépassement.
     */
        $depassementCredit =
            max(
                0,
                $encours
                    -
                    $plafondCredit
            );


        /*
     * Pourcentage d'utilisation.
     */
        $pourcentageCredit =
            $plafondCredit > 0
            ? min(
                100,
                (int) round(
                    (
                        $encours
                        /
                        $plafondCredit
                    )
                        * 100
                )
            )
            : 0;


        /*
     * ============================================================
     * DEVIS : STATISTIQUES
     * ============================================================
     */

        $totalDevis = 0;

        foreach ($devis as $unDevis) {
            $totalDevis +=
                (int) $unDevis->getTotalTtc();
        }


        /*
     * ============================================================
     * ENVOI AU TWIG
     * ============================================================
     */

        return $this->render(
            'clients/show.html.twig',
            [
                'client' =>
                $client,

                'commandes' =>
                $commandesAvecPaiements,

                'devis' =>
                $devis,

                'paiements' =>
                $paiements,

                'statistiques' => [
                    'nombreCommandes' =>
                    $nombreCommandes,

                    'nombreDevis' =>
                    $nombreDevis,

                    'nombrePaiements' =>
                    $nombrePaiements,

                    'totalCommandes' =>
                    $totalCommandes,

                    'totalDevis' =>
                    $totalDevis,

                    'totalPaye' =>
                    $totalPaye,

                    'resteAPayer' =>
                    $resteAPayer,

                    'encours' =>
                    $encours,
                ],

                'credit' => [
                    'plafond' =>
                    $plafondCredit,

                    'encours' =>
                    $encours,

                    'disponible' =>
                    $creditDisponible,

                    'depassement' =>
                    $depassementCredit,

                    'pourcentage' =>
                    $pourcentageCredit,
                ],
            ]
        );
    }

    #[Route(
        '/{id}',
        name: 'app_clients_delete',
        requirements: ['id' => '\d+'],
        methods: ['POST']
    )]
    public function delete(
        Request $request,
        Clients $client,
        EntityManagerInterface $entityManager
    ): Response {
        if ($this->isCsrfTokenValid(
            'delete' . $client->getId(),
            $request->getPayload()->getString('_token')
        )) {
            $entityManager->remove($client);
            $entityManager->flush();
        }

        return $this->redirectToRoute(
            'app_clients_index',
            [],
            Response::HTTP_SEE_OTHER
        );
    }

    private function validerIdentiteClient(
        FormInterface $form,
        Clients $client
    ): void {
        if (
            $client->isB2B()
            && trim((string) $client->getRaisonSociale()) === ''
        ) {
            $form->get('raisonSociale')->addError(
                new FormError(
                    'La raison sociale est obligatoire pour un client B2B.'
                )
            );
        }

        if (
            $client->isB2C()
            && trim((string) $client->getNom()) === ''
            && trim((string) $client->getPrenom()) === ''
        ) {
            $form->get('nom')->addError(
                new FormError(
                    'Indiquez au moins le nom ou le prénom du client.'
                )
            );
        }
    }

    private function getFormErrors(
        FormInterface $form
    ): array {
        $errors = [];

        foreach ($form->getErrors(true) as $error) {
            $origine = $error->getOrigin();

            $champ = $origine !== null
                ? $origine->getName()
                : 'formulaire';

            $errors[$champ][] = $error->getMessage();
        }

        return $errors;
    }
    #[Route(
        '/datatable',
        name: 'app_clients_datatable',
        methods: ['GET']
    )]
    public function datatable(
        Request $request,
        ClientsRepository $clientsRepository
    ): JsonResponse {
        $draw = max(
            0,
            $request->query->getInt('draw')
        );

        $start = max(
            0,
            $request->query->getInt('start')
        );

        $length = $request->query->getInt('length', 10);

        if (!in_array($length, [10, 25, 50, 100], true)) {
            $length = 10;
        }

        $searchData = $request->query->all('search');
        $search = trim((string) ($searchData['value'] ?? ''));

        $resultat = $clientsRepository->rechercherPourDataTable(
            $start,
            $length,
            $search
        );

        $data = [];

        foreach ($resultat['clients'] as $client) {
            $nomClient = trim(
                (string) (
                    $client->getRaisonSociale()
                    ?: $client->getPrenom() . ' ' . $client->getNom()
                )
            );

            $data[] = [
                'id' => $client->getId(),
                'code' => $client->getCode(),
                'client' => $nomClient ?: '-',
                'typeClient' => $client->getTypeClient(),
                'telephone' => $client->getTelephone() ?: '-',
                'telephone2' => $client->getTelephone2(),
                'email' => $client->getEmail() ?: '-',
                'ville' => $client->getVille() ?: '-',
                'nif' => $client->getNif() ?: '-',
                'rccm' => $client->getRccm() ?: '-',
                'plafondCredit' => $client->getPlafondCredit(),
                'statut' => $client->isStatut(),
                'createdAt' => $client->getCreatedAt()
                    ? $client->getCreatedAt()->format('d/m/Y H:i')
                    : '-',

                'showUrl' => $this->generateUrl(
                    'app_clients_show',
                    [
                        'publicId' =>
                        $client->getPublicId()
                            ->toRfc4122(),
                    ]
                ),

                'editFormUrl' => $this->generateUrl(
                    'app_clients_edit_form',
                    ['id' => $client->getId()]
                ),

                'toggleUrl' =>
                $this->isGranted('ROLE_ADMIN')
                    ? $this->generateUrl(
                        'app_clients_toggle_statut',
                        [
                            'id' => $client->getId(),
                        ]
                    )
                    : null,

                'toggleToken' =>
                $this->isGranted('ROLE_ADMIN')
                    ? $this->container
                    ->get('security.csrf.token_manager')
                    ->getToken(
                        'toggle_client_' . $client->getId()
                    )
                    ->getValue()
                    : null,
            ];
        }

        return $this->json([
            'draw' => $draw,
            'recordsTotal' => $resultat['total'],
            'recordsFiltered' => $resultat['filtered'],
            'data' => $data,
        ]);
    }
}
