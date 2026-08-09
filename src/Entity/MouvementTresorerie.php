<?php

namespace App\Entity;

use App\Repository\MouvementTresorerieRepository;
use Doctrine\DBAL\Types\Types;
use Doctrine\ORM\Mapping as ORM;
use Symfony\Component\Validator\Constraints as Assert;
use Symfony\Component\Validator\Context\ExecutionContextInterface;

#[ORM\Entity(repositoryClass: MouvementTresorerieRepository::class)]
#[ORM\Table(name: 'mouvement_tresorerie')]
#[ORM\Index(
    name: 'idx_mouvement_type',
    columns: ['type']
)]
#[ORM\Index(
    name: 'idx_mouvement_statut',
    columns: ['statut']
)]
#[ORM\Index(
    name: 'idx_mouvement_date',
    columns: ['date_operation']
)]
#[ORM\HasLifecycleCallbacks]
class MouvementTresorerie
{
    public const TYPE_ENCAISSEMENT = 'encaissement';
    public const TYPE_DECAISSEMENT = 'decaissement';
    public const TYPE_TRANSFERT = 'transfert';

    public const TYPES = [
        self::TYPE_ENCAISSEMENT,
        self::TYPE_DECAISSEMENT,
        self::TYPE_TRANSFERT,
    ];

    public const TYPES_LABELS = [
        self::TYPE_ENCAISSEMENT => 'Encaissement',
        self::TYPE_DECAISSEMENT => 'Décaissement',
        self::TYPE_TRANSFERT => 'Transfert',
    ];

    public const STATUT_EN_ATTENTE = 'en_attente';
    public const STATUT_VALIDE = 'valide';
    public const STATUT_ANNULE = 'annule';

    public const STATUTS = [
        self::STATUT_EN_ATTENTE,
        self::STATUT_VALIDE,
        self::STATUT_ANNULE,
    ];

    public const STATUTS_LABELS = [
        self::STATUT_EN_ATTENTE => 'En attente',
        self::STATUT_VALIDE => 'Validé',
        self::STATUT_ANNULE => 'Annulé',
    ];

    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    private ?int $id = null;

    #[ORM\Column(length: 50, unique: true)]
    #[Assert\NotBlank(message: 'La référence est obligatoire.')]
    #[Assert\Length(
        max: 50,
        maxMessage: 'La référence ne peut pas dépasser {{ limit }} caractères.'
    )]
    private string $reference = '';

    #[ORM\Column(length: 30)]
    #[Assert\NotBlank]
    #[Assert\Choice(callback: [self::class, 'getTypesDisponibles'])]
    private string $type = self::TYPE_ENCAISSEMENT;

    /*
     * Encaissement :
     * compteDestination obligatoire.
     *
     * Décaissement :
     * compteSource obligatoire.
     *
     * Transfert :
     * compteSource et compteDestination obligatoires.
     */
    #[ORM\ManyToOne]
    #[ORM\JoinColumn(
        name: 'compte_source_id',
        nullable: true,
        onDelete: 'RESTRICT'
    )]
    private ?CompteTresorerie $compteSource = null;

    #[ORM\ManyToOne]
    #[ORM\JoinColumn(
        name: 'compte_destination_id',
        nullable: true,
        onDelete: 'RESTRICT'
    )]
    private ?CompteTresorerie $compteDestination = null;

    #[ORM\Column]
    #[Assert\NotNull]
    #[Assert\Positive(
        message: 'Le montant doit être supérieur à zéro.'
    )]
    private int $montant = 0;

    #[ORM\Column(length: 10, options: ['default' => 'XOF'])]
    #[Assert\NotBlank]
    #[Assert\Length(max: 10)]
    private string $devise = 'XOF';

    #[ORM\Column(length: 50, nullable: true)]
    #[Assert\Length(max: 50)]
    private ?string $modePaiement = null;

    /*
     * Numéro de reçu, référence bancaire,
     * numéro de transaction mobile, etc.
     */
    #[ORM\Column(length: 100, nullable: true)]
    #[Assert\Length(max: 100)]
    private ?string $referenceExterne = null;

    #[ORM\Column(length: 255)]
    #[Assert\NotBlank]
    #[Assert\Length(max: 255)]
    private string $libelle = '';

    #[ORM\Column(type: Types::TEXT, nullable: true)]
    private ?string $description = null;

    #[ORM\Column(length: 30)]
    #[Assert\Choice(callback: [self::class, 'getStatutsDisponibles'])]
    private string $statut = self::STATUT_EN_ATTENTE;

    #[ORM\Column(type: Types::DATETIME_IMMUTABLE)]
    private ?\DateTimeImmutable $dateOperation = null;

    #[ORM\Column(type: Types::DATETIME_IMMUTABLE)]
    private ?\DateTimeImmutable $dateCreation = null;

    #[ORM\Column(
        type: Types::DATETIME_IMMUTABLE,
        nullable: true
    )]
    private ?\DateTimeImmutable $dateValidation = null;

    #[ORM\Column(
        type: Types::DATETIME_IMMUTABLE,
        nullable: true
    )]
    private ?\DateTimeImmutable $dateAnnulation = null;

    #[ORM\Column(type: Types::TEXT, nullable: true)]
    private ?string $motifAnnulation = null;

    #[ORM\PrePersist]
    public function initialiserDates(): void
    {
        $maintenant = new \DateTimeImmutable();

        if ($this->dateCreation === null) {
            $this->dateCreation = $maintenant;
        }

        if ($this->dateOperation === null) {
            $this->dateOperation = $maintenant;
        }
    }

    #[Assert\Callback]
    public function validerComptes(
        ExecutionContextInterface $context
    ): void {
        if (
            $this->type === self::TYPE_ENCAISSEMENT
            && $this->compteDestination === null
        ) {
            $context
                ->buildViolation(
                    'Sélectionnez le compte qui reçoit l’encaissement.'
                )
                ->atPath('compteDestination')
                ->addViolation();
        }

        if (
            $this->type === self::TYPE_DECAISSEMENT
            && $this->compteSource === null
        ) {
            $context
                ->buildViolation(
                    'Sélectionnez le compte à débiter.'
                )
                ->atPath('compteSource')
                ->addViolation();
        }

        if ($this->type === self::TYPE_TRANSFERT) {
            if ($this->compteSource === null) {
                $context
                    ->buildViolation(
                        'Sélectionnez le compte source.'
                    )
                    ->atPath('compteSource')
                    ->addViolation();
            }

            if ($this->compteDestination === null) {
                $context
                    ->buildViolation(
                        'Sélectionnez le compte destination.'
                    )
                    ->atPath('compteDestination')
                    ->addViolation();
            }

            if (
                $this->compteSource !== null
                && $this->compteDestination !== null
                && $this->compteSource === $this->compteDestination
            ) {
                $context
                    ->buildViolation(
                        'Les comptes source et destination doivent être différents.'
                    )
                    ->atPath('compteDestination')
                    ->addViolation();
            }
        }
    }
    #[ORM\OneToOne(
        inversedBy: 'mouvementTresorerie'
    )]
    #[ORM\JoinColumn(
        name: 'paiement_id',
        referencedColumnName: 'id',
        nullable: true,
        onDelete: 'SET NULL'
    )]
    private ?Paiements $paiement = null;

    #[ORM\ManyToOne]
    #[ORM\JoinColumn(
        name: 'agent_id',
        nullable: true,
        onDelete: 'SET NULL'
    )]
    private ?User $agent = null;
    public function getId(): ?int
    {
        return $this->id;
    }

    public function getReference(): string
    {
        return $this->reference;
    }

    public function setReference(string $reference): static
    {
        $reference = strtoupper(trim($reference));

        $reference = preg_replace(
            '/[^A-Z0-9\-]+/',
            '-',
            $reference
        ) ?? '';

        $this->reference = trim($reference, '-');

        return $this;
    }

    public function getType(): string
    {
        return $this->type;
    }

    public function setType(string $type): static
    {
        $type = strtolower(trim($type));

        if (!in_array($type, self::TYPES, true)) {
            throw new \InvalidArgumentException(
                'Le type de mouvement est invalide.'
            );
        }

        $this->type = $type;

        return $this;
    }

    public function getTypeLabel(): string
    {
        return self::TYPES_LABELS[$this->type] ?? $this->type;
    }

    public static function getTypesDisponibles(): array
    {
        return self::TYPES;
    }

    public static function getTypesPourFormulaire(): array
    {
        return array_flip(self::TYPES_LABELS);
    }

    public function getCompteSource(): ?CompteTresorerie
    {
        return $this->compteSource;
    }

    public function setCompteSource(
        ?CompteTresorerie $compteSource
    ): static {
        $this->compteSource = $compteSource;

        return $this;
    }

    public function getCompteDestination(): ?CompteTresorerie
    {
        return $this->compteDestination;
    }

    public function setCompteDestination(
        ?CompteTresorerie $compteDestination
    ): static {
        $this->compteDestination = $compteDestination;

        return $this;
    }

    public function getMontant(): int
    {
        return $this->montant;
    }

    public function setMontant(?int $montant): static
    {
        $this->montant = $montant ?? 0;

        return $this;
    }

    public function getDevise(): string
    {
        return $this->devise;
    }

    public function setDevise(string $devise): static
    {
        $this->devise = strtoupper(trim($devise));

        return $this;
    }

    public function getModePaiement(): ?string
    {
        return $this->modePaiement;
    }

    public function setModePaiement(
        ?string $modePaiement
    ): static {
        $modePaiement = $modePaiement !== null
            ? trim($modePaiement)
            : null;

        $this->modePaiement = $modePaiement !== ''
            ? $modePaiement
            : null;

        return $this;
    }

    public function getReferenceExterne(): ?string
    {
        return $this->referenceExterne;
    }

    public function setReferenceExterne(
        ?string $referenceExterne
    ): static {
        $referenceExterne = $referenceExterne !== null
            ? trim($referenceExterne)
            : null;

        $this->referenceExterne = $referenceExterne !== ''
            ? $referenceExterne
            : null;

        return $this;
    }

    public function getLibelle(): string
    {
        return $this->libelle;
    }

    public function setLibelle(string $libelle): static
    {
        $this->libelle = trim($libelle);

        return $this;
    }

    public function getDescription(): ?string
    {
        return $this->description;
    }

    public function setDescription(?string $description): static
    {
        $description = $description !== null
            ? trim($description)
            : null;

        $this->description = $description !== ''
            ? $description
            : null;

        return $this;
    }

    public function getStatut(): string
    {
        return $this->statut;
    }

    public function setStatut(string $statut): static
    {
        if (!in_array($statut, self::STATUTS, true)) {
            throw new \InvalidArgumentException(
                'Le statut du mouvement est invalide.'
            );
        }

        $this->statut = $statut;

        return $this;
    }

    public function getStatutLabel(): string
    {
        return self::STATUTS_LABELS[$this->statut]
            ?? $this->statut;
    }

    public static function getStatutsDisponibles(): array
    {
        return self::STATUTS;
    }

    public function isEnAttente(): bool
    {
        return $this->statut === self::STATUT_EN_ATTENTE;
    }

    public function isValide(): bool
    {
        return $this->statut === self::STATUT_VALIDE;
    }

    public function isAnnule(): bool
    {
        return $this->statut === self::STATUT_ANNULE;
    }

    public function necessiteValidationManuelle(): bool
    {
        return $this->compteSource?->estCompteBancaire()
            || $this->compteDestination?->estCompteBancaire();
    }

    public function getDateOperation(): ?\DateTimeImmutable
    {
        return $this->dateOperation;
    }

    public function setDateOperation(
        ?\DateTimeImmutable $dateOperation
    ): static {
        $this->dateOperation = $dateOperation;

        return $this;
    }

    public function getDateCreation(): ?\DateTimeImmutable
    {
        return $this->dateCreation;
    }

    public function getDateValidation(): ?\DateTimeImmutable
    {
        return $this->dateValidation;
    }

    public function setDateValidation(?\DateTimeImmutable $dateValidation): static
    {
        $this->dateValidation = $dateValidation;

        return $this;
    }

    public function marquerCommeValide(): static
    {
        if ($this->isAnnule()) {
            throw new \LogicException(
                'Un mouvement annulé ne peut pas être validé.'
            );
        }

        $this->statut = self::STATUT_VALIDE;
        $this->dateValidation = new \DateTimeImmutable();

        return $this;
    }

    public function getDateAnnulation(): ?\DateTimeImmutable
    {
        return $this->dateAnnulation;
    }

    public function getMotifAnnulation(): ?string
    {
        return $this->motifAnnulation;
    }

    public function marquerCommeAnnule(
        string $motif
    ): static {
        if ($this->isValide()) {
            throw new \LogicException(
                'Un mouvement déjà validé doit être contrepassé.'
            );
        }

        $motif = trim($motif);

        if ($motif === '') {
            throw new \InvalidArgumentException(
                'Le motif d’annulation est obligatoire.'
            );
        }

        $this->statut = self::STATUT_ANNULE;
        $this->motifAnnulation = $motif;
        $this->dateAnnulation = new \DateTimeImmutable();

        return $this;
    }
    public function getPaiement(): ?Paiements
    {
        return $this->paiement;
    }

    public function setPaiement(?Paiements $paiement): static
    {
        $this->paiement = $paiement;

        if (
            $paiement !== null
            && $paiement->getMouvementTresorerie() !== $this
        ) {
            $paiement->setMouvementTresorerie($this);
        }

        return $this;
    }
    public function getAgent(): ?User
    {
        return $this->agent;
    }

    public function setAgent(?User $agent): static
    {
        $this->agent = $agent;

        return $this;
    }
}
