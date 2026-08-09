<?php

namespace App\Controller;

use App\Entity\Devis;
use App\Entity\DevisDetails;
use App\Entity\User;
use App\Service\DevisCommandeConverter;
use App\Entity\DevisDetailFinition;
use App\Entity\ProduitConfigurationFinition;
use App\Form\DevisType;
use App\Repository\DevisRepository;
use App\Repository\ClientsRepository;
use Doctrine\ORM\EntityManagerInterface;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\Form\FormError;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;
use App\Entity\Produits;
use App\Entity\ProduitConfiguration;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\Form\FormInterface;



#[Route('/devis', name: 'app_devis_')]
class DevisController extends AbstractController
{
    #[Route('/', name: 'index', methods: ['GET'])]
    public function index(
        Request $request,
        DevisRepository $devisRepository,
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
         * Sans filtre, le repository affiche uniquement les devis
         * dont le paiement est en attente OU les travaux sont en cours.
         */
        $devis = $devisRepository->rechercherPourIndex($filtres);

        $totalPaye = 0;
        $totalReste = 0;
        $totalDevis = 0;

        foreach ($devis as $devi) {
            $total = (int) ($devi->getTotalTtc() ?? 0);

            $paye = (int) ($devi->getMontantApayer() ?? 0);

            $totalDevis += $total;
            $totalPaye += $paye;
            $totalReste += max(0, $total - $paye);
        }

        return $this->render('devis/index.html.twig', [
            'devis' => $devis,
            'clients' => $clientsRepository->findBy([], [
                'nom' => 'ASC',
            ]),
            'filtres' => $filtres,
            'totalDevis' => $totalDevis,
            'totalPaye' => $totalPaye,
            'totalReste' => $totalReste,
        ]);
    }


    #[Route('/new', name: 'new', methods: ['GET', 'POST'])]
    public function new(
        Request $request,
        EntityManagerInterface $entityManager,
    ): Response {
        $devi = new Devis();

        $form = $this->createForm(DevisType::class, $devi);
        $form->handleRequest($request);

        if ($form->isSubmitted() && $form->isValid()) {
            try {
                /*
             * Sécurise les configurations, les dimensions,
             * les prix et synchronise les finitions.
             */


                $this->synchroniserDetailsEtFinitions(
                    $devi,
                    $form,
                    $entityManager
                );

              
            } catch (\DomainException | \RuntimeException $exception) {
                $form->addError(
                    new FormError($exception->getMessage())
                );
            }
        }

        /*
     * isValid() est vérifié une seconde fois, car une erreur
     * métier peut avoir été ajoutée ci-dessus.
     */
        if ($form->isSubmitted() && $form->isValid()) {
            $maintenant = new \DateTimeImmutable();

            $devi->setDateDevis($maintenant);
            ;

            $utilisateur = $this->getUser();

            if (!$utilisateur instanceof User) {
                throw $this->createAccessDeniedException(
                    'Vous devez être connecté pour enregistrer un devis.'
                );
            }

            $devi->setAgents($utilisateur);

            /*
         * Premier enregistrement pour obtenir l’identifiant.
         */
            $entityManager->persist($devi);
            $entityManager->flush();

            $devi->setNumero(sprintf(
                'DEV-%06d-%s',
                $devi->getId(),
                $maintenant->format('m-Y')
            ));

            $entityManager->flush();

            $this->addFlash(
                'success',
                sprintf(
                    'Le devis %s a été enregistré avec succès.',
                    $devi->getNumero()
                )
            );

            return $this->redirectToRoute('app_devis_show', [
                'id' => $devi->getId(),
            ]);
        }

        return $this->render('devis/new.html.twig', [
            'devi' => $devi,
            'form' => $form,
        ]);
    }

    #[Route('/{id}', name: 'show', methods: ['GET'])]
    public function show(Devis $devi): Response
    {
        return $this->render('devis/show.html.twig', [
            'devis' => $devi,
        ]);
    }

   #[Route(
    '/{id}/edit',
    name: 'edit',
    methods: ['GET', 'POST']
)]
public function edit(
    Request $request,
    Devis $devi,
    EntityManagerInterface $entityManager,
): Response {
    $form = $this->createForm(DevisType::class, $devi);
    $form->handleRequest($request);

    if ($form->isSubmitted() && $form->isValid()) {
        try {
            $this->synchroniserDetailsEtFinitions(
                $devi,
                $form,
                $entityManager
            );

            $entityManager->flush();

            $this->addFlash(
                'success',
                'Le devis a été modifié avec succès.'
            );

            return $this->redirectToRoute(
                'app_devis_show',
                ['id' => $devi->getId()],
                Response::HTTP_SEE_OTHER
            );
        } catch (\DomainException | \RuntimeException $exception) {
            $form->addError(
                new FormError($exception->getMessage())
            );
        } catch (\Doctrine\DBAL\Exception\UniqueConstraintViolationException) {
            $form->addError(
                new FormError(
                    'Une même finition ne peut pas être ajoutée deux fois au même détail.'
                )
            );
        }
    }

    return $this->render('devis/edit.html.twig', [
        'devi' => $devi,
        'form' => $form,
    ]);
}

    #[Route('/{id}', name: 'app_devis_delete', methods: ['POST'])]
    public function delete(Request $request, Devis $devi, EntityManagerInterface $entityManager): Response
    {
        if ($this->isCsrfTokenValid('delete' . $devi->getId(), $request->getPayload()->getString('_token'))) {
            $entityManager->remove($devi);
            $entityManager->flush();
        }

        return $this->redirectToRoute('app_devis_index', [], Response::HTTP_SEE_OTHER);
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
    

    private function synchroniserDetailsEtFinitions(
        Devis $devi,
        FormInterface $form,
        EntityManagerInterface $entityManager
    ): void {
        $detailsForm = $form->get('devisDetails');

        foreach ($detailsForm as $detailForm) {
            $detail = $detailForm->getData();

            if (!$detail instanceof DevisDetails) {
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
    DevisDetails $detail,
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
     * Liste des configurations de finition sélectionnées.
     * La clé correspond à l'identifiant de la configuration.
     */
    $finitionsSelectionnees = [];

    if ($detailForm->has('finitionsSelectionnees')) {
        $valeurs = $detailForm
            ->get('finitionsSelectionnees')
            ->getData();

        if (is_iterable($valeurs)) {
            foreach ($valeurs as $configurationFinition) {
                if (
                    !$configurationFinition
                    instanceof ProduitConfigurationFinition
                ) {
                    continue;
                }

                if ($configurationFinition->getId() === null) {
                    continue;
                }

                $finitionsSelectionnees[
                    $configurationFinition->getId()
                ] = $configurationFinition;
            }
        }
    }

    /*
     * Ajout automatique des finitions obligatoires.
     */
    foreach (
        $configuration->getConfigurationFinitions()
        as $configurationFinition
    ) {
        if (
            !$configurationFinition->isActive()
            || !$configurationFinition->isObligatoire()
            || $configurationFinition->getId() === null
        ) {
            continue;
        }

        $finitionsSelectionnees[
            $configurationFinition->getId()
        ] = $configurationFinition;
    }

    /*
     * Indexation des finitions déjà enregistrées.
     * Elles seront réutilisées au lieu d'être supprimées puis recréées.
     */
    $finitionsExistantes = [];

    foreach ($detail->getFinitions()->toArray() as $finitionExistante) {
        $configurationExistante = $finitionExistante
            ->getConfigurationFinition();

        $configurationId = $configurationExistante?->getId();

        /*
         * Une finition automatique doit avoir une configuration.
         */
        if ($configurationId === null) {
            $detail->removeFinition($finitionExistante);

            if ($finitionExistante->getId() !== null) {
                $entityManager->remove($finitionExistante);
            }

            continue;
        }

        /*
         * Protection contre un éventuel doublon déjà présent
         * dans la collection PHP.
         */
        if (isset($finitionsExistantes[$configurationId])) {
            $detail->removeFinition($finitionExistante);

            if ($finitionExistante->getId() !== null) {
                $entityManager->remove($finitionExistante);
            }

            continue;
        }

        $finitionsExistantes[$configurationId] = $finitionExistante;
    }

    /*
     * Suppression uniquement des finitions qui ne sont plus sélectionnées.
     */
    foreach (
        $finitionsExistantes
        as $configurationId => $finitionExistante
    ) {
        if (isset($finitionsSelectionnees[$configurationId])) {
            continue;
        }

        $detail->removeFinition($finitionExistante);

        if ($finitionExistante->getId() !== null) {
            $entityManager->remove($finitionExistante);
        }

        unset($finitionsExistantes[$configurationId]);
    }

    $quantiteDetail = max(
        1,
        (int) ($detail->getQuantite() ?? 1)
    );

    /*
     * Mise à jour des finitions existantes ou création des nouvelles.
     */
    foreach (
        $finitionsSelectionnees
        as $configurationId => $configurationFinition
    ) {
        if (
            $configurationFinition->getProduitConfiguration()
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

        $prix = max(
            0,
            (int) ($configurationFinition->getPrix() ?? 0)
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

        /*
         * Réutilisation de l'entité existante pendant l'édition.
         */
        $finition = $finitionsExistantes[$configurationId]
            ?? new DevisDetailFinition();

        $finition->setConfigurationFinition(
            $configurationFinition
        );

        $finition->setFinition(
            $configurationFinition->getFinition()
        );

        $finition->setPrixApplique($prix);
        $finition->setModeCalcul($modeCalcul);
        $finition->setQuantite($quantiteFinition);
        $finition->setMontant($montant);

        /*
         * addFinition() n'est appelée que pour une nouvelle entité.
         */
        if (!$detail->getFinitions()->contains($finition)) {
            $detail->addFinition($finition);
        }
    }
}
    private function synchroniserDetailManuel(
        DevisDetails $detail,
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
        DevisDetails $detail,
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
        '/devis/{id}/convertir-commande',
        name: 'convertir_commande',
        methods: ['POST']
    )]
    public function convertirCommande(
        Devis $devis,
        Request $request,
        DevisCommandeConverter $converter
    ): Response {
        if (!$this->isCsrfTokenValid(
            'convertir-devis-' . $devis->getId(),
            (string) $request->request->get('_token')
        )) {
            throw $this->createAccessDeniedException(
                'Jeton de sécurité invalide.'
            );
        }

        try {
            $commande = $converter->convertir($devis);

            $this->addFlash(
                'success',
                sprintf(
                    'Le devis %s a été validé et transféré dans la commande %s.',
                    $devis->getNumero(),
                    $commande->getNumero()
                        ?? '#' . $commande->getId()
                )
            );

            return $this->redirectToRoute(
                'app_commandes_show',
                [
                    'id' => $commande->getId(),
                ]
            );
        } catch (\LogicException $exception) {
            $this->addFlash(
                'warning',
                $exception->getMessage()
            );
        } catch (\Throwable $exception) {
    dd(
        $exception::class,
        $exception->getMessage(),
        $exception->getFile(),
        $exception->getLine()
    );
}

        return $this->redirectToRoute(
            'app_devis_show',
            [
                'id' => $devis->getId(),
            ]
        );
    }
    
   
}
