<?php

namespace App\Entity;

use App\Repository\CompteTresorerieRepository;
use Doctrine\DBAL\Types\Types;
use Doctrine\ORM\Mapping as ORM;
use Symfony\Component\Validator\Constraints as Assert;

#[ORM\Entity(repositoryClass: CompteTresorerieRepository::class)]
#[ORM\Table(name: 'compte_tresorerie')]
#[ORM\HasLifecycleCallbacks]
class CompteTresorerie
{
    public const TYPE_CAISSE = 'caisse';
    public const TYPE_ORANGE_MONEY = 'orange_money';
    public const TYPE_WAVE = 'wave';
    public const TYPE_BANQUE = 'banque';

    public const TYPES = [
        self::TYPE_CAISSE,
        self::TYPE_ORANGE_MONEY,
        self::TYPE_WAVE,
        self::TYPE_BANQUE,
    ];

    public const TYPES_LABELS = [
        self::TYPE_CAISSE => 'Caisse',
        self::TYPE_ORANGE_MONEY => 'Orange Money',
        self::TYPE_WAVE => 'Wave',
        self::TYPE_BANQUE => 'Compte bancaire',
    ];

    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    private ?int $id = null;

    /*
     * Code interne unique du compte.
     *
     * Exemples :
     * CAISSE-PRINCIPALE
     * OM-COMMERCIAL
     * WAVE-PRINCIPAL
     * BDM-001
     */
    #[ORM\Column(length: 50, unique: true)]
    #[Assert\NotBlank]
    #[Assert\Length(max: 50)]
    private string $code = '';

    #[ORM\Column(length: 150)]
    #[Assert\NotBlank]
    #[Assert\Length(max: 150)]
    private string $nom = '';

    #[ORM\Column(length: 30)]
    #[Assert\NotBlank]
    #[Assert\Choice(callback: [self::class, 'getTypesDisponibles'])]
    private string $type = self::TYPE_CAISSE;

    /*
     * Nom de la banque.
     * Ce champ sera utilisé uniquement lorsque type = banque.
     *
     * Nous pourrons ensuite le remplacer par une relation ManyToOne
     * si votre application possède déjà une entité Banque.
     */
    #[ORM\Column(length: 150, nullable: true)]
    #[Assert\Length(max: 150)]
    private ?string $nomBanque = null;

    /*
     * Numéro du compte bancaire, numéro Orange Money,
     * numéro Wave ou autre référence.
     */
    #[ORM\Column(length: 100, nullable: true)]
    #[Assert\Length(max: 100)]
    private ?string $numeroCompte = null;

    #[ORM\Column(length: 150, nullable: true)]
    #[Assert\Length(max: 150)]
    private ?string $titulaireCompte = null;

    /*
     * Les montants sont enregistrés en nombres entiers,
     * car le FCFA ne nécessite pas de décimales.
     */
    #[ORM\Column(options: ['default' => 0])]
    #[Assert\PositiveOrZero]
    private int $soldeInitial = 0;

    #[ORM\Column(options: ['default' => 0])]
    private int $soldeActuel = 0;

    #[ORM\Column(length: 10, options: ['default' => 'XOF'])]
    #[Assert\NotBlank]
    #[Assert\Length(max: 10)]
    private string $devise = 'XOF';

    /*
     * Si false, aucun débit supérieur au solde actuel
     * ne devra être autorisé.
     */
    #[ORM\Column(options: ['default' => false])]
    private bool $autoriserDecouvert = false;

    #[ORM\Column(options: ['default' => true])]
    private bool $actif = true;

    #[ORM\Column(type: Types::TEXT, nullable: true)]
    private ?string $description = null;

    #[ORM\Column(type: Types::DATETIME_IMMUTABLE)]
    private ?\DateTimeImmutable $dateCreation = null;

    #[ORM\Column(
        type: Types::DATETIME_IMMUTABLE,
        nullable: true
    )]
    private ?\DateTimeImmutable $dateModification = null;

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getCode(): string
    {
        return $this->code;
    }

    public function setCode(string $code): static
    {
        $code = strtoupper(trim($code));
        $code = preg_replace('/[^A-Z0-9]+/', '-', $code) ?? '';
        $code = trim($code, '-');

        $this->code = $code;

        return $this;
    }

    public function getNom(): string
    {
        return $this->nom;
    }

    public function setNom(string $nom): static
    {
        $this->nom = trim($nom);

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
                sprintf(
                    'Le type de compte "%s" est invalide.',
                    $type
                )
            );
        }

        $this->type = $type;

        /*
         * Les informations bancaires ne doivent pas rester
         * attachées à une caisse ou à un portefeuille mobile.
         */
        if ($type !== self::TYPE_BANQUE) {
            $this->nomBanque = null;
        }

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

    public function getNomBanque(): ?string
    {
        return $this->nomBanque;
    }

    public function setNomBanque(?string $nomBanque): static
    {
        $nomBanque = $nomBanque !== null
            ? trim($nomBanque)
            : null;

        $this->nomBanque = $nomBanque !== ''
            ? $nomBanque
            : null;

        return $this;
    }

    public function getNumeroCompte(): ?string
    {
        return $this->numeroCompte;
    }

    public function setNumeroCompte(?string $numeroCompte): static
    {
        $numeroCompte = $numeroCompte !== null
            ? trim($numeroCompte)
            : null;

        $this->numeroCompte = $numeroCompte !== ''
            ? $numeroCompte
            : null;

        return $this;
    }

    public function getTitulaireCompte(): ?string
    {
        return $this->titulaireCompte;
    }

    public function setTitulaireCompte(
        ?string $titulaireCompte
    ): static {
        $titulaireCompte = $titulaireCompte !== null
            ? trim($titulaireCompte)
            : null;

        $this->titulaireCompte = $titulaireCompte !== ''
            ? $titulaireCompte
            : null;

        return $this;
    }

    public function getSoldeInitial(): int
    {
        return $this->soldeInitial;
    }

    public function setSoldeInitial(?int $soldeInitial): static
    {
        $soldeInitial = max(0, $soldeInitial ?? 0);

        /*
         * Lors de la création du compte, le solde actuel
         * commence avec le solde initial.
         *
         * Après création, le solde actuel sera modifié
         * uniquement par les mouvements de trésorerie.
         */
        if ($this->id === null) {
            $this->soldeActuel = $soldeInitial;
        }

        $this->soldeInitial = $soldeInitial;

        return $this;
    }

    public function getSoldeActuel(): int
    {
        return $this->soldeActuel;
    }

    /*
     * Cette méthode ne devra pas être utilisée directement
     * depuis un formulaire. Le solde doit être modifié par
     * les services de mouvement et de transfert.
     */
    public function setSoldeActuel(int $soldeActuel): static
    {
        if (!$this->autoriserDecouvert && $soldeActuel < 0) {
            throw new \LogicException(
                'Le solde du compte ne peut pas être négatif.'
            );
        }

        $this->soldeActuel = $soldeActuel;

        return $this;
    }

    public function crediter(int $montant): static
    {
        if ($montant <= 0) {
            throw new \InvalidArgumentException(
                'Le montant à créditer doit être supérieur à zéro.'
            );
        }

        $this->soldeActuel += $montant;

        return $this;
    }

    public function debiter(int $montant): static
    {
        if ($montant <= 0) {
            throw new \InvalidArgumentException(
                'Le montant à débiter doit être supérieur à zéro.'
            );
        }

        $nouveauSolde = $this->soldeActuel - $montant;

        if (!$this->autoriserDecouvert && $nouveauSolde < 0) {
            throw new \LogicException(
                sprintf(
                    'Solde insuffisant sur le compte "%s".',
                    $this->nom
                )
            );
        }

        $this->soldeActuel = $nouveauSolde;

        return $this;
    }

    public function peutEtreDebite(int $montant): bool
    {
        if ($montant <= 0) {
            return false;
        }

        return $this->autoriserDecouvert
            || $this->soldeActuel >= $montant;
    }

    public function getDevise(): string
    {
        return $this->devise;
    }

    public function setDevise(?string $devise): static
    {
        $devise = strtoupper(trim($devise ?? ''));

        $this->devise = $devise !== ''
            ? $devise
            : 'XOF';

        return $this;
    }

    public function isAutoriserDecouvert(): bool
    {
        return $this->autoriserDecouvert;
    }

    public function setAutoriserDecouvert(
        bool $autoriserDecouvert
    ): static {
        $this->autoriserDecouvert = $autoriserDecouvert;

        return $this;
    }

    public function isActif(): bool
    {
        return $this->actif;
    }

    public function setActif(bool $actif): static
    {
        $this->actif = $actif;

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

    public function getDateCreation(): ?\DateTimeImmutable
    {
        return $this->dateCreation;
    }

    public function setDateCreation(
        \DateTimeImmutable $dateCreation
    ): static {
        $this->dateCreation = $dateCreation;

        return $this;
    }

    public function getDateModification(): ?\DateTimeImmutable
    {
        return $this->dateModification;
    }

    public function setDateModification(
        ?\DateTimeImmutable $dateModification
    ): static {
        $this->dateModification = $dateModification;

        return $this;
    }

    public function estCompteBancaire(): bool
    {
        return $this->type === self::TYPE_BANQUE;
    }

    public function estCaisse(): bool
    {
        return $this->type === self::TYPE_CAISSE;
    }

    public function estMobileMoney(): bool
    {
        return in_array(
            $this->type,
            [
                self::TYPE_ORANGE_MONEY,
                self::TYPE_WAVE,
            ],
            true
        );
    }

    #[ORM\PrePersist]
    public function initialiserDates(): void
    {
        $maintenant = new \DateTimeImmutable();

        $this->dateCreation ??= $maintenant;
        $this->dateModification = $maintenant;
    }

    #[ORM\PreUpdate]
    public function actualiserDateModification(): void
    {
        $this->dateModification = new \DateTimeImmutable();
    }

    public function __toString(): string
    {
        return sprintf(
            '%s — %s',
            $this->nom,
            $this->getTypeLabel()
        );
    }
}