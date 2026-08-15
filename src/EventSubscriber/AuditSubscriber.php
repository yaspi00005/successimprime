<?php

namespace App\EventSubscriber;

use App\Entity\Achats;
use App\Entity\Articles;
use App\Entity\Clients;
use App\Entity\Commandes;
use App\Entity\Devis;
use App\Entity\Factures;
use App\Entity\Fournisseurs;
use App\Entity\JournalActivite;
use App\Entity\Paiements;
use App\Entity\Produits;
use App\Entity\User;
use Doctrine\Common\EventSubscriber;
use Doctrine\ORM\EntityManagerInterface;
use Doctrine\ORM\Event\OnFlushEventArgs;
use Doctrine\ORM\Event\PostFlushEventArgs;
use Doctrine\ORM\Events;
use Symfony\Bundle\SecurityBundle\Security;

/**
 * Journal d'activité automatique : capture création, modification et
 * suppression des entités métier principales avec leurs valeurs
 * avant/après en JSON (App\Entity\JournalActivite).
 *
 * Fonctionnement :
 * - onFlush : les valeurs "avant" sont encore disponibles pour les
 *   suppressions et les changesets de modification, on les capture ici.
 *   Pour les créations, l'identifiant n'existe pas encore : on garde
 *   juste une référence à l'entité et on termine le travail après.
 * - postFlush : les créations ont désormais un identifiant, on
 *   construit les entrées de journal et on les enregistre dans un
 *   flush séparé (JournalActivite n'étant pas une entité suivie,
 *   il n'y a pas de boucle).
 */
final class AuditSubscriber implements EventSubscriber
{
    private const ENTITES_SUIVIES = [
        Commandes::class,
        Clients::class,
        Paiements::class,
        Articles::class,
        Achats::class,
        Fournisseurs::class,
        Produits::class,
        Devis::class,
        Factures::class,
    ];

    /** @var JournalActivite[] */
    private array $enAttente = [];

    /** @var object[] */
    private array $creationsEnAttente = [];

    public function __construct(private readonly Security $security)
    {
    }

    public function getSubscribedEvents(): array
    {
        return [
            Events::onFlush,
            Events::postFlush,
        ];
    }

    public function onFlush(OnFlushEventArgs $args): void
    {
        $em = $args->getObjectManager();
        $uow = $em->getUnitOfWork();

        foreach ($uow->getScheduledEntityInsertions() as $entite) {
            if ($this->estSuivie($entite)) {
                $this->creationsEnAttente[] = $entite;
            }
        }

        foreach ($uow->getScheduledEntityUpdates() as $entite) {
            if (!$this->estSuivie($entite)) {
                continue;
            }

            [$avant, $apres] = $this->decomposerChangeSet($em, $uow->getEntityChangeSet($entite));

            if ($avant === [] && $apres === []) {
                continue;
            }

            $this->enAttente[] = $this->creerJournal($entite, JournalActivite::ACTION_MODIFICATION, $avant, $apres);
        }

        foreach ($uow->getScheduledEntityDeletions() as $entite) {
            if (!$this->estSuivie($entite)) {
                continue;
            }

            $this->enAttente[] = $this->creerJournal(
                $entite,
                JournalActivite::ACTION_SUPPRESSION,
                $this->extraireValeurs($em, $entite),
                null
            );
        }
    }

    public function postFlush(PostFlushEventArgs $args): void
    {
        if ($this->creationsEnAttente === [] && $this->enAttente === []) {
            return;
        }

        $em = $args->getObjectManager();

        foreach ($this->creationsEnAttente as $entite) {
            $this->enAttente[] = $this->creerJournal(
                $entite,
                JournalActivite::ACTION_CREATION,
                null,
                $this->extraireValeurs($em, $entite)
            );
        }

        $this->creationsEnAttente = [];

        $aEnregistrer = $this->enAttente;
        $this->enAttente = [];

        foreach ($aEnregistrer as $journal) {
            $em->persist($journal);
        }

        $em->flush();
    }

    private function estSuivie(object $entite): bool
    {
        foreach (self::ENTITES_SUIVIES as $classe) {
            if ($entite instanceof $classe) {
                return true;
            }
        }

        return false;
    }

    private function creerJournal(
        object $entite,
        string $action,
        ?array $avant,
        ?array $apres
    ): JournalActivite {
        $journal = new JournalActivite();
        $journal
            ->setEntite($this->nomCourt($entite))
            ->setEntiteId((int) ($entite->getId() ?? 0))
            ->setAction($action)
            ->setDonneesAvant($avant)
            ->setDonneesApres($apres);

        $utilisateur = $this->security->getUser();

        if ($utilisateur instanceof User) {
            $journal->setUtilisateur($utilisateur);
        }

        return $journal;
    }

    private function nomCourt(object $entite): string
    {
        $chemin = explode('\\', $entite::class);

        return end($chemin);
    }

    /**
     * @return array{0: array, 1: array}
     */
    private function decomposerChangeSet(EntityManagerInterface $em, array $changeSet): array
    {
        $avant = [];
        $apres = [];

        foreach ($changeSet as $champ => $paire) {
            [$ancienne, $nouvelle] = $paire;

            $avant[$champ] = $this->normaliserValeur($em, $ancienne);
            $apres[$champ] = $this->normaliserValeur($em, $nouvelle);
        }

        return [$avant, $apres];
    }

    /**
     * Extrait une représentation JSON-safe de l'entité : champs scalaires
     * tels quels, associations *-to-one réduites à leur identifiant,
     * collections *-to-many ignorées (pour éviter des journaux énormes
     * ou des chargements en cascade non désirés).
     */
    private function extraireValeurs(EntityManagerInterface $em, object $entite): array
    {
        $metadata = $em->getClassMetadata($entite::class);
        $valeurs = [];

        foreach ($metadata->getFieldNames() as $champ) {
            $valeurs[$champ] = $this->normaliserValeur($em, $metadata->getFieldValue($entite, $champ));
        }

        foreach ($metadata->getAssociationNames() as $association) {
            if (!$metadata->isSingleValuedAssociation($association)) {
                continue;
            }

            $valeurAssociation = $metadata->getFieldValue($entite, $association);
            $valeurs[$association . '_id'] = $valeurAssociation ? $this->recupererId($em, $valeurAssociation) : null;
        }

        return $valeurs;
    }

    private function normaliserValeur(EntityManagerInterface $em, mixed $valeur): mixed
    {
        if ($valeur instanceof \DateTimeInterface) {
            return $valeur->format(DATE_ATOM);
        }

        if ($valeur instanceof \BackedEnum) {
            return $valeur->value;
        }

        if (is_object($valeur)) {
            return $this->recupererId($em, $valeur);
        }

        return $valeur;
    }

    private function recupererId(EntityManagerInterface $em, object $entite): mixed
    {
        $metadata = $em->getClassMetadata($entite::class);
        $identifiants = $metadata->getIdentifierValues($entite);

        return $identifiants['id'] ?? (reset($identifiants) ?: null);
    }
}
