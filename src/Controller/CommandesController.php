<?php

namespace App\Controller;

use App\Entity\Commandes;
use App\Entity\Paiements;
use App\Entity\User;
use App\Form\CommandesType;
use App\Form\PaiementsType;
use App\Repository\CommandesRepository;
use App\Repository\ClientsRepository;
use App\Repository\CommandeDetailFichierRepository;
use Doctrine\ORM\EntityManagerInterface;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;
use App\Entity\CommandeDetailFinition;
use App\Entity\ProduitConfigurationFinition;
use Symfony\Component\Form\FormError;
use Symfony\Component\Form\FormInterface;
use App\Entity\CommandesDetails;
use App\Service\StockService;


#[Route('/commandes')]
final class CommandesController extends AbstractController
{
    #[Route('/', name: 'app_commandes_index', methods: ['GET'])]
    public function index(
        Request $request,
        CommandesRepository $commandesRepository,
        ClientsRepository $clientsRepository
    ): Response {
        $filtres = [
            'q' => trim((string) $request->query->get('q', '')),
            'client' => (string) $request->query->get('client', ''),
            'statut' => (string) $request->query->get('statut', ''),
            'etat' => (string) $request->query->get('etat', ''),
            'paiement' => (string) $request->query->get('paiement', ''),
            'date_debut' => (string) $request->query->get('date_debut', ''),
            'date_fin' => (string) $request->query->get('date_fin', ''),
            'montant_min' => (string) $request->query->get('montant_min', ''),
            'montant_max' => (string) $request->query->get('montant_max', ''),
            'affichage' => (string) $request->query->get(
                'affichage',
                'actives'
            ),
            'tri' => (string) $request->query->get('tri', 'recent'),
        ];

        /*
         * Sans filtre, le repository affiche uniquement les commandes
         * dont le paiement est en attente OU les travaux sont en cours.
         */
        $commandes = $commandesRepository->rechercherPourIndex($filtres);

        $totalPaye = 0;
        $totalReste = 0;
        $totalCommandes = 0;

        foreach ($commandes as $commande) {
            $total = (int) ($commande->getTotalTtc() ?? 0);
            $paye = (int) ($commande->getMontantApayer() ?? 0);

            $totalCommandes += $total;
            $totalPaye += $paye;
            $totalReste += max(0, $total - $paye);
        }

        return $this->render('commandes/index.html.twig', [
            'commandes' => $commandes,
            'clients' => $clientsRepository->findBy([], [
                'nom' => 'ASC',
            ]),
            'filtres' => $filtres,
            'totalCommandes' => $totalCommandes,
            'totalPaye' => $totalPaye,
            'totalReste' => $totalReste,
        ]);
    }


    #[Route(
        '/new',
        name: 'app_commandes_new',
        methods: ['GET', 'POST']
    )]
    public function new(
        Request $request,
        EntityManagerInterface $entityManager,
        CommandeDetailFichierRepository $fichierRepository,
        StockService $stockService
    ): Response {
        $commande = new Commandes();

        $form = $this->createForm(
            CommandesType::class,
            $commande
        );

        $form->handleRequest($request);

        /*
     * ============================================================
     * PREMIÈRE PHASE :
     * VALIDATION / SYNCHRONISATION / CONTRÔLE STOCK
     * ============================================================
     */
        if (
            $form->isSubmitted()
            && $form->isValid()
        ) {
            try {
                $this->synchroniserDetailsEtFinitions(
                    $commande,
                    $form,
                    $entityManager
                );

                $this->rattacherFichiers(
                    $commande,
                    $fichierRepository
                );

                /*
             * Contrôle du stock uniquement si
             * la commande est validée.
             */
            } catch (
                \DomainException |
                \RuntimeException $exception
            ) {
                $form->addError(
                    new FormError(
                        $exception->getMessage()
                    )
                );
            }
        }

        /*
     * ============================================================
     * DEUXIÈME PHASE :
     * ENREGISTREMENT
     * ============================================================
     */
        if (
            $form->isSubmitted()
            && $form->isValid()
        ) {
            try {
                $maintenant =
                    new \DateTimeImmutable();

                $commande->setDateCommande(
                    $maintenant
                );

                $commande->setDateLivraison(
                    $this->ajouterHeuresOuvrees(
                        $maintenant,
                        48
                    )
                );

                $utilisateur =
                    $this->getUser();

                if (
                    !$utilisateur
                        instanceof User
                ) {
                    throw $this
                        ->createAccessDeniedException(
                            'Vous devez être connecté pour enregistrer une commande.'
                        );
                }

                $commande->setAgents(
                    $utilisateur
                );

                /*
             * ====================================================
             * ROUTAGE MÉTIER
             * ====================================================
             */
                if (
                    $this->commandeEstValidee(
                        $commande
                    )
                ) {
                    $this->preparerCircuitCommande(
                        $commande
                    );
                }

                /*
             * ====================================================
             * PREMIER PERSIST
             * ====================================================
             *
             * Nécessaire pour que les détails de commande
             * soient gérés par Doctrine avant création des
             * réservations.
             */
                $entityManager->persist(
                    $commande
                );

                /*
             * ====================================================
             * RÉSERVATION DU STOCK
             * ====================================================
             *
             * Aucune réservation pour un brouillon.
             */
                if (
                    $this->commandeEstValidee(
                        $commande
                    )
                ) {
                    $stockService
                        ->reserverPourCommande(
                            $commande
                        );
                }

                /*
             * Commande + détails + réservations
             * sont enregistrés ensemble.
             */
                $entityManager->flush();

                /*
             * ====================================================
             * NUMÉRO DE COMMANDE
             * ====================================================
             */
                $commande->setNumero(
                    sprintf(
                        'CMD-%06d-%s',
                        $commande->getId(),
                        $maintenant->format(
                            'm-Y'
                        )
                    )
                );

                $entityManager->flush();

                $this->addFlash(
                    'success',
                    sprintf(
                        'La commande %s a été enregistrée avec succès.',
                        $commande->getNumero()
                    )
                );

                return $this->redirectToRoute(
                    'app_commandes_show',
                    [
                        'id' =>
                        $commande->getId(),
                    ]
                );
            } catch (
                \DomainException |
                \RuntimeException $exception
            ) {
                /*
             * Si la réservation échoue à ce stade,
             * aucun enregistrement ne doit continuer.
             */
                $form->addError(
                    new FormError(
                        $exception->getMessage()
                    )
                );
            }
        }

        return $this->render(
            'commandes/new.html.twig',
            [
                'commande' => $commande,
                'form' => $form,
            ]
        );
    }

    #[Route('/{id}', name: 'app_commandes_show', methods: ['GET'])]
    public function show(Commandes $commande): Response
    {
        return $this->render('commandes/show.html.twig', [
            'commande' => $commande,
        ]);
    }

    #[Route(
        '/{id}/edit',
        name: 'app_commandes_edit',
        methods: ['GET', 'POST']
    )]
    public function edit(
        Request $request,
        Commandes $commande,
        EntityManagerInterface $entityManager,
        CommandeDetailFichierRepository $fichierRepository,
        StockService $stockService
    ): Response {
        /*
     * État AVANT modification du formulaire.
     */
        $commandeEtaitValidee =
            $this->commandeEstValidee(
                $commande
            );

        $circuitDejaCommence =
            $this->commandeACommenceSonCircuit(
                $commande
            );
        $commandeEtaitValidee =
            $this->commandeEstValidee(
                $commande
            );

        $circuitDejaCommence =
            $this->commandeACommenceSonCircuit(
                $commande
            );

        $empreinteDetailsAvant =
            $this->creerEmpreinteDetails(
                $commande
            );
        $form = $this->createForm(
            CommandesType::class,
            $commande
        );

        $form->handleRequest(
            $request
        );

        if (
            $form->isSubmitted()
            && $circuitDejaCommence
        ) {
            $detailsSoumis = $request->request->all(
                $form->getName()
            )['commandesDetails'] ?? null;

            if ($detailsSoumis !== null) {
                $form->addError(
                    new FormError(
                        'Les lignes de cette commande ne peuvent plus être modifiées car la production ou la livraison a déjà commencé.'
                    )
                );
            }
        }
        /*
     * ============================================================
     * PREMIÈRE PHASE :
     * SYNCHRONISATION / CONTRÔLE
     * ============================================================
     */
        if (
            $form->isSubmitted()
            && $form->isValid()
        ) {
            try {
                if ($circuitDejaCommence) {
                    $this->verifierModificationStructurelleAutorisee(
                        $commande
                    );
                }
                $empreinteDetailsApres =
                    $this->creerEmpreinteDetails(
                        $commande
                    );

                if (
                    $circuitDejaCommence
                    && $empreinteDetailsAvant
                    !== $empreinteDetailsApres
                ) {
                    throw new \DomainException(
                        'Impossible de modifier les lignes de cette commande : '
                            . 'la production ou la livraison a déjà commencé.'
                    );
                }
                $this->synchroniserDetailsEtFinitions(
                    $commande,
                    $form,
                    $entityManager
                );

                $this->rattacherFichiers(
                    $commande,
                    $fichierRepository
                );

                if (
                    $this->commandeEstValidee(
                        $commande
                    )
                ) {
                    /*
                 * Attention :
                 * verifierStockCommande() utilise actuellement
                 * le stock physique.
                 *
                 * La vraie vérification tenant compte des
                 * réservations est également faite ensuite par
                 * reserverPourCommande().
                 */
                }
            } catch (
                \DomainException |
                \RuntimeException $exception
            ) {
                $form->addError(
                    new FormError(
                        $exception->getMessage()
                    )
                );
            }
        }

        /*
 * ============================================================
 * DEUXIÈME PHASE :
 * ENREGISTREMENT
 * ============================================================
 */
        if (
            $form->isSubmitted()
            && $form->isValid()
        ) {
            try {
                $commandeEstValideeMaintenant =
                    $this->commandeEstValidee(
                        $commande
                    );

                /*
         * ========================================================
         * CAS 1 :
         * BROUILLON → VALIDÉE
         * ========================================================
         */
                if (
                    !$commandeEtaitValidee
                    && $commandeEstValideeMaintenant
                ) {
                    /*
             * Entrée initiale dans le circuit.
             */
                    $this->preparerCircuitCommande(
                        $commande
                    );

                    /*
             * Réservation du stock.
             */
                    $stockService
                        ->reserverPourCommande(
                            $commande
                        );
                }

                /*
         * ========================================================
         * CAS 2 :
         * VALIDÉE → VALIDÉE
         * ========================================================
         */ elseif (
                    $commandeEtaitValidee
                    && $commandeEstValideeMaintenant
                ) {
                    /*
             * Tant que le circuit métier n'a pas commencé,
             * on autorise encore la modification et le
             * recalcul des réservations.
             */
                    if (!$circuitDejaCommence) {
                        $stockService
                            ->reserverPourCommande(
                                $commande
                            );
                    }

                    /*
             * Si production/livraison a commencé,
             * on NE réinitialise surtout pas les statuts
             * avec preparerCircuitCommande().
             *
             * Et on ne recrée pas non plus les réservations.
             */
                }

                /*
         * ========================================================
         * CAS 3 :
         * VALIDÉE → BROUILLON
         * ========================================================
         */ elseif (
                    $commandeEtaitValidee
                    && !$commandeEstValideeMaintenant
                ) {
                    if ($circuitDejaCommence) {
                        throw new \DomainException(
                            'Cette commande a déjà commencé son circuit de production ou de livraison. Elle ne peut plus être repassée en brouillon.'
                        );
                    }

                    /*
             * Aucune production/livraison n'a commencé :
             * les réservations peuvent être libérées.
             */
                    $stockService
                        ->libererReservationsCommande(
                            $commande
                        );
                }

                /*
         * ========================================================
         * CAS 4 :
         * BROUILLON → BROUILLON
         * ========================================================
         *
         * Rien à faire concernant le stock ou le circuit.
         */

                $entityManager->flush();

                $this->addFlash(
                    'success',
                    'La commande a été modifiée avec succès.'
                );

                return $this->redirectToRoute(
                    'app_commandes_show',
                    [
                        'id' =>
                        $commande->getId(),
                    ],
                    Response::HTTP_SEE_OTHER
                );
            } catch (
                \DomainException |
                \RuntimeException |
                \LogicException $exception
            ) {
                $form->addError(
                    new FormError(
                        $exception->getMessage()
                    )
                );
            }
        }

        return $this->render(
            'commandes/edit.html.twig',
            [
                'commande' =>
                $commande,

                'form' =>
                $form,

                'circuitDejaCommence' =>
                $circuitDejaCommence,
            ]
        );
    }

    #[Route('/{id}', name: 'app_commandes_delete', methods: ['POST'])]
    public function delete(Request $request, Commandes $commande, EntityManagerInterface $entityManager): Response
    {
        if ($this->isCsrfTokenValid('delete' . $commande->getId(), $request->getPayload()->getString('_token'))) {
            $entityManager->remove($commande);
            $entityManager->flush();
        }

        return $this->redirectToRoute('app_commandes_index', [], Response::HTTP_SEE_OTHER);
    }

    private function rattacherFichiers(
        Commandes $commande,
        CommandeDetailFichierRepository $fichierRepository
    ): void {
        foreach ($commande->getCommandesDetails() as $detail) {
            $valeurJetons = trim(
                (string) $detail->getJetonsFichiers()
            );

            if ($valeurJetons === '') {
                continue;
            }

            $jetons = array_values(
                array_unique(
                    array_filter(
                        array_map(
                            'trim',
                            explode(',', $valeurJetons)
                        )
                    )
                )
            );

            foreach ($jetons as $jeton) {
                if (!preg_match('/^[a-f0-9]{64}$/', $jeton)) {
                    throw new \RuntimeException(
                        'Un jeton de fichier est invalide.'
                    );
                }

                $fichier = $fichierRepository->findOneBy([
                    'jetonUpload' => $jeton,
                    'statut' => 'TERMINE',
                ]);

                if ($fichier === null) {
                    throw new \RuntimeException(
                        sprintf(
                            'Le fichier correspondant au jeton %s est introuvable ou incomplet.',
                            $jeton
                        )
                    );
                }

                $detailActuel = $fichier->getCommandeDetail();

                if (
                    $detailActuel !== null
                    && $detailActuel !== $detail
                ) {
                    throw new \RuntimeException(
                        'Ce fichier est déjà rattaché à un autre travail.'
                    );
                }

                $detail->addFichier($fichier);
            }

            // Évite de retraiter les mêmes jetons lors d’une modification.
            $detail->setJetonsFichiers('');
        }
    }


    private function convertirDimension(
        int|float|string|null $valeur
    ): ?float {
        if ($valeur === null) {
            return null;
        }

        $valeurNormalisee = str_replace(
            ',',
            '.',
            trim((string) $valeur)
        );

        if (
            $valeurNormalisee === ''
            || !is_numeric($valeurNormalisee)
        ) {
            return null;
        }

        return max(
            0.0,
            (float) $valeurNormalisee
        );
    }
    private function ajouterHeuresOuvrees(
        \DateTimeImmutable $dateDepart,
        int $heures
    ): \DateTimeImmutable {
        $date = $dateDepart;
        $heuresRestantes = $heures;

        while ($heuresRestantes > 0) {
            $date = $date->modify('+1 hour');

            // 7 = dimanche : aucune heure n’est comptabilisée
            if ((int) $date->format('N') !== 7) {
                --$heuresRestantes;
            }
        }

        return $date;
    }

    private function synchroniserDetailsEtFinitions(
    Commandes $commande,
    FormInterface $form,
    EntityManagerInterface $entityManager
): void {
    $detailsForm =
        $form->get('commandesDetails');

    foreach ($detailsForm as $detailForm) {
        $detail =
            $detailForm->getData();

        if (
            !$detail instanceof CommandesDetails
        ) {
            continue;
        }

        /*
         * ====================================================
         * TYPE : ARTICLE EN STOCK
         * ====================================================
         *
         * Vente directe d'un article physique.
         * Aucun produit, aucune configuration,
         * aucun prépresse, aucune production.
         */
        if (
            $detail->getTypeLigne()
            === CommandesDetails::TYPE_ARTICLE
        ) {
            $article =
                $detail->getArticle();

            if ($article === null) {
                throw new \DomainException(
                    sprintf(
                        'Veuillez sélectionner un article pour la ligne « %s ».',
                        $detail->getDesignation()
                        ?: 'Article en stock'
                    )
                );
            }

            if (
                method_exists(
                    $article,
                    'isActif'
                )
                && !$article->isActif()
            ) {
                throw new \DomainException(
                    sprintf(
                        'L’article « %s » est désactivé.',
                        $article->getDesignation()
                    )
                );
            }

            if (
                method_exists(
                    $article,
                    'isVendable'
                )
                && !$article->isVendable()
            ) {
                throw new \DomainException(
                    sprintf(
                        'L’article « %s » n’est pas autorisé à la vente directe.',
                        $article->getDesignation()
                    )
                );
            }

            /*
             * Nettoyage de toutes les informations
             * propres à une ligne Produit.
             */
            $detail->setProduit(null);

            $detail->setProduitConfiguration(
                null
            );

            $detail->setTypeImpression(null);

            $detail->setSupport(null);

            $detail->setFormat(null);

            /*
             * Pas de traitement technique.
             */
            $detail->setPrePresseNecessaire(
                false
            );

            $detail->setProductionNecessaire(
                false
            );

            /*
             * Vente directe = calcul par quantité/unité.
             *
             * Garde cette ligne seulement si ton setter existe.
             */
            if (
                method_exists(
                    $detail,
                    'setModeCalcul'
                )
            ) {
                $detail->setModeCalcul(
                    'unite'
                );
            }

            /*
             * Si aucune désignation n'est saisie,
             * on utilise celle de l'article.
             */
            if (
                trim(
                    (string)
                    $detail->getDesignation()
                ) === ''
            ) {
                $detail->setDesignation(
                    $article->getDesignation()
                );
            }

            /*
             * Pas de synchronisation ProduitConfiguration
             * pour une vente directe d'article.
             */

            $detail->calculerTotaux(
                false
            );

            continue;
        }


        /*
         * ====================================================
         * TYPE : SAISIE LIBRE
         * ====================================================
         */
        if (
            $detail->getTypeLigne()
            === CommandesDetails::TYPE_LIBRE
        ) {
            /*
             * Une ligne libre ne doit être reliée
             * ni à un article, ni à un produit.
             */
            $detail->setArticle(null);

            $detail->setProduit(null);

            $detail->setProduitConfiguration(
                null
            );

            $detail->setTypeImpression(null);

            $detail->setSupport(null);

            $detail->setFormat(null);

            /*
             * Par défaut :
             * livraison directe.
             */
            $detail->setPrePresseNecessaire(
                false
            );

            $detail->setProductionNecessaire(
                false
            );

            $this->synchroniserDetailLibre(
                $detail,
                $entityManager
            );

            $detail->calculerTotaux(
                false
            );

            continue;
        }


        /*
         * ====================================================
         * TYPE : PRODUIT / PRESTATION
         * ====================================================
         */
        if (
            $detail->getTypeLigne()
            !== CommandesDetails::TYPE_PRODUIT
        ) {
            throw new \DomainException(
                'Le type de ligne du travail est invalide.'
            );
        }

        /*
         * Une ligne Produit ne doit pas conserver
         * un Article de vente directe.
         */
        $detail->setArticle(null);


        /*
         * ====================================================
         * MODE DE CONFIGURATION DU PRODUIT
         * ====================================================
         */
        if (
            $detail->isConfigurationAutomatique()
        ) {
            $this->synchroniserDetailAutomatique(
                $detail,
                $detailForm,
                $entityManager
            );
        } elseif (
            $detail->isConfigurationManuelle()
        ) {
            $this->synchroniserDetailManuel(
                $detail,
                $detailForm,
                $entityManager
            );
        } elseif (
            $detail->isSaisieLibre()
        ) {
            /*
             * Compatibilité temporaire avec ton ancien
             * modeConfiguration = libre.
             *
             * À terme, TYPE_LIBRE suffit et cette branche
             * pourra être retirée.
             */
            $this->synchroniserDetailLibre(
                $detail,
                $entityManager
            );
        } else {
            throw new \DomainException(
                'Le mode de saisie du travail est invalide.'
            );
        }

        $detail->calculerTotaux(
            false
        );
    }
}


    private function synchroniserDetailAutomatique(
        CommandesDetails $detail,
        FormInterface $detailForm,
        EntityManagerInterface $entityManager
    ): void {
        $configuration = $detail->getProduitConfiguration();

        if ($configuration === null) {
            throw new \DomainException(
                'Veuillez sélectionner une configuration de produit.'
            );
        }

        if (!$configuration->isActive()) {
            throw new \DomainException(
                'La configuration sélectionnée est inactive.'
            );
        }

        /*
     * Les choix faits dans finitionsSelectionnees.
     */
        $finitionsSelectionnees = [];

        if ($detailForm->has('finitionsSelectionnees')) {
            $valeurs = $detailForm
                ->get('finitionsSelectionnees')
                ->getData();

            if (is_iterable($valeurs)) {
                foreach ($valeurs as $configurationFinition) {
                    if (
                        $configurationFinition
                        instanceof ProduitConfigurationFinition
                    ) {
                        $finitionsSelectionnees[$configurationFinition->getId()] = $configurationFinition;
                    }
                }
            }
        }

        /*
     * Ajoute automatiquement les finitions obligatoires,
     * même si leur case n’a pas été cochée.
     */
        foreach (
            $configuration->getConfigurationFinitions()
            as $configurationFinition
        ) {
            if (!$configurationFinition->isActive()) {
                continue;
            }

            if ($configurationFinition->isObligatoire()) {
                $finitionsSelectionnees[$configurationFinition->getId()] = $configurationFinition;
            }
        }

        /*
     * Supprime les anciennes finitions du détail.
     */
        foreach ($detail->getFinitions()->toArray() as $ancienneFinition) {
            $detail->removeFinition($ancienneFinition);

            if ($ancienneFinition->getId() !== null) {
                $entityManager->remove($ancienneFinition);
            }
        }

        $quantiteDetail = max(
            1,
            (int) ($detail->getQuantite() ?? 1)
        );

        foreach (
            $finitionsSelectionnees
            as $configurationFinition
        ) {
            /*
         * Vérifie que la finition appartient réellement
         * à la configuration sélectionnée.
         */
            if (
                $configurationFinition
                ->getProduitConfiguration()
                !== $configuration
            ) {
                throw new \DomainException(
                    'Une finition sélectionnée ne correspond pas '
                        . 'à la configuration du produit.'
                );
            }

            if (!$configurationFinition->isActive()) {
                continue;
            }

            $prix = (int) (
                $configurationFinition->getPrix() ?? 0
            );

            $modeCalcul = (string) (
                $configurationFinition->getModeCalcul()
                ?: 'forfait'
            );

            $quantiteFinition = match ($modeCalcul) {
                'forfait' => 1,

                'unite',
                'exemplaire',
                'feuille',
                'face',
                'point' => $quantiteDetail,

                default => $quantiteDetail,
            };

            $montant = $modeCalcul === 'forfait'
                ? $prix
                : $prix * $quantiteFinition;

            $finition = new CommandeDetailFinition();

            $finition->setConfigurationFinition(
                $configurationFinition
            );

            /*
         * Nécessaire si CommandeDetailFinition possède aussi
         * une relation directe vers Finition.
         */
            $finition->setFinition(
                $configurationFinition->getFinition()
            );

            $finition->setPrixApplique($prix);
            $finition->setModeCalcul($modeCalcul);
            $finition->setQuantite($quantiteFinition);
            $finition->setMontant($montant);

            $detail->addFinition($finition);
        }
    }
    private function synchroniserDetailManuel(
        CommandesDetails $detail,
        FormInterface $detailForm,
        EntityManagerInterface $entityManager
    ): void {
        foreach ($detail->getFinitions() as $finition) {
            if ($finition->getFinition() === null) {
                throw new \DomainException(
                    'Veuillez sélectionner la finition manuelle.'
                );
            }

            $prix = max(
                0,
                (int) ($finition->getPrixApplique() ?? 0)
            );

            $quantite = max(
                1,
                (int) ($finition->getQuantite() ?? 1)
            );

            $modeCalcul = $finition->getModeCalcul()
                ?: 'forfait';

            $montant = $modeCalcul === 'forfait'
                ? $prix
                : $prix * $quantite;

            $finition->setPrixApplique($prix);
            $finition->setQuantite($quantite);
            $finition->setModeCalcul($modeCalcul);
            $finition->setMontant($montant);
        }
    }

    private function synchroniserDetailLibre(
        CommandesDetails $detail,
        EntityManagerInterface $entityManager
    ): void {
        if (trim((string) $detail->getDesignation()) === '') {
            throw new \DomainException(
                'La désignation de la saisie libre est obligatoire.'
            );
        }

        if ((int) $detail->getQuantite() < 1) {
            throw new \DomainException(
                'La quantité doit être supérieure à zéro.'
            );
        }

        if ((int) $detail->getPrixUnitaire() < 0) {
            throw new \DomainException(
                'Le prix unitaire ne peut pas être négatif.'
            );
        }

        /*
     * Une saisie libre ne dépend pas d’une configuration.
     */
        $detail->setProduitConfiguration(null);

        foreach ($detail->getFinitions()->toArray() as $finition) {
            $detail->removeFinition($finition);

            if ($finition->getId() !== null) {
                $entityManager->remove($finition);
            }
        }
    }
    #[Route(
        '/{id}/ajuster-livraison',
        name: 'app_commandes_ajuster_livraison',
        methods: ['POST']
    )]
    public function ajusterLivraison(
        Request $request,
        Commandes $commande,
        EntityManagerInterface $entityManager
    ): Response {
        $this->denyAccessUnlessGranted('ROLE_PRODUCTION');

        if (!$this->isCsrfTokenValid(
            'ajuster-livraison-' . $commande->getId(),
            (string) $request->request->get('_token')
        )) {
            throw $this->createAccessDeniedException(
                'Jeton de sécurité invalide.'
            );
        }

        $dateSaisie = $request->request->get('dateLivraison');

        if (!$dateSaisie) {
            $this->addFlash('error', 'La nouvelle date est obligatoire.');

            return $this->redirectToRoute('app_commandes_show', [
                'id' => $commande->getId(),
            ]);
        }

        try {
            $nouvelleDate = new \DateTimeImmutable($dateSaisie);
        } catch (\Throwable) {
            $this->addFlash('error', 'La date de livraison est invalide.');

            return $this->redirectToRoute('app_commandes_show', [
                'id' => $commande->getId(),
            ]);
        }

        if ($nouvelleDate <= new \DateTimeImmutable()) {
            $this->addFlash(
                'error',
                'La date de livraison doit être postérieure à maintenant.'
            );

            return $this->redirectToRoute('app_commandes_show', [
                'id' => $commande->getId(),
            ]);
        }

        $commande->setDateLivraison($nouvelleDate);
        $entityManager->flush();

        $this->addFlash(
            'success',
            'Le délai de livraison a été ajusté.'
        );

        return $this->redirectToRoute('app_commandes_show', [
            'id' => $commande->getId(),
        ]);
    }
    #[Route(
        '/{id}/paiement',
        name: 'app_commandes_paiement',
        methods: ['GET', 'POST']
    )]
    public function paiement(
        Commandes $commande,
        Request $request,
        EntityManagerInterface $entityManager
    ): Response {
        $user = $this->getUser();

        if (!$user instanceof User) {
            throw $this->createAccessDeniedException(
                'Vous devez être connecté pour enregistrer un paiement.'
            );
        }

        $resteAPayer = $commande->getResteAPayer();

        if ($resteAPayer <= 0) {
            $this->addFlash(
                'warning',
                'Cette commande est déjà entièrement payée.'
            );

            return $this->redirectToRoute('app_commandes_show', [
                'id' => $commande->getId(),
            ]);
        }

        $paiement = new Paiements();
        $paiement->setCommande($commande);
        $paiement->setEncaissePar($user);
        $paiement->setDate(new \DateTimeImmutable());

        $form = $this->createForm(PaiementsType::class, $paiement);
        $form->handleRequest($request);

        if ($form->isSubmitted() && $form->isValid()) {
            $montant = (int) $paiement->getMontant();

            // Recalcul effectué avant l’ajout du nouveau paiement.
            $resteAvantPaiement = $commande->getResteAPayer();

            if ($montant <= 0) {
                $form->get('montant')->addError(
                    new FormError(
                        'Le montant doit être supérieur à zéro.'
                    )
                );
            } elseif ($montant > $resteAvantPaiement) {
                $form->get('montant')->addError(
                    new FormError(
                        'Le montant dépasse le reste à payer.'
                    )
                );
            } else {
                /*
             * addPaiement() établit également la relation
             * Paiement -> Commande.
             */
                $commande->addPaiement($paiement);

                $entityManager->persist($paiement);

                $commande = $paiement->getCommande();

                if ($commande === null) {
                    throw new \LogicException(
                        'Aucune commande n’est associée à ce paiement.'
                    );
                }

                $totalPaye = 0;

                foreach ($commande->getPaiements() as $paiementCommande) {
                    // Adapte le nom du getter si ton champ s’appelle autrement.
                    $totalPaye += (int) $paiementCommande->getMontant();
                }

                $totalCommande = (int) $commande->getTotalTtc();
                $resteAPayer = max(0, $totalCommande - $totalPaye);

                $commande->setTotalPaye($totalPaye);
                $commande->setResteAPayer($resteAPayer);

                $commande->setStatutPaiement(
                    $resteAPayer <= 0
                        ? Commandes::PAIEMENT_PAYE
                        : (
                            $totalPaye > 0
                            ? Commandes::PAIEMENT_PARTIEL
                            : Commandes::PAIEMENT_IMPAYE
                        )
                );

                $entityManager->persist($commande);
                $entityManager->flush();
                $entityManager->flush();

                $this->addFlash(
                    'success',
                    sprintf(
                        'Paiement de %s FCFA enregistré avec succès.',
                        number_format($montant, 0, ',', ' ')
                    )
                );

                return $this->redirectToRoute(
                    'app_commandes_show',
                    ['id' => $commande->getId()]
                );
            }
        }

        return $this->render('commandes/paiement.html.twig', [
            'commande' => $commande,
            'form' => $form->createView(),
            'totalPaye' => $commande->getTotalPaye(),
            'resteAPayer' => $commande->getResteAPayer(),
        ]);
    }


    private function commandeEstValidee(
        Commandes $commande
    ): bool {
        return $commande->isStatut();
    }


    private function preparerCircuitCommande(
        Commandes $commande
    ): void {
        foreach ($commande->getCommandesDetails() as $detail) {

            /*
         * Sécurité.
         */
            if (!$detail instanceof CommandesDetails) {
                continue;
            }

            /*
         * La ligne décide elle-même de son premier statut
         * selon son circuit.
         */
            $detail->preparerApresValidationCommande();
            dump([
                'apres' => $detail->getStatutProduction(),
            ]);
        }
    }
    private function commandeACommenceSonCircuit(
        Commandes $commande
    ): bool {
        foreach (
            $commande->getCommandesDetails()
            as $detail
        ) {
            if (!$detail instanceof CommandesDetails) {
                continue;
            }

            $statut =
                $detail->getStatutProduction();

            if (
                in_array(
                    $statut,
                    [
                        CommandesDetails::PRODUCTION_EN_COURS,
                        CommandesDetails::PRODUCTION_TERMINEE,
                        CommandesDetails::PRODUCTION_PRETE_LIVRAISON,
                        CommandesDetails::PRODUCTION_EN_LIVRAISON,
                        CommandesDetails::PRODUCTION_LIVREE,
                    ],
                    true
                )
            ) {
                return true;
            }

            if (
                method_exists(
                    $detail,
                    'getQuantiteLivree'
                )
                && (float) $detail->getQuantiteLivree() > 0
            ) {
                return true;
            }

            if (
                method_exists(
                    $detail,
                    'getProductionDebuteLe'
                )
                && $detail->getProductionDebuteLe() !== null
            ) {
                return true;
            }
        }

        return false;
    }

    private function verifierModificationStructurelleAutorisee(
        Commandes $commande
    ): void {
        if (
            !$this->commandeACommenceSonCircuit(
                $commande
            )
        ) {
            return;
        }

        throw new \DomainException(
            'Cette commande a déjà commencé son circuit de production ou de livraison. '
                . 'Les lignes ne peuvent plus être modifiées.'
        );
    }
    private function creerEmpreinteDetails(
        Commandes $commande
    ): string {
        $donnees = [];

        foreach (
            $commande->getCommandesDetails()
            as $detail
        ) {
            if (!$detail instanceof CommandesDetails) {
                continue;
            }

            $finitions = [];

            foreach (
                $detail->getFinitions()
                as $finition
            ) {
                $finitions[] = [
                    'id' =>
                    $finition->getId(),

                    'configuration' =>
                    $finition
                        ->getConfigurationFinition()
                        ?->getId(),

                    'quantite' =>
                    $finition->getQuantite(),

                    'prix' =>
                    $finition->getPrixApplique(),

                    'montant' =>
                    $finition->getMontant(),
                ];
            }

            $donnees[] = [
                'id' =>
                $detail->getId(),

                'produit' =>
                $detail->getProduit()
                    ?->getId(),

                'configuration' =>
                $detail
                    ->getProduitConfiguration()
                    ?->getId(),

                'designation' =>
                $detail->getDesignation(),

                'typeImpression' =>
                $detail->getTypeImpression()
                    ?->getId(),

                'support' =>
                $detail->getSupport()
                    ?->getId(),

                'format' =>
                $detail->getFormat()
                    ?->getId(),

                'largeur' =>
                $detail->getLargeur(),

                'longueur' =>
                $detail->getLongueur(),

                'surface' =>
                $detail->getSurface(),

                'quantite' =>
                $detail->getQuantite(),

                'prixUnitaire' =>
                $detail->getPrixUnitaire(),

                'productionNecessaire' =>
                $detail->isProductionNecessaire(),

                'prePresseNecessaire' =>
                $detail->isPrePresseNecessaire(),

                'finitions' =>
                $finitions,
            ];
        }

        return hash(
            'sha256',
            serialize($donnees)
        );
    }
}
