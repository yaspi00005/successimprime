<?php

namespace App\Entity;

use App\Repository\ProduitConfigurationRepository;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\DBAL\Types\Types;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity(repositoryClass: ProduitConfigurationRepository::class)]
#[ORM\Table(name: 'produit_configuration')]
#[ORM\UniqueConstraint(
    name: 'uniq_produit_configuration',
    columns: [
        'produit_id',
        'type_impression_id',
        'support_id',
        'format_id',
    ]
)]
class ProduitConfiguration
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    private ?int $id = null;

    #[ORM\ManyToOne(inversedBy: 'configurations')]
    #[ORM\JoinColumn(
        name: 'produit_id',
        referencedColumnName: 'id',
        nullable: false,
        onDelete: 'CASCADE'
    )]
    private ?Produits $produit = null;

    #[ORM\ManyToOne]
    #[ORM\JoinColumn(
        name: 'type_impression_id',
        referencedColumnName: 'id',
        nullable: false,
        onDelete: 'CASCADE'
    )]
    private ?TypesImpression $typeImpression = null;

    #[ORM\ManyToOne]
    #[ORM\JoinColumn(
        name: 'support_id',
        referencedColumnName: 'id',
        nullable: false,
        onDelete: 'CASCADE'
    )]
    private ?Supports $support = null;

    #[ORM\ManyToOne]
    #[ORM\JoinColumn(
        name: 'format_id',
        referencedColumnName: 'id',
        nullable: false,
        onDelete: 'CASCADE'
    )]
    private ?Format $format = null;

    #[ORM\Column]
    private bool $active = true;

    #[ORM\Column]
    private int $ordre = 10;

    #[ORM\Column(type: Types::TEXT, nullable: true)]
    private ?string $description = null;

    /**
     * Prix normal B2C de cette configuration.
     */
    #[ORM\Column(nullable: true)]
    private ?int $prixBase = null;

    /**
     * Modes possibles :
     *
     * forfait
     * unite
     * metre
     * metre_carre
     * heure
     */
    #[ORM\Column(length: 30)]
    private string $modeCalcul = 'forfait';

    #[ORM\Column]
    private int $quantiteMinimale = 1;

    #[ORM\Column(nullable: true)]
    private ?int $quantiteMaximale = null;

    /**
     * @var Collection<int, ProduitConfigurationFinition>
     */
    #[ORM\OneToMany(
        targetEntity: ProduitConfigurationFinition::class,
        mappedBy: 'produitConfiguration',
        cascade: ['persist', 'remove'],
        orphanRemoval: true
    )]
    #[ORM\OrderBy(['ordre' => 'ASC'])]
    private Collection $configurationFinitions;

    public function __construct()
    {
        $this->configurationFinitions = new ArrayCollection();
    }

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getProduit(): ?Produits
    {
        return $this->produit;
    }

    public function setProduit(?Produits $produit): static
    {
        $this->produit = $produit;

        return $this;
    }

    public function getTypeImpression(): ?TypesImpression
    {
        return $this->typeImpression;
    }

    public function setTypeImpression(
        ?TypesImpression $typeImpression
    ): static {
        $this->typeImpression = $typeImpression;

        return $this;
    }

    public function getSupport(): ?Supports
    {
        return $this->support;
    }

    public function setSupport(?Supports $support): static
    {
        $this->support = $support;

        return $this;
    }

    public function getFormat(): ?Format
    {
        return $this->format;
    }

    public function setFormat(?Format $format): static
    {
        $this->format = $format;

        return $this;
    }

    public function isActive(): bool
    {
        return $this->active;
    }

    public function setActive(bool $active): static
    {
        $this->active = $active;

        return $this;
    }

    public function getOrdre(): int
    {
        return $this->ordre;
    }

    public function setOrdre(int $ordre): static
    {
        $this->ordre = max(0, $ordre);

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

    public function getPrixBase(): ?int
    {
        return $this->prixBase;
    }

    public function setPrixBase(?int $prixBase): static
    {
        $this->prixBase = $prixBase !== null
            ? max(0, $prixBase)
            : null;

        return $this;
    }

    public function getModeCalcul(): string
    {
        return $this->modeCalcul;
    }

    public function setModeCalcul(string $modeCalcul): static
    {
        $modesAutorises = [
            'forfait',
            'unite',
            'metre',
            'metre_carre',
            'heure',
        ];

        $modeCalcul = strtolower(trim($modeCalcul));

        $this->modeCalcul = in_array(
            $modeCalcul,
            $modesAutorises,
            true
        )
            ? $modeCalcul
            : 'forfait';

        return $this;
    }

    public function getQuantiteMinimale(): int
    {
        return $this->quantiteMinimale;
    }

    public function setQuantiteMinimale(
        int $quantiteMinimale
    ): static {
        $this->quantiteMinimale = max(
            1,
            $quantiteMinimale
        );

        if (
            $this->quantiteMaximale !== null
            && $this->quantiteMaximale < $this->quantiteMinimale
        ) {
            $this->quantiteMaximale = $this->quantiteMinimale;
        }

        return $this;
    }

    public function getQuantiteMaximale(): ?int
    {
        return $this->quantiteMaximale;
    }

    public function setQuantiteMaximale(
        ?int $quantiteMaximale
    ): static {
        if ($quantiteMaximale === null) {
            $this->quantiteMaximale = null;

            return $this;
        }

        $this->quantiteMaximale = max(
            $this->quantiteMinimale,
            $quantiteMaximale
        );

        return $this;
    }

    /**
     * @return Collection<int, ProduitConfigurationFinition>
     */
    public function getConfigurationFinitions(): Collection
    {
        return $this->configurationFinitions;
    }

    public function addConfigurationFinition(
        ProduitConfigurationFinition $configurationFinition
    ): static {
        if (
            !$this->configurationFinitions
                ->contains($configurationFinition)
        ) {
            $this->configurationFinitions->add(
                $configurationFinition
            );

            $configurationFinition
                ->setProduitConfiguration($this);
        }

        return $this;
    }

    public function removeConfigurationFinition(
        ProduitConfigurationFinition $configurationFinition
    ): static {
        if (
            $this->configurationFinitions
                ->removeElement($configurationFinition)
            && $configurationFinition
                ->getProduitConfiguration() === $this
        ) {
            $configurationFinition
                ->setProduitConfiguration(null);
        }

        return $this;
    }

    public function __toString(): string
    {
        return sprintf(
            '%s — %s — %s — %s',
            $this->produit?->getNom() ?? 'Produit',
            $this->typeImpression?->getNom() ?? 'Type d’impression',
            $this->support?->getNom() ?? 'Support',
            $this->format?->getNom() ?? 'Format'
        );
    }
}