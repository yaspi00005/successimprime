<?php

namespace App\Controller;

use App\Entity\CommandeDetailFichier;
use App\Entity\CommandesDetails;
use App\Entity\ControlePrePresse;
use App\Entity\OrdreProduction;
use App\Entity\User;
use App\Repository\CommandesDetailsRepository;
use App\Repository\OrdreProductionRepository;
use Doctrine\ORM\EntityManagerInterface;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
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
         * Affiche uniquement les lignes ayant au moins un fichier.
         */
        $details = $detailsRepository
            ->createQueryBuilder('detail')
            ->addSelect('commande', 'produit', 'fichier')
            ->innerJoin('detail.commande', 'commande')
            ->leftJoin('detail.produit', 'produit')
            ->innerJoin('detail.fichiers', 'fichier')
            ->andWhere('fichier.actif = :actif')
            ->setParameter('actif', true)
            ->orderBy('commande.dateCommande', 'DESC')
            ->addOrderBy('detail.id', 'DESC')
            ->distinct()
            ->getQuery()
            ->getResult();

        return $this->render('controle_pre_presse/index.html.twig', [
            'details' => $details,
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
    OrdreProductionRepository $ordreProductionRepository
): Response {
        $utilisateur = $this->getUser();

        if (!$utilisateur instanceof User) {
            throw $this->createAccessDeniedException(
                'Vous devez être connecté pour effectuer un contrôle prépresse.'
            );
        }

        if ($detail->getFichiers()->isEmpty()) {
            $this->addFlash(
                'warning',
                'Cette ligne de commande ne contient aucun fichier.'
            );

            return $this->redirectToRoute('app_controle_pre_presse_index');
        }

        if ($request->isMethod('POST')) {
            $jeton = (string) $request->request->get('_token');

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

            $controle = new ControlePrePresse();
            $controle->setCommandeDetail($detail);

            $fichiersSelectionnes = $request->request->all('fichiers');

            foreach ($fichiersSelectionnes as $fichierId) {
                foreach ($detail->getFichiers() as $fichier) {
                    if (
                        $fichier->getId() === (int) $fichierId
                        && $fichier->isActif()
                    ) {
                        $controle->addFichier($fichier);
                    }
                }
            }

            if ($controle->getFichiers()->isEmpty()) {
                $this->addFlash(
                    'error',
                    'Sélectionnez au moins un fichier à contrôler.'
                );

                return $this->redirectToRoute(
                    'app_controle_pre_presse_controler',
                    ['id' => $detail->getId()]
                );
            }

            $controle
                ->setFormatConforme(
                    $request->request->getBoolean('formatConforme')
                )
                ->setDimensionsConformes(
                    $request->request->getBoolean('dimensionsConformes')
                )
                ->setResolutionConforme(
                    $request->request->getBoolean('resolutionConforme')
                )
                ->setProfilCouleursConforme(
                    $request->request->getBoolean('profilCouleursConforme')
                )
                ->setFondsPerdusConformes(
                    $request->request->getBoolean('fondsPerdusConformes')
                )
                ->setMargesSecuriteConformes(
                    $request->request->getBoolean(
                        'margesSecuriteConformes'
                    )
                )
                ->setPolicesConformes(
                    $request->request->getBoolean('policesConformes')
                )
                ->setOrthographeVerifiee(
                    $request->request->getBoolean('orthographeVerifiee')
                )
                ->setOrientationConforme(
                    $request->request->getBoolean('orientationConforme')
                )
                ->setNombrePagesConforme(
                    $request->request->getBoolean('nombrePagesConforme')
                )
                ->setRectoVersoConforme(
                    $request->request->getBoolean('rectoVersoConforme')
                )
                ->setSupportConforme(
                    $request->request->getBoolean('supportConforme')
                )
                ->setQuantiteConforme(
                    $request->request->getBoolean('quantiteConforme')
                )
                ->setFichierDejaTraite(
                    $request->request->getBoolean('fichierDejaTraite')
                )
                ->setBatNecessaire(
                    $request->request->getBoolean('batNecessaire')
                )
                ->setAnomalies(
                    $request->request->get('anomalies')
                )
                ->setCorrectionsEffectuees(
                    $request->request->get('correctionsEffectuees')
                )
                ->setObservation(
                    $request->request->get('observation')
                );

            $batValide = $request->request->getBoolean('batValide');

            if ($controle->isBatNecessaire()) {
                $controle->setBatValide($batValide);
            }

            $controle->commencerControle($utilisateur);

            $correctionNecessaire = $request->request->getBoolean(
                'correctionNecessaire'
            );

            $controle->setCorrectionNecessaire(
                $correctionNecessaire
            );

            $action = (string) $request->request->get(
                'action',
                'enregistrer'
            );

           try {
    $envoyerProduction = in_array(
        $action,
        ['valider', 'valider_production'],
        true
    );

    /*
     * Dans ton fonctionnement :
     * toute validation prépresse transmet automatiquement
     * le travail à la production.
     */
    if ($envoyerProduction) {
        $controle
            ->valider($utilisateur)
            ->envoyerEnProduction($utilisateur);
    }

    $detail->addControlePrePresse($controle);
    $entityManager->persist($controle);

    /*
     * Création de l’ordre seulement après validation
     * et transmission prépresse.
     */
    if ($envoyerProduction) {
        /*
         * Empêche la création de plusieurs ordres
         * pour la même ligne de commande.
         */
        $ordre = $ordreProductionRepository->findOneBy([
            'commandeDetail' => $detail,
        ]);

        if ($ordre === null) {
            $ordre = new OrdreProduction();

            $ordre
                ->setCommandeDetail($detail)
                ->setControlePrePresse($controle)
                ->setCreePar($utilisateur)
                ->setPriorite($detail->getPriorite())
                ->setQuantite($detail->getQuantite());

            /*
             * Affectation automatique de la machine
             * définie sur la ligne de commande.
             */
            if ($detail->getMachine() !== null) {
                $ordre->setMachine($detail->getMachine());
            }

            /*
             * Les observations de commande deviennent
             * les instructions de production.
             */
            if ($detail->getObservation() !== null) {
                $ordre->setInstructions(
                    $detail->getObservation()
                );
            }

            /*
             * Date de livraison de la commande utilisée
             * comme date limite de production.
             */
            $commande = $detail->getCommande();

            if (
                $commande !== null
                && $commande->getDateLivraison() !== null
            ) {
                $dateLivraison = $commande->getDateLivraison();

                /*
                 * Sécurise le type si getDateLivraison()
                 * retourne un DateTime mutable.
                 */
                if ($dateLivraison instanceof \DateTimeImmutable) {
                    $ordre->setDateLimite($dateLivraison);
                } else {
                    $ordre->setDateLimite(
                        \DateTimeImmutable::createFromMutable(
                            $dateLivraison
                        )
                    );
                }
            }

            /*
             * Copie dans l’ordre tous les fichiers
             * validés par le prépresse.
             */
            foreach ($controle->getFichiers() as $fichier) {
                $ordre->addFichier($fichier);
            }

            /*
             * Marque l’ordre comme réellement transmis.
             */
            $ordre->transmettre();

            /*
             * Synchronisation avec le statut conservé
             * dans CommandesDetails.
             */
            $detail->setStatutProduction(
                CommandesDetails::PRODUCTION_A_PRODUIRE
            );

            $entityManager->persist($ordre);

            $message = sprintf(
                'Prépresse validé. L’ordre %s a été transmis à la production.',
                $ordre->getNumero()
            );
        } else {
            $message = sprintf(
                'Le prépresse est validé. L’ordre %s existe déjà en production.',
                $ordre->getNumero()
            );
        }
    } else {
        $message = 'Le contrôle prépresse a été enregistré.';
    }

    /*
     * Le contrôle et l’ordre sont enregistrés
     * dans la même transaction Doctrine.
     */
    $entityManager->flush();

    $this->addFlash('success', $message);

    if ($envoyerProduction && isset($ordre)) {
        return $this->redirectToRoute(
            'app_production_show',
            ['id' => $ordre->getId()]
        );
    }

    return $this->redirectToRoute(
        'app_controle_pre_presse_controler',
        ['id' => $detail->getId()]
    );
} catch (
    \LogicException |
    \DomainException |
    \InvalidArgumentException $exception
) {
    $this->addFlash(
        'error',
        $exception->getMessage()
    );
}
        }

        return $this->render(
            'controle_pre_presse/controler.html.twig',
            [
                'detail' => $detail,
                'commande' => $detail->getCommande(),
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
