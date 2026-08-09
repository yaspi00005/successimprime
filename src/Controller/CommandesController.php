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


    #[Route('/new', name: 'app_commandes_new', methods: ['GET', 'POST'])]
    public function new(
        Request $request,
        EntityManagerInterface $entityManager,
        CommandeDetailFichierRepository $fichierRepository
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
     * VALIDATION ET SYNCHRONISATION DES DONNÉES
     * ============================================================
     */
        if (
            $form->isSubmitted()
            && $form->isValid()
        ) {
            try {
                /*
             * Sécurise :
             * - configurations
             * - dimensions
             * - prix
             * - finitions
             * - modes de calcul
             */
                $this->synchroniserDetailsEtFinitions(
                    $commande,
                    $form,
                    $entityManager
                );

                /*
             * Rattache les fichiers téléchargés
             * à chaque ligne de commande.
             */
                $this->rattacherFichiers(
                    $commande,
                    $fichierRepository
                );
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
     *
     * isValid() est volontairement vérifié une seconde fois,
     * car une erreur métier peut avoir été ajoutée ci-dessus.
     */
        if (
            $form->isSubmitted()
            && $form->isValid()
        ) {
            $maintenant = new \DateTimeImmutable();

            /*
         * Date de commande.
         */
            $commande->setDateCommande(
                $maintenant
            );

            /*
         * Date de livraison théorique.
         */
            $commande->setDateLivraison(
                $this->ajouterHeuresOuvrees(
                    $maintenant,
                    48
                )
            );

            /*
         * Utilisateur connecté.
         */
            $utilisateur = $this->getUser();

            if (!$utilisateur instanceof User) {
                throw $this->createAccessDeniedException(
                    'Vous devez être connecté pour enregistrer une commande.'
                );
            }

            $commande->setAgents(
                $utilisateur
            );

            /*
         * ========================================================
         * ROUTAGE MÉTIER DES LIGNES
         * ========================================================
         *
         * Important :
         * seulement si la commande est déjà validée.
         *
         * Une commande brouillon ne doit encore apparaître
         * ni en prépresse, ni en production, ni en livraison.
         */
            if ($this->commandeEstValidee($commande)) {
                $this->preparerCircuitCommande(
                    $commande
                );
            }

            /*
         * ========================================================
         * PREMIER ENREGISTREMENT
         * ========================================================
         *
         * Permet d'obtenir l'identifiant de la commande.
         */
            $entityManager->persist(
                $commande
            );

            $entityManager->flush();

            /*
         * Génération du numéro après obtention de l'ID.
         */
            $commande->setNumero(
                sprintf(
                    'CMD-%06d-%s',
                    $commande->getId(),
                    $maintenant->format('m-Y')
                )
            );

            $entityManager->flush();

            /*
         * ========================================================
         * MESSAGE
         * ========================================================
         */
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
                    'id' => $commande->getId(),
                ]
            );
        }

        /*
     * ============================================================
     * AFFICHAGE
     * ============================================================
     */
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
        CommandeDetailFichierRepository $fichierRepository
    ): Response {
        $form = $this->createForm(CommandesType::class, $commande);
        $form->handleRequest($request);

        if ($form->isSubmitted() && $form->isValid()) {
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
            } catch (\DomainException | \RuntimeException $exception) {
                $form->addError(
                    new FormError($exception->getMessage())
                );
            }
        }

        if ($form->isSubmitted() && $form->isValid()) {
            $entityManager->flush();

            $this->addFlash(
                'success',
                'La commande a été modifiée avec succès.'
            );

            return $this->redirectToRoute(
                'app_commandes_show',
                ['id' => $commande->getId()],
                Response::HTTP_SEE_OTHER
            );
        }

        return $this->render('commandes/edit.html.twig', [
            'commande' => $commande,
            'form' => $form,
        ]);
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
        $detailsForm = $form->get('commandesDetails');

        foreach ($detailsForm as $detailForm) {
            $detail = $detailForm->getData();

            if (!$detail instanceof CommandesDetails) {
                continue;
            }

            if ($detail->isConfigurationAutomatique()) {
                $this->synchroniserDetailAutomatique(
                    $detail,
                    $detailForm,
                    $entityManager
                );
            } elseif ($detail->isConfigurationManuelle()) {
                $this->synchroniserDetailManuel(
                    $detail,
                    $detailForm,
                    $entityManager
                );
            } elseif ($detail->isSaisieLibre()) {
                $this->synchroniserDetailLibre(
                    $detail,
                    $entityManager
                );
            } else {
                throw new \DomainException(
                    'Le mode de saisie du travail est invalide.'
                );
            }

            $detail->calculerTotaux(false);
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
}
