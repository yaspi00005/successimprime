<?php

namespace App\Controller;

use App\Entity\CommandeDetailFichier;
use App\Repository\CommandeDetailFichierRepository;
use Doctrine\ORM\EntityManagerInterface;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\File\UploadedFile;
use Symfony\Component\HttpFoundation\BinaryFileResponse;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\ResponseHeaderBag;
use Symfony\Component\HttpKernel\KernelInterface;
use Symfony\Component\Routing\Attribute\Route;

#[Route('/commande-fichiers')]
final class FichierUploadController extends AbstractController
{
    private const TAILLE_MAX = 750 * 1024 * 1024;
    private const NOMBRE_MORCEAUX_MAX = 10000;

    private string $dossierTemporaire;
    private string $dossierFinal;

    public function __construct(
        KernelInterface $kernel
    ) {
        $this->dossierTemporaire =
            $kernel->getProjectDir().'/var/uploads/commande_tmp';

        $this->dossierFinal =
            $kernel->getProjectDir().'/var/uploads/commandes';

        foreach ([
            $this->dossierTemporaire,
            $this->dossierFinal,
        ] as $dossier) {
            if (
                !is_dir($dossier)
                && !mkdir($dossier, 0775, true)
                && !is_dir($dossier)
            ) {
                throw new \RuntimeException(
                    'Impossible de créer le dossier : '.$dossier
                );
            }
        }
    }

    #[Route('/initialiser', name: 'app_fichier_upload_initialiser', methods: ['POST'])]
    public function initialiser(
        Request $request,
        EntityManagerInterface $entityManager
    ): JsonResponse {
        if (!$this->isCsrfTokenValid(
            'upload-commande',
            $request->headers->get('X-CSRF-TOKEN')
        )) {
            return $this->json([
                'message' => 'Jeton CSRF invalide.',
            ], 403);
        }

        try {
            $donnees = $request->toArray();
        } catch (\Throwable) {
            return $this->json([
                'message' => 'Le corps JSON de la requête est invalide.',
            ], 400);
        }

        $nomOriginal = trim((string) ($donnees['nom'] ?? ''));
        $typeMime = trim((string) ($donnees['typeMime'] ?? 'application/octet-stream'));
        $taille = (int) ($donnees['taille'] ?? 0);
        $nombreMorceaux = (int) ($donnees['nombreMorceaux'] ?? 0);

        if (
            $nomOriginal === ''
            || $taille <= 0
            || $nombreMorceaux <= 0
            || $taille > self::TAILLE_MAX
            || $nombreMorceaux > self::NOMBRE_MORCEAUX_MAX
        ) {
            return $this->json([
                'message' => 'Informations du fichier invalides.',
            ], 422);
        }

        $jeton = bin2hex(random_bytes(32));

        $extension = strtolower(
            pathinfo($nomOriginal, PATHINFO_EXTENSION)
        );

        $nomStockage = $jeton;

        if ($extension !== '') {
            $nomStockage .= '.'.preg_replace(
                '/[^a-z0-9]/i',
                '',
                $extension
            );
        }

        $dossierJeton = $this->dossierTemporaire.'/'.$jeton;

        if (!mkdir($dossierJeton, 0775, true) && !is_dir($dossierJeton)) {
            return $this->json([
                'message' => 'Impossible de créer le dossier temporaire.',
            ], 500);
        }

        $fichier = (new CommandeDetailFichier())
            ->setJetonUpload($jeton)
            ->setNomOriginal(basename($nomOriginal))
            ->setNomStockage($nomStockage)
            ->setTypeMime($typeMime ?: 'application/octet-stream')
            ->setTaille($taille)
            ->setNombreMorceaux($nombreMorceaux)
            ->setMorceauxRecus(0)
            ->setStatut('EN_COURS');

        $entityManager->persist($fichier);
        $entityManager->flush();

        return $this->json([
            'jeton' => $jeton,
            'morceauxRecus' => 0,
            'nombreMorceaux' => $nombreMorceaux,
            'statut' => 'EN_COURS',
        ], 201);
    }

    #[Route(
        '/{jeton}/morceaux/{index}',
        name: 'app_fichier_upload_morceau',
        requirements: [
            'jeton' => '[a-f0-9]{64}',
            'index' => '\d+',
        ],
        methods: ['POST']
    )]
    public function envoyerMorceau(
        string $jeton,
        int $index,
        Request $request,
        CommandeDetailFichierRepository $repository,
        EntityManagerInterface $entityManager
    ): JsonResponse {
        if (!$this->isCsrfTokenValid(
            'upload-commande',
            $request->headers->get('X-CSRF-TOKEN')
        )) {
            return $this->json([
                'message' => 'Jeton CSRF invalide.',
            ], 403);
        }

        $fichier = $repository->findOneBy([
            'jetonUpload' => $jeton,
        ]);

        if (!$fichier) {
            return $this->json([
                'message' => 'Session d’upload introuvable.',
            ], 404);
        }

        if ($fichier->getStatut() === 'TERMINE') {
            return $this->json([
                'jeton' => $jeton,
                'statut' => 'TERMINE',
                'progression' => 100,
            ]);
        }

        $nombreMorceaux = $fichier->getNombreMorceaux();

        if (
            $nombreMorceaux === null
            || $index < 0
            || $index >= $nombreMorceaux
        ) {
            return $this->json([
                'message' => 'Index du morceau invalide.',
            ], 422);
        }

        /** @var UploadedFile|null $morceau */
        $morceau = $request->files->get('morceau');

        if (!$morceau || !$morceau->isValid()) {
            return $this->json([
                'message' => 'Morceau absent ou invalide.',
            ], 422);
        }

        $dossierJeton = $this->dossierTemporaire.'/'.$jeton;

        if (
            !is_dir($dossierJeton)
            && !mkdir($dossierJeton, 0775, true)
            && !is_dir($dossierJeton)
        ) {
            return $this->json([
                'message' => 'Impossible de créer le dossier temporaire.',
            ], 500);
        }

        $cheminMorceau = $dossierJeton.'/'.sprintf(
            '%08d.part',
            $index
        );

        /*
         * Si le morceau existe déjà, on ne le compte pas deux fois.
         * Cela permet de reprendre un transfert interrompu.
         */
        if (!is_file($cheminMorceau)) {
            $morceau->move(
                $dossierJeton,
                basename($cheminMorceau)
            );
        }

        $morceauxRecus = count(
            glob($dossierJeton.'/*.part') ?: []
        );

        $fichier->setMorceauxRecus($morceauxRecus);

        if ($morceauxRecus === $nombreMorceaux) {
            $this->assemblerFichier($fichier);
        }

        $entityManager->flush();

        $progression = (int) floor(
            ($fichier->getMorceauxRecus() / $nombreMorceaux) * 100
        );

        return $this->json([
            'jeton' => $jeton,
            'morceauxRecus' => $fichier->getMorceauxRecus(),
            'nombreMorceaux' => $nombreMorceaux,
            'progression' => min(100, $progression),
            'statut' => $fichier->getStatut(),
        ]);
    }

    #[Route(
        '/{jeton}/statut',
        name: 'app_fichier_upload_statut',
        requirements: [
            'jeton' => '[a-f0-9]{64}',
        ],
        methods: ['GET']
    )]
    public function statut(
        string $jeton,
        CommandeDetailFichierRepository $repository
    ): JsonResponse {
        $fichier = $repository->findOneBy([
            'jetonUpload' => $jeton,
        ]);

        if (!$fichier) {
            return $this->json([
                'message' => 'Fichier introuvable.',
            ], 404);
        }

        $nombreMorceaux = $fichier->getNombreMorceaux() ?? 0;

        $progression = $nombreMorceaux > 0
            ? (int) floor(
                ($fichier->getMorceauxRecus() / $nombreMorceaux) * 100
            )
            : 0;

        return $this->json([
            'jeton' => $fichier->getJetonUpload(),
            'nom' => $fichier->getNomOriginal(),
            'taille' => $fichier->getTaille(),
            'morceauxRecus' => $fichier->getMorceauxRecus(),
            'nombreMorceaux' => $nombreMorceaux,
            'progression' => min(100, $progression),
            'statut' => $fichier->getStatut(),
        ]);
    }

    #[Route(
        '/{id}/visualiser',
        name: 'app_fichier_visualiser',
        requirements: ['id' => '\\d+'],
        methods: ['GET']
    )]
    public function visualiser(
        CommandeDetailFichier $fichier
    ): BinaryFileResponse {
        if ($fichier->getStatut() !== 'TERMINE' || !$fichier->getNomStockage()) {
            throw $this->createNotFoundException('Ce fichier est indisponible.');
        }

        $dossierFinal = realpath($this->dossierFinal);
        $chemin = $dossierFinal !== false
            ? realpath($dossierFinal.DIRECTORY_SEPARATOR.basename($fichier->getNomStockage()))
            : false;

        if (
            $dossierFinal === false
            || $chemin === false
            || !str_starts_with($chemin, $dossierFinal.DIRECTORY_SEPARATOR)
            || !is_file($chemin)
        ) {
            throw $this->createNotFoundException(
                'Le fichier physique est introuvable.'
            );
        }

        $response = new BinaryFileResponse($chemin);
        $response->setContentDisposition(
            ResponseHeaderBag::DISPOSITION_INLINE,
            $fichier->getNomOriginal() ?: basename($chemin)
        );
        $response->headers->set('X-Content-Type-Options', 'nosniff');
        $response->headers->set('Cache-Control', 'private, no-store');

        if ($fichier->getTypeMime()) {
            $response->headers->set('Content-Type', $fichier->getTypeMime());
        }

        return $response;
    }

    private function assemblerFichier(
        CommandeDetailFichier $fichier
    ): void {
        $jeton = $fichier->getJetonUpload();

        if ($jeton === null) {
            throw new \RuntimeException('Jeton d’upload absent.');
        }

        $dossierJeton = $this->dossierTemporaire.'/'.$jeton;

        if (
            !is_dir($this->dossierFinal)
            && !mkdir($this->dossierFinal, 0775, true)
            && !is_dir($this->dossierFinal)
        ) {
            throw new \RuntimeException(
                'Impossible de créer le dossier final.'
            );
        }

        $cheminFinal = $this->dossierFinal
            .'/'.basename((string) $fichier->getNomStockage());
        $cheminAssemblage = $cheminFinal.'.assemblage';

        $sortie = fopen($cheminAssemblage, 'wb');

        if ($sortie === false) {
            throw new \RuntimeException(
                'Impossible de créer le fichier final.'
            );
        }

        try {
            for (
                $index = 0;
                $index < (int) $fichier->getNombreMorceaux();
                $index++
            ) {
                $cheminMorceau = $dossierJeton.'/'.sprintf(
                    '%08d.part',
                    $index
                );

                if (!is_file($cheminMorceau)) {
                    throw new \RuntimeException(
                        sprintf('Le morceau %d est absent.', $index)
                    );
                }

                $entree = fopen($cheminMorceau, 'rb');

                if ($entree === false) {
                    throw new \RuntimeException(
                        sprintf(
                            'Impossible de lire le morceau %d.',
                            $index
                        )
                    );
                }

                stream_copy_to_stream($entree, $sortie);
                fclose($entree);
            }
        } catch (\Throwable $exception) {
            @unlink($cheminAssemblage);
            throw $exception;
        } finally {
            fclose($sortie);
        }

        $tailleReelle = filesize($cheminAssemblage);

        if ($tailleReelle === false || $tailleReelle !== $fichier->getTaille()) {
            @unlink($cheminAssemblage);

            throw new \RuntimeException(
                'La taille du fichier assemblé est incorrecte.'
            );
        }

        if (!rename($cheminAssemblage, $cheminFinal)) {
            @unlink($cheminAssemblage);
            throw new \RuntimeException(
                'Impossible de finaliser le fichier assemblé.'
            );
        }

        $typeMime = mime_content_type($cheminFinal);

        if (is_string($typeMime)) {
            $fichier->setTypeMime($typeMime);
        }

        $fichier
            ->setStatut('TERMINE')
            ->setTermineLe(new \DateTimeImmutable());

        foreach (glob($dossierJeton.'/*.part') ?: [] as $morceau) {
            @unlink($morceau);
        }

        @rmdir($dossierJeton);
    }
}