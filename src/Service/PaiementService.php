<?php

namespace App\Service;

use App\Entity\MouvementTresorerie;
use App\Entity\Paiements;
use App\Entity\User;
use Doctrine\DBAL\LockMode;
use Doctrine\ORM\EntityManagerInterface;

final class PaiementService
{
    public function __construct(
        private readonly EntityManagerInterface $entityManager
    ) {
    }

    /**
     * Valide un paiement, crédite le compte de trésorerie
     * et crée son mouvement dans une transaction unique.
     */
    public function valider(
        Paiements $paiement,
        User $utilisateur
    ): MouvementTresorerie {
        $connexion = $this->entityManager->getConnection();

        $connexion->beginTransaction();

        try {
            /*
             * Si le paiement existe déjà, on le verrouille afin
             * d’empêcher deux validations simultanées.
             */
            if ($paiement->getId() !== null) {
                $this->entityManager->lock(
                    $paiement,
                    LockMode::PESSIMISTIC_WRITE
                );

                /*
                 * Recharge les relations depuis la base, notamment
                 * mouvementTresorerie, avant le contrôle anti-doublon.
                 */
                $this->entityManager->refresh($paiement);
            } else {
                /*
                 * Permet également de valider directement
                 * un nouveau paiement.
                 */
                $this->entityManager->persist($paiement);
                $this->entityManager->flush();
            }

            if (!$paiement->estEnAttente()) {
                throw new \LogicException(
                    'Seul un paiement en attente peut être validé.'
                );
            }

            if ($paiement->getMouvementTresorerie() !== null) {
                throw new \LogicException(
                    'Ce paiement possède déjà un mouvement de trésorerie.'
                );
            }

            $compte = $paiement->getCompteTresorerie();

            if ($compte === null) {
                throw new \LogicException(
                    'Le compte de trésorerie du paiement est obligatoire.'
                );
            }

            /*
             * Le verrouillage du compte protège le solde contre
             * plusieurs encaissements exécutés simultanément.
             */
            if ($compte->getId() !== null) {
                $this->entityManager->lock(
                    $compte,
                    LockMode::PESSIMISTIC_WRITE
                );

                $this->entityManager->refresh($compte);
            }

            $paiement->verifierCompatibiliteCompte();
            $paiement->validerPar($utilisateur);

            $mouvement = new MouvementTresorerie();

            $mouvement
                ->setCompteTresorerie($compte)
                ->setPaiement($paiement)
                ->setSens(MouvementTresorerie::SENS_CREDIT)
                ->setOrigine(MouvementTresorerie::ORIGINE_PAIEMENT)
                ->setMontant($paiement->getMontant())
                ->setReferenceExterne(
                    $this->construireReferencePaiement($paiement)
                )
                ->setLibelle(
                    $this->construireLibellePaiement($paiement)
                )
                ->setObservation($paiement->getObservation());

            /*
             * Cette méthode crédite le compte et mémorise
             * le solde avant et après.
             */
            $mouvement->valider();

            $this->entityManager->persist($mouvement);
            $this->entityManager->flush();

            $connexion->commit();

            return $mouvement;
        } catch (\Throwable $exception) {
            if ($connexion->isTransactionActive()) {
                $connexion->rollBack();
            }

            throw $exception;
        }
    }

    /**
     * Annule un paiement validé et restaure le solde
     * du compte de trésorerie.
     */
    public function annuler(
        Paiements $paiement,
        string $motif,
        User $utilisateur
    ): void {
        $motif = trim($motif);

        if ($motif === '') {
            throw new \InvalidArgumentException(
                'Le motif de l’annulation est obligatoire.'
            );
        }

        if ($paiement->getId() === null) {
            throw new \LogicException(
                'Un paiement non enregistré ne peut pas être annulé.'
            );
        }

        $connexion = $this->entityManager->getConnection();

        $connexion->beginTransaction();

        try {
            $this->entityManager->lock(
                $paiement,
                LockMode::PESSIMISTIC_WRITE
            );

            $this->entityManager->refresh($paiement);

            if (!$paiement->estValide()) {
                throw new \LogicException(
                    'Seul un paiement validé peut être annulé.'
                );
            }

            $mouvement = $paiement->getMouvementTresorerie();

            if ($mouvement === null) {
                throw new \LogicException(
                    'Aucun mouvement de trésorerie n’est associé à ce paiement.'
                );
            }

            $this->entityManager->lock(
                $mouvement,
                LockMode::PESSIMISTIC_WRITE
            );

            if (!$mouvement->estValide()) {
                throw new \LogicException(
                    'Le mouvement de ce paiement n’est pas dans un état annulable.'
                );
            }

            $compte = $paiement->getCompteTresorerie();

            if ($compte === null) {
                throw new \LogicException(
                    'Aucun compte de trésorerie n’est associé au paiement.'
                );
            }

            $this->entityManager->lock(
                $compte,
                LockMode::PESSIMISTIC_WRITE
            );

            $this->entityManager->refresh($compte);

            /*
             * annuler() exécute l’opération inverse :
             * le crédit initial devient un débit.
             */
            $mouvement->annuler($motif);
            $paiement->annuler($motif, $utilisateur);

            $this->entityManager->flush();

            $connexion->commit();
        } catch (\Throwable $exception) {
            if ($connexion->isTransactionActive()) {
                $connexion->rollBack();
            }

            throw $exception;
        }
    }

    /**
     * Rejette un paiement encore en attente.
     * Aucun mouvement de trésorerie n’est créé.
     */
    public function rejeter(
        Paiements $paiement,
        string $motif,
        User $utilisateur
    ): void {
        $motif = trim($motif);

        if ($motif === '') {
            throw new \InvalidArgumentException(
                'Le motif du rejet est obligatoire.'
            );
        }

        $connexion = $this->entityManager->getConnection();

        $connexion->beginTransaction();

        try {
            if ($paiement->getId() !== null) {
                $this->entityManager->lock(
                    $paiement,
                    LockMode::PESSIMISTIC_WRITE
                );

                $this->entityManager->refresh($paiement);
            }

            if ($paiement->getMouvementTresorerie() !== null) {
                throw new \LogicException(
                    'Un paiement possédant un mouvement ne peut pas être rejeté.'
                );
            }

            $paiement->rejeter($motif, $utilisateur);

            $this->entityManager->persist($paiement);
            $this->entityManager->flush();

            $connexion->commit();
        } catch (\Throwable $exception) {
            if ($connexion->isTransactionActive()) {
                $connexion->rollBack();
            }

            throw $exception;
        }
    }

    private function construireReferencePaiement(
        Paiements $paiement
    ): string {
        if (
            $paiement->getReference() !== null
            && trim($paiement->getReference()) !== ''
        ) {
            return trim($paiement->getReference());
        }

        return sprintf(
            'PAIEMENT-%d',
            $paiement->getId()
        );
    }

    private function construireLibellePaiement(
        Paiements $paiement
    ): string {
        $numeroCommande = $paiement->getCommande()?->getId();

        return sprintf(
            'Paiement de la commande #%s par %s',
            $numeroCommande ?? 'N/A',
            $paiement->getModeLabel()
        );
    }
}