<?php

namespace App\Entity;

use App\Repository\ProduitsRepository;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity(repositoryClass: ProduitsRepository::class)]
class Produits
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    private ?int $id = null;

    #[ORM\Column(length: 255, unique: true)]
    private ?string $nom = null;

    #[ORM\Column(length: 1000)]
    private ?string $description = null;

    #[ORM\Column]
    private ?bool $publie = true;

    #[ORM\Column]
    private ?int $ordre = 10;

       #[ORM\Column(length: 50, unique: true)]
    private ?string $code = null;

    #[ORM\Column(nullable: true)]
    private ?float $prixBase = null;

    #[ORM\Column]
    private ?bool $personnalisable = true;

    #[ORM\Column]
    private ?bool $actif = true;

    /**
     * Catégorie
     */
    #[ORM\ManyToOne(inversedBy: 'produits')]
    #[ORM\JoinColumn(nullable: false)]
    private ?CategorieProduit $categorieProduit = null;

    /**
     * Types d'impression compatibles
     */
    #[ORM\ManyToMany(targetEntity: TypesImpression::class)]
    private Collection $typesImpressions;

    /**
     * Supports compatibles
     */
    #[ORM\ManyToMany(targetEntity: Supports::class)]
    private Collection $supports;

    /**
     * Formats compatibles
     */
    #[ORM\ManyToMany(targetEntity: Format::class)]
    private Collection $formats;

    /**
     * Finitions compatibles
     */
    #[ORM\ManyToMany(targetEntity: Finition::class)]
    private Collection $finitions;

    /**
     * Détails des commandes
     */
    #[ORM\OneToMany(
        targetEntity: CommandesDetails::class,
        mappedBy: 'produit'
    )]
    private Collection $commandesDetails;

    public function __construct()
    {
        $this->typesImpressions = new ArrayCollection();
        $this->supports = new ArrayCollection();
        $this->formats = new ArrayCollection();
        $this->finitions = new ArrayCollection();
        $this->commandesDetails = new ArrayCollection();
    }

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getNom(): ?string
    {
        return $this->nom;
    }

    public function setNom(string $nom): static
    {
        $this->nom = $nom;

        return $this;
    }

    public function getCode(): ?string
    {
        return $this->code;
    }

    public function setCode(string $code): static
    {
        $this->code = $code ;

        return $this;
    }
      public function getPrixBase(): ?float
    {
        return $this->prixBase;
    }

    public function setPrixBase(float $prixBase): static
    {
        $this->prixBase = $prixBase;

        return $this;
    }
      public function isPersonnalisable(): ?bool
    {
        return $this->personnalisable;
    }

    public function setPersonnalisable(bool $personnalisable): static
    {
        $this->personnalisable = $personnalisable;

        return $this;
    }
      public function isActif(): ?bool
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

    public function setDescription(string $description): static
    {
        $this->description = $description;

        return $this;
    }

    public function isPublie(): ?bool
    {
        return $this->publie;
    }

    public function setPublie(bool $publie): static
    {
        $this->publie = $publie;

        return $this;
    }

    public function getOrdre(): ?int
    {
        return $this->ordre;
    }

    public function setOrdre(int $ordre): static
    {
        $this->ordre = $ordre;

        return $this;
    }

    public function getCategorieProduit(): ?CategorieProduit
    {
        return $this->categorieProduit;
    }

    public function setCategorieProduit(?CategorieProduit $categorieProduit): static
    {
        $this->categorieProduit = $categorieProduit;

        return $this;
    }

    /**
     * @return Collection<int, TypesImpression>
     */
    public function getTypesImpressions(): Collection
    {
        return $this->typesImpressions;
    }

    public function addTypeImpression(TypesImpression $typeImpression): static
    {
        if (!$this->typesImpressions->contains($typeImpression)) {
            $this->typesImpressions->add($typeImpression);
        }

        return $this;
    }

    public function removeTypeImpression(TypesImpression $typeImpression): static
    {
        $this->typesImpressions->removeElement($typeImpression);

        return $this;
    }

    /**
     * @return Collection<int, Supports>
     */
    public function getSupports(): Collection
    {
        return $this->supports;
    }

    public function addSupport(Supports $support): static
    {
        if (!$this->supports->contains($support)) {
            $this->supports->add($support);
        }

        return $this;
    }

    public function removeSupport(Supports $support): static
    {
        $this->supports->removeElement($support);

        return $this;
    }

    /**
     * @return Collection<int, Format>
     */
    public function getFormats(): Collection
    {
        return $this->formats;
    }

    public function addFormat(Format $format): static
    {
        if (!$this->formats->contains($format)) {
            $this->formats->add($format);
        }

        return $this;
    }

    public function removeFormat(Format $format): static
    {
        $this->formats->removeElement($format);

        return $this;
    }

    /**
     * @return Collection<int, Finition>
     */
    public function getFinitions(): Collection
    {
        return $this->finitions;
    }

    public function addFinition(Finition $finition): static
    {
        if (!$this->finitions->contains($finition)) {
            $this->finitions->add($finition);
        }

        return $this;
    }

    public function removeFinition(Finition $finition): static
    {
        $this->finitions->removeElement($finition);

        return $this;
    }

    /**
     * @return Collection<int, CommandesDetails>
     */
    public function getCommandesDetails(): Collection
    {
        return $this->commandesDetails;
    }

    public function addCommandesDetail(CommandesDetails $commandesDetail): static
    {
        if (!$this->commandesDetails->contains($commandesDetail)) {
            $this->commandesDetails->add($commandesDetail);
            //$commandesDetail->setProduit($this);
        }

        return $this;
    }

    public function removeCommandesDetail(CommandesDetails $commandesDetail): static
    {
        if ($this->commandesDetails->removeElement($commandesDetail)) {
            if ($commandesDetail->getProduit() === $this) {
                $commandesDetail->setProduit(null);
            }
        }

        return $this;
    }
}
