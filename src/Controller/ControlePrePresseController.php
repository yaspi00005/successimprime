<?php

namespace App\Controller;

use App\Entity\CommandeDetailFichier;
use App\Entity\CommandesDetails;
use App\Entity\ControlePrePresse;
use App\Entity\OrdreProduction;
use App\Entity\User;

use App\Repository\CommandesDetailsRepository;
use App\Repository\OrdreProductionRepository;

use App\Service\ControleCreditClientService;
use App\Service\BonusPlafondClientService;

use Doctrine\ORM\EntityManagerInterface;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;
use Symfony\Component\HttpFoundation\BinaryFileResponse;
use Symfony\Component\HttpFoundation\File\UploadedFile;
use Symfony\Component\HttpFoundation\ResponseHeaderBag;
use Symfony\Component\String\Slugger\SluggerInterface;



#[Route('/pre-presse', name: 'app_controle_pre_presse_')]
final class ControlePrePresseController extends AbstractController
{
    #[Route('/', name: 'index', methods: ['GET'])]
    public function index(
        CommandesDetailsRepository $detailsRepository
    ): Response {
        /*
         * Affiche uniquement les lignes ayant au moins un fichier
         * ET nécessitant réellement un contrôle prépresse : une
         * ligne en impression directe (prePresseNecessaire = false)
         * ne doit jamais apparaître ici, même si un fichier y est
         * rattaché.
         */
        $details = $detailsRepository
            ->createQueryBuilder('detail')
            ->addSelect('commande', 'produit', 'fichier')
            ->innerJoin('detail.commande', 'commande')
            ->leftJoin('detail.produit', 'produit')
            ->innerJoin('detail.fichiers', 'fichier')
            ->andWhere('fichier.actif = :actif')
            ->andWhere('detail.prePresseNecessaire = :prepresseNecessaire')
            ->setParameter('actif', true)
            ->setParameter('prepresseNecessaire', true)
            ->orderBy('commande.dateCommande', 'DESC')
            ->addOrderBy('detail.id', 'DESC')
            ->distinct()
            ->getQuery()
            ->getResult();

        return $this->render('controle_pre_presse/index.html.twig', [
            'details' => $details,
        ]);
    }

    /*
     * ============================================================
     * VÉRIFIER LES NOUVEAUX ÉLÉMENTS (ALERTE SONORE)
     * ============================================================
     *
     * Interrogé périodiquement en JS depuis la file d'attente pour
     * détecter l'arrivée d'une nouvelle ligne "à contrôler" (aucun
     * contrôle prépresse enregistré) et déclencher une alerte
     * sonore tant que personne ne l'a traitée.
     */
    #[Route('/verifier-nouveaux', name: 'verifier_nouveaux', methods: ['GET'])]
    public function verifierNouveaux(
        CommandesDetailsRepository $detailsRepository
    ): JsonResponse {
        $ids = $detailsRepository
            ->createQueryBuilder('detail')
            ->select('detail.id')
            ->innerJoin('detail.fichiers', 'fichier')
            ->leftJoin('detail.controlesPrePresse', 'controle')
            ->andWhere('fichier.actif = :actif')
            ->andWhere('controle.id IS NULL')
            ->andWhere('detail.prePresseNecessaire = :prepresseNecessaire')
            ->setParameter('actif', true)
            ->setParameter('prepresseNecessaire', true)
            ->distinct()
            ->getQuery()
            ->getResult();

        return $this->json([
            'ids' => array_map(
                static fn (array $ligne): int => (int) $ligne['id'],
                $ids
            ),
        ]);
    }

  #[Route(
    '/travail/{id}',
    name: 'controler',
    requirements: ['id' => '\d+'],
    methods: ['GET', 'POST']
)]
public function controler(
    CommandesDetails $detail,
    Request $request,
    EntityManagerInterface $entityManager,
    OrdreProductionRepository $ordreProductionRepository,
    ControleCreditClientService $controleCreditClientService,
    BonusPlafondClientService $bonusPlafondClientService
): Response {
    /*
     * ============================================================
     * UTILISATEUR CONNECTÉ
     * ============================================================
     */

    $utilisateur = $this->getUser();

    if (!$utilisateur instanceof User) {
        throw $this->createAccessDeniedException(
            'Vous devez être connecté pour effectuer un contrôle prépresse.'
        );
    }


    /*
     * ============================================================
     * COMMANDE
     * ============================================================
     */

    $commande = $detail->getCommande();

    if ($commande === null) {
        throw $this->createNotFoundException(
            'Aucune commande n’est associée à ce travail.'
        );
    }


    /*
     * ============================================================
     * VÉRIFICATION DES FICHIERS
     * ============================================================
     */

    if ($detail->getFichiers()->isEmpty()) {
        $this->addFlash(
            'warning',
            'Cette ligne de commande ne contient aucun fichier.'
        );

        return $this->redirectToRoute(
            'app_controle_pre_presse_index'
        );
    }


    /*
     * ============================================================
     * IMPRESSION DIRECTE : PAS DE PRÉPRESSE
     * ============================================================
     */

    if (!$detail->isPrePresseNecessaire()) {
        $this->addFlash(
            'warning',
            'Cette ligne de commande est en impression directe et ne nécessite pas de contrôle prépresse.'
        );

        return $this->redirectToRoute(
            'app_controle_pre_presse_index'
        );
    }


    /*
     * ============================================================
     * CONTRÔLE FINANCIER POUR AFFICHAGE
     * ============================================================
     *
     * Permet d'afficher dans le Twig :
     *
     * - ancienneté du client ;
     * - plafond ;
     * - encours antérieur ;
     * - avance sur la commande actuelle ;
     * - autorisation ou blocage.
     *
     * La commande actuelle reste neutre dans le calcul
     * du plafond.
     * ============================================================
     */

    $controleCredit =
        $controleCreditClientService
            ->analyser(
                $commande
            );


    /*
     * ============================================================
     * TRAITEMENT POST
     * ============================================================
     */

    if ($request->isMethod('POST')) {

        /*
         * ========================================================
         * CSRF
         * ========================================================
         */

        $jeton =
            (string) $request
                ->request
                ->get('_token');


        if (
            !$this->isCsrfTokenValid(
                'controle_pre_presse_' . $detail->getId(),
                $jeton
            )
        ) {
            throw $this->createAccessDeniedException(
                'Le jeton de sécurité est invalide.'
            );
        }


        /*
         * ========================================================
         * NOUVEAU CONTRÔLE PRÉPRESSE
         * ========================================================
         */

        $controle =
            new ControlePrePresse();


        $controle->setCommandeDetail(
            $detail
        );


        /*
         * ========================================================
         * FICHIERS SÉLECTIONNÉS
         * ========================================================
         */

        $fichiersSelectionnes =
            $request
                ->request
                ->all('fichiers');


        foreach (
            $fichiersSelectionnes
            as $fichierId
        ) {
            foreach (
                $detail->getFichiers()
                as $fichier
            ) {
                if (
                    $fichier->getId()
                    ===
                    (int) $fichierId
                    &&
                    $fichier->isActif()
                ) {
                    $controle->addFichier(
                        $fichier
                    );
                }
            }
        }


        /*
         * ========================================================
         * AU MOINS UN FICHIER
         * ========================================================
         */

        if (
            $controle
                ->getFichiers()
                ->isEmpty()
        ) {
            $this->addFlash(
                'error',
                'Sélectionnez au moins un fichier à contrôler.'
            );

            return $this->redirectToRoute(
                'app_controle_pre_presse_controler',
                [
                    'id' =>
                        $detail->getId(),
                ]
            );
        }


        /*
         * ========================================================
         * CONTRÔLES TECHNIQUES
         * ========================================================
         */

        $controle
            ->setFormatConforme(
                $request
                    ->request
                    ->getBoolean(
                        'formatConforme'
                    )
            )
            ->setDimensionsConformes(
                $request
                    ->request
                    ->getBoolean(
                        'dimensionsConformes'
                    )
            )
            ->setResolutionConforme(
                $request
                    ->request
                    ->getBoolean(
                        'resolutionConforme'
                    )
            )
            ->setProfilCouleursConforme(
                $request
                    ->request
                    ->getBoolean(
                        'profilCouleursConforme'
                    )
            )
            ->setFondsPerdusConformes(
                $request
                    ->request
                    ->getBoolean(
                        'fondsPerdusConformes'
                    )
            )
            ->setMargesSecuriteConformes(
                $request
                    ->request
                    ->getBoolean(
                        'margesSecuriteConformes'
                    )
            )
            ->setPolicesConformes(
                $request
                    ->request
                    ->getBoolean(
                        'policesConformes'
                    )
            )
            ->setOrthographeVerifiee(
                $request
                    ->request
                    ->getBoolean(
                        'orthographeVerifiee'
                    )
            )
            ->setOrientationConforme(
                $request
                    ->request
                    ->getBoolean(
                        'orientationConforme'
                    )
            )
            ->setNombrePagesConforme(
                $request
                    ->request
                    ->getBoolean(
                        'nombrePagesConforme'
                    )
            )
            ->setRectoVersoConforme(
                $request
                    ->request
                    ->getBoolean(
                        'rectoVersoConforme'
                    )
            )
            ->setSupportConforme(
                $request
                    ->request
                    ->getBoolean(
                        'supportConforme'
                    )
            )
            ->setQuantiteConforme(
                $request
                    ->request
                    ->getBoolean(
                        'quantiteConforme'
                    )
            )
            ->setFichierDejaTraite(
                $request
                    ->request
                    ->getBoolean(
                        'fichierDejaTraite'
                    )
            )
            ->setBatNecessaire(
                $request
                    ->request
                    ->getBoolean(
                        'batNecessaire'
                    )
            )
            ->setAnomalies(
                $request
                    ->request
                    ->get(
                        'anomalies'
                    )
            )
            ->setCorrectionsEffectuees(
                $request
                    ->request
                    ->get(
                        'correctionsEffectuees'
                    )
            )
            ->setObservation(
                $request
                    ->request
                    ->get(
                        'observation'
                    )
            );


        /*
         * ========================================================
         * BAT
         * ========================================================
         */

        $batValide =
            $request
                ->request
                ->getBoolean(
                    'batValide'
                );


        if (
            $controle
                ->isBatNecessaire()
        ) {
            $controle->setBatValide(
                $batValide
            );
        }


        /*
         * ========================================================
         * DÉBUT DU CONTRÔLE
         * ========================================================
         */

        $controle->commencerControle(
            $utilisateur
        );


        /*
         * ========================================================
         * CORRECTION NÉCESSAIRE
         * ========================================================
         */

        $correctionNecessaire =
            $request
                ->request
                ->getBoolean(
                    'correctionNecessaire'
                );


        $controle->setCorrectionNecessaire(
            $correctionNecessaire
        );


        /*
         * ========================================================
         * ACTION
         * ========================================================
         */

        $action =
            (string) $request
                ->request
                ->get(
                    'action',
                    'enregistrer'
                );


        /*
         * ========================================================
         * VALIDATION DE L'ACTION
         * ========================================================
         */

        if (
            !in_array(
                $action,
                [
                    'enregistrer',
                    'valider',
                    'valider_production',
                ],
                true
            )
        ) {
            $this->addFlash(
                'error',
                'Action prépresse invalide.'
            );

            return $this->redirectToRoute(
                'app_controle_pre_presse_controler',
                [
                    'id' =>
                        $detail->getId(),
                ]
            );
        }


        /*
         * ========================================================
         * DÉTERMINATION DU CIRCUIT
         * ========================================================
         */

        $validerControle =
            in_array(
                $action,
                [
                    'valider',
                    'valider_production',
                ],
                true
            );


        $envoyerProduction =
            $action
            ===
            'valider_production';


        /*
         * Valeur par défaut :
         * aucun bonus appliqué.
         */
        $bonusPlafond =
            0;


        try {

            /*
             * ====================================================
             * 1. CONTRÔLE FINANCIER AVANT PRODUCTION
             * ====================================================
             *
             * IMPORTANT :
             *
             * Le contrôle doit être fait AVANT d'ajouter le bonus
             * de 1 % de la commande actuelle.
             *
             * Ainsi :
             *
             * - la commande actuelle reste neutre ;
             * - son propre bonus ne peut pas l'aider à passer ;
             * - seules les anciennes dettes sont prises en compte.
             * ====================================================
             */

            if ($envoyerProduction) {

                $controleCredit =
                    $controleCreditClientService
                        ->analyser(
                            $commande
                        );


                if (
                    $controleCredit['autorise']
                    !==
                    true
                ) {
                    throw new \DomainException(
                        $controleCredit[
                            'motif'
                        ]
                    );
                }
            }


            /*
             * ====================================================
             * 2. VALIDATION PRÉPRESSE
             * ====================================================
             */

            if ($validerControle) {

                $controle->valider(
                    $utilisateur
                );


                /*
                 * =================================================
                 * BONUS PLAFOND CLIENT : +1 %
                 * =================================================
                 *
                 * Appliqué après validation réussie.
                 *
                 * Bonus une seule fois par commande.
                 * =================================================
                 */

                $bonusPlafond =
                    $bonusPlafondClientService
                        ->appliquer(
                            $commande
                        );
            }


            /*
             * ====================================================
             * 3. ENVOI EN PRODUCTION
             * ====================================================
             */

            if ($envoyerProduction) {
                $controle
                    ->envoyerEnProduction(
                        $utilisateur
                    );
            }


            /*
             * ====================================================
             * 4. RATTACHEMENT DU CONTRÔLE
             * ====================================================
             */

            $detail
                ->addControlePrePresse(
                    $controle
                );


            $entityManager->persist(
                $controle
            );


            /*
             * ====================================================
             * 5. CRÉATION ORDRE DE PRODUCTION
             * ====================================================
             */

            $ordre = null;


            if ($envoyerProduction) {

                /*
                 * Recherche ordre existant.
                 */
                $ordre =
                    $ordreProductionRepository
                        ->findOneBy([
                            'commandeDetail' =>
                                $detail,
                        ]);


                /*
                 * =================================================
                 * CRÉATION SI AUCUN ORDRE
                 * =================================================
                 */

                if ($ordre === null) {

                    $ordre =
                        new OrdreProduction();


                    $ordre
                        ->setCommandeDetail(
                            $detail
                        )
                        ->setControlePrePresse(
                            $controle
                        )
                        ->setCreePar(
                            $utilisateur
                        )
                        ->setPriorite(
                            $detail
                                ->getPriorite()
                        )
                        ->setQuantite(
                            $detail
                                ->getQuantite()
                        );


                    /*
                     * =============================================
                     * MACHINE
                     * =============================================
                     */

                    if (
                        $detail->getMachine()
                        !==
                        null
                    ) {
                        $ordre->setMachine(
                            $detail
                                ->getMachine()
                        );
                    }


                    /*
                     * =============================================
                     * INSTRUCTIONS
                     * =============================================
                     */

                    if (
                        $detail
                            ->getObservation()
                        !==
                        null
                    ) {
                        $ordre
                            ->setInstructions(
                                $detail
                                    ->getObservation()
                            );
                    }


                    /*
                     * =============================================
                     * DATE LIMITE
                     * =============================================
                     */

                    if (
                        $commande
                            ->getDateLivraison()
                        !==
                        null
                    ) {
                        $dateLivraison =
                            $commande
                                ->getDateLivraison();


                        if (
                            $dateLivraison
                            instanceof
                            \DateTimeImmutable
                        ) {
                            $ordre->setDateLimite(
                                $dateLivraison
                            );
                        } else {
                            $ordre->setDateLimite(
                                \DateTimeImmutable
                                    ::createFromMutable(
                                        $dateLivraison
                                    )
                            );
                        }
                    }


                    /*
                     * =============================================
                     * FICHIERS VALIDÉS
                     * =============================================
                     */

                    foreach (
                        $controle->getFichiers()
                        as $fichier
                    ) {
                        $ordre->addFichier(
                            $fichier
                        );
                    }


                    /*
                     * =============================================
                     * TRANSMISSION
                     * =============================================
                     */

                    $ordre->transmettre();


                    /*
                     * =============================================
                     * STATUT PRODUCTION DU DÉTAIL
                     * =============================================
                     */

                    $detail
                        ->setStatutProduction(
                            CommandesDetails
                                ::PRODUCTION_A_PRODUIRE
                        );


                    $entityManager->persist(
                        $ordre
                    );


                    /*
                     * =============================================
                     * MESSAGE
                     * =============================================
                     */

                    if ($bonusPlafond > 0) {

                        $message =
                            sprintf(
                                'Prépresse validé. L’ordre %s a été transmis à la production. Le plafond du client a augmenté de %s FCFA.',
                                $ordre->getNumero(),
                                number_format(
                                    $bonusPlafond,
                                    0,
                                    ',',
                                    ' '
                                )
                            );

                    } else {

                        $message =
                            sprintf(
                                'Prépresse validé. L’ordre %s a été transmis à la production.',
                                $ordre->getNumero()
                            );
                    }

                } else {

                    /*
                     * =================================================
                     * ORDRE DÉJÀ EXISTANT
                     * =================================================
                     */

                    $message =
                        sprintf(
                            'Le prépresse est validé. L’ordre %s existe déjà en production.',
                            $ordre->getNumero()
                        );
                }

            } elseif (
                $action ===
                'valider'
            ) {

                /*
                 * =================================================
                 * VALIDATION SANS PRODUCTION
                 * =================================================
                 */

                if ($bonusPlafond > 0) {

                    $message =
                        sprintf(
                            'Le contrôle prépresse a été validé. Le plafond du client a augmenté de %s FCFA. Le travail n’a pas encore été envoyé en production.',
                            number_format(
                                $bonusPlafond,
                                0,
                                ',',
                                ' '
                            )
                        );

                } else {

                    $message =
                        'Le contrôle prépresse a été validé. Le travail n’a pas encore été envoyé en production.';
                }

            } else {

                /*
                 * =================================================
                 * SIMPLE ENREGISTREMENT
                 * =================================================
                 */

                $message =
                    'Le contrôle prépresse a été enregistré.';
            }


            /*
             * ====================================================
             * 6. ENREGISTREMENT GLOBAL
             * ====================================================
             *
             * Doctrine sauvegarde dans le même flush :
             *
             * - contrôle prépresse ;
             * - détail ;
             * - ordre ;
             * - nouveau plafond client ;
             * - marqueur bonus de la commande.
             * ====================================================
             */

            $entityManager->flush();


            /*
             * ====================================================
             * MESSAGE SUCCÈS
             * ====================================================
             */

            $this->addFlash(
                'success',
                $message
            );


            /*
             * ====================================================
             * REDIRECTION VERS PRODUCTION
             * ====================================================
             */

            if (
                $envoyerProduction
                &&
                $ordre !== null
            ) {
                return $this->redirectToRoute(
                    'app_production_show',
                    [
                        'id' =>
                            $ordre->getId(),
                    ]
                );
            }


            /*
             * ====================================================
             * RETOUR PRÉPRESSE
             * ====================================================
             */

            return $this->redirectToRoute(
                'app_controle_pre_presse_controler',
                [
                    'id' =>
                        $detail->getId(),
                ]
            );

        } catch (
            \LogicException |
            \DomainException |
            \InvalidArgumentException $exception
        ) {

            /*
             * ====================================================
             * ERREUR MÉTIER
             * ====================================================
             */

            $this->addFlash(
                'error',
                $exception->getMessage()
            );
        }
    }


    /*
     * ============================================================
     * RECALCUL APRÈS POST / POUR AFFICHAGE GET
     * ============================================================
     */

    $controleCredit =
        $controleCreditClientService
            ->analyser(
                $commande
            );


    /*
     * ============================================================
     * AFFICHAGE
     * ============================================================
     */

    return $this->render(
        'controle_pre_presse/controler.html.twig',
        [
            'detail' =>
                $detail,

            'commande' =>
                $commande,

            'controleCredit' =>
                $controleCredit,
        ]
    );
}
    #[Route(
        '/travail/{id}/fichier-traite',
        name: 'ajouter_fichier_traite',
        requirements: ['id' => '\d+'],
        methods: ['POST']
    )]
    public function ajouterFichierTraite(
        CommandesDetails $detail,
        Request $request,
        EntityManagerInterface $entityManager,
        SluggerInterface $slugger
    ): Response {
        $utilisateur = $this->getUser();

        if (!$utilisateur instanceof User) {
            throw $this->createAccessDeniedException(
                'Vous devez être connecté.'
            );
        }

        if (!$this->isCsrfTokenValid(
            'ajouter_fichier_traite_' . $detail->getId(),
            (string) $request->request->get('_token')
        )) {
            throw $this->createAccessDeniedException(
                'Le jeton de sécurité est invalide.'
            );
        }
        /** @var UploadedFile|null $fichierUpload */
        $fichierUpload = $request->files->get('fichierTraite');

        if (!$fichierUpload instanceof UploadedFile) {
            $this->addFlash(
                'error',
                'Veuillez sélectionner un fichier traité.'
            );

            return $this->redirectToRoute(
                'app_controle_pre_presse_controler',
                ['id' => $detail->getId()]
            );
        }

        if (!$fichierUpload->isValid()) {
            $this->addFlash(
                'error',
                'Le fichier n’a pas pu être envoyé correctement.'
            );

            return $this->redirectToRoute(
                'app_controle_pre_presse_controler',
                ['id' => $detail->getId()]
            );
        }

        /*
     * 600 Mo maximum.
     * Vérifiez également upload_max_filesize et post_max_size dans php.ini.
     */
        $tailleMaximale = 600 * 1024 * 1024;

        if ($fichierUpload->getSize() > $tailleMaximale) {
            $this->addFlash(
                'error',
                'Le fichier dépasse la taille maximale autorisée de 600 Mo.'
            );

            return $this->redirectToRoute(
                'app_controle_pre_presse_controler',
                ['id' => $detail->getId()]
            );
        }

        $fichierSourceId = $request->request->getInt('fichierSource');

        $fichierSource = null;

        foreach ($detail->getFichiers() as $fichierDetail) {
            if ($fichierDetail->getId() === $fichierSourceId) {
                $fichierSource = $fichierDetail;
                break;
            }
        }

        if (!$fichierSource instanceof CommandeDetailFichier) {
            $this->addFlash(
                'error',
                'Sélectionnez le fichier original correspondant.'
            );

            return $this->redirectToRoute(
                'app_controle_pre_presse_controler',
                ['id' => $detail->getId()]
            );
        }

        /*
         * Ces métadonnées doivent être lues avant move(), car le fichier
         * temporaire PHP n'existe plus à son ancien emplacement ensuite.
         */
        $nomOriginal = $fichierUpload->getClientOriginalName();
        $taille = (int) ($fichierUpload->getSize() ?: 0);
        $typeMime = $fichierUpload->getMimeType()
            ?: $fichierUpload->getClientMimeType()
            ?: 'application/octet-stream';
        $nomSansExtension = pathinfo(
            $nomOriginal,
            PATHINFO_FILENAME
        );

        $nomSecurise = $slugger
            ->slug($nomSansExtension)
            ->lower();

        $extension = $fichierUpload->guessExtension()
            ?: $fichierUpload->getClientOriginalExtension()
            ?: 'bin';

        $nomStockage = sprintf(
            '%s-v%d-%s.%s',
            $nomSecurise,
            $fichierSource->getVersion() + 1,
            bin2hex(random_bytes(8)),
            strtolower($extension)
        );

        $repertoireRelatif = sprintf(
            'uploads/prepresse/commande_%d/detail_%d',
            $detail->getCommande()->getId(),
            $detail->getId()
        );

        $repertoireAbsolu = $this->getParameter('kernel.project_dir')
            . '/public/'
            . $repertoireRelatif;

        try {
            $fichierDeplace = $fichierUpload->move(
                $repertoireAbsolu,
                $nomStockage
            );
        } catch (\Throwable $exception) {
            $this->addFlash(
                'error',
                'Impossible d’enregistrer le fichier traité : '
                    . $exception->getMessage()
            );

            return $this->redirectToRoute(
                'app_controle_pre_presse_controler',
                ['id' => $detail->getId()]
            );
        }

        $fichierTraite = new CommandeDetailFichier();

        $fichierTraite
            ->setCommandeDetail($detail)
            ->setFichierSource($fichierSource)
            ->setJetonUpload(bin2hex(random_bytes(32)))
            ->setNomOriginal($nomOriginal)
            ->setNomStockage($nomStockage)
            ->setChemin($repertoireRelatif . '/' . $nomStockage)
            ->setTypeMime($typeMime)
            ->setTaille($taille)
            ->setOrigine(CommandeDetailFichier::ORIGINE_INTERNE)
            ->setEtat(CommandeDetailFichier::ETAT_TRAITE)
            ->setVersion($fichierSource->getVersion() + 1)
            ->setFace(
                $request->request->get('face') ?: $fichierSource->getFace()
            )
            ->setDesignation(
                $request->request->get('designation')
                    ?: 'Fichier traité'
            )
            ->setGroupeFichier(
                $fichierSource->getGroupeFichier()
            )
            ->setQuantiteAProduire(
                $fichierSource->getQuantiteAProduire()
            )
            ->setObservation(
                $request->request->get('observation')
            )
            ->setAjoutePar($utilisateur)
            ->marquerUploadTermine();

        $detail->addFichier($fichierTraite);

        $entityManager->persist($fichierTraite);
        $entityManager->flush();

        $this->addFlash(
            'success',
            'Le fichier traité a été ajouté avec succès.'
        );

        return $this->redirectToRoute(
            'app_controle_pre_presse_controler',
            ['id' => $detail->getId()]
        );
    }
    #[Route(
        '/fichier/{id}/visualiser',
        name: 'visualiser_fichier',
        requirements: ['id' => '\d+'],
        methods: ['GET']
    )]
    public function visualiserFichier(
        CommandeDetailFichier $fichier
    ): BinaryFileResponse {
        if (!$fichier->isActif()) {
            throw $this->createNotFoundException(
                'Le fichier demandé est indisponible.'
            );
        }

        $projet = (string) $this->getParameter('kernel.project_dir');

        /*
     * Répertoire réel de stockage :
     * var/uploads/commandes
     */
        $racineStockage = $projet . '/var/uploads/commandes';
        $racineReelle = realpath($racineStockage);

        if ($racineReelle === false || !is_dir($racineReelle)) {
            throw $this->createNotFoundException(
                'Le répertoire de stockage est introuvable.'
            );
        }

        $nomStockage = basename(
            trim((string) $fichier->getNomStockage())
        );

        if ($nomStockage === '' || $nomStockage === '.') {
            throw $this->createNotFoundException(
                'Le nom de stockage du fichier est invalide.'
            );
        }

        $cheminRecherche = $racineStockage
            . DIRECTORY_SEPARATOR
            . $nomStockage;

        $cheminComplet = realpath($cheminRecherche);

        /*
     * Sécurité :
     * le fichier doit obligatoirement rester dans
     * var/uploads/commandes.
     */
        if (
            $cheminComplet === false
            || !str_starts_with(
                $cheminComplet,
                $racineReelle . DIRECTORY_SEPARATOR
            )
            || !is_file($cheminComplet)
            || !is_readable($cheminComplet)
        ) {
            throw $this->createNotFoundException(
                'Le fichier est introuvable sur le serveur.'
            );
        }

        /*
     * Détection réelle du type MIME.
     * On ne dépend pas seulement de la valeur enregistrée en base.
     */
        $extension = strtolower(
            pathinfo($cheminComplet, PATHINFO_EXTENSION)
        );

        $extensionsImages = [
            'jpg',
            'jpeg',
            'png',
            'webp',
        ];

        if (in_array($extension, $extensionsImages, true)) {
            $racineApercus = $racineReelle
                . DIRECTORY_SEPARATOR
                . 'apercus';

            $cheminApercu = $racineApercus
                . DIRECTORY_SEPARATOR
                . basename($cheminComplet);

            if (is_file($cheminApercu) && is_readable($cheminApercu)) {
                $cheminComplet = $cheminApercu;
            }
        }
        $typeMime = mime_content_type($cheminComplet);

        if ($typeMime === false) {
            $typeMime = $fichier->getTypeMime()
                ?: 'application/octet-stream';
        }

        $nomOriginal = trim(
            (string) $fichier->getNomOriginal()
        );

        if ($nomOriginal === '') {
            $nomOriginal = basename($cheminComplet);
        }

        $response = new BinaryFileResponse($cheminComplet);

        $response->headers->set('Content-Type', $typeMime);
        $response->headers->set('X-Content-Type-Options', 'nosniff');
        $response->headers->set('Cache-Control', 'private, max-age=0');

        $response->setContentDisposition(
            ResponseHeaderBag::DISPOSITION_INLINE,
            $nomOriginal
        );

        return $response;
    }
    #[Route(
        '/fichier/{id}/telecharger',
        name: 'telecharger_fichier',
        requirements: ['id' => '\d+'],
        methods: ['GET']
    )]
    public function telechargerFichier(
        CommandeDetailFichier $fichier
    ): BinaryFileResponse {
        if (!$fichier->isActif()) {
            throw $this->createNotFoundException(
                'Le fichier demandé est indisponible.'
            );
        }

        $projet = (string) $this->getParameter('kernel.project_dir');
        $racineStockage = $projet . '/var/uploads/commandes';
        $racineReelle = realpath($racineStockage);

        if ($racineReelle === false || !is_dir($racineReelle)) {
            throw $this->createNotFoundException(
                'Le répertoire de stockage est introuvable.'
            );
        }

        $nomStockage = basename(
            trim((string) $fichier->getNomStockage())
        );

        if ($nomStockage === '' || $nomStockage === '.') {
            throw $this->createNotFoundException(
                'Le nom de stockage est invalide.'
            );
        }

        $cheminComplet = realpath(
            $racineReelle . DIRECTORY_SEPARATOR . $nomStockage
        );

        if (
            $cheminComplet === false
            || !str_starts_with(
                $cheminComplet,
                $racineReelle . DIRECTORY_SEPARATOR
            )
            || !is_file($cheminComplet)
            || !is_readable($cheminComplet)
        ) {
            throw $this->createNotFoundException(
                'Le fichier original est introuvable sur le serveur.'
            );
        }

        $nomOriginal = trim(
            (string) $fichier->getNomOriginal()
        );

        if ($nomOriginal === '') {
            $nomOriginal = basename($cheminComplet);
        }

        $response = new BinaryFileResponse($cheminComplet);

        /*
     * ATTACHMENT force le téléchargement.
     * La route de visualisation utilise INLINE.
     */
        $response->setContentDisposition(
            ResponseHeaderBag::DISPOSITION_ATTACHMENT,
            $nomOriginal
        );

        $typeMime = mime_content_type($cheminComplet);

        $response->headers->set(
            'Content-Type',
            $typeMime ?: 'application/octet-stream'
        );

        $response->headers->set(
            'X-Content-Type-Options',
            'nosniff'
        );

        return $response;
    }
}
