<?php

namespace App\Entity;

use App\Repository\ArticlesRepository;
use BcMath\Number;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\DBAL\Types\Types;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity(repositoryClass: ArticlesRepository::class)]
class Articles
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    private ?int $id = null;

    #[ORM\Column(length: 255)]
    private ?string $reference = null;

    #[ORM\Column(length: 255)]
    private ?string $designation = null;

    #[ORM\Column(length: 100)]
    private ?string $categorie = null;

    #[ORM\Column(length: 30)]
    private ?string $unite = null;

    #[ORM\Column(type: Types::INTEGER)]
    private ?int $stock = null;

    #[ORM\Column(length: 255)]
    private ?string $stockMin = null;

    #[ORM\Column(type: Types::INTEGER)]
    private ?int $prixAchat = null;

    #[ORM\Column(type: Types::INTEGER)]
    private ?int $prixVente = null;

    #[ORM\Column(length: 50)]
    private ?string $fournisseur = null;

    /**
     * @var Collection<int, StockEntrees>
     */
    #[ORM\OneToMany(targetEntity: StockEntrees::class, mappedBy: 'article')]
    private Collection $stockEntrees;

    /**
     * @var Collection<int, StockSorties>
     */
    #[ORM\OneToMany(targetEntity: StockSorties::class, mappedBy: 'article')]
    private Collection $stockSorties;

    public function __construct()
    {
        $this->stockEntrees = new ArrayCollection();
        $this->stockSorties = new ArrayCollection();
    }

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getReference(): ?string
    {
        return $this->reference;
    }

    public function setReference(string $reference): static
    {
        $this->reference = $reference;

        return $this;
    }

    public function getDesignation(): ?string
    {
        return $this->designation;
    }

    public function setDesignation(string $designation): static
    {
        $this->designation = $designation;

        return $this;
    }

    public function getCategorie(): ?string
    {
        return $this->categorie;
    }

    public function setCategorie(string $categorie): static
    {
        $this->categorie = $categorie;

        return $this;
    }

    public function getUnite(): ?string
    {
        return $this->unite;
    }

    public function setUnite(string $unite): static
    {
        $this->unite = $unite;

        return $this;
    }

    public function getStock(): ?Number
    {
        return $this->stock;
    }

    public function setStock(Number $stock): static
    {
        $this->stock = $stock;

        return $this;
    }

    public function getStockMin(): ?string
    {
        return $this->stockMin;
    }

    public function setStockMin(string $stockMin): static
    {
        $this->stockMin = $stockMin;

        return $this;
    }

    public function getPrixAchat(): ?Number
    {
        return $this->prixAchat;
    }

    public function setPrixAchat(Number $prixAchat): static
    {
        $this->prixAchat = $prixAchat;

        return $this;
    }

    public function getPrixVente(): ?Number
    {
        return $this->prixVente;
    }

    public function setPrixVente(Number $prixVente): static
    {
        $this->prixVente = $prixVente;

        return $this;
    }

    public function getFournisseur(): ?string
    {
        return $this->fournisseur;
    }

    public function setFournisseur(string $fournisseur): static
    {
        $this->fournisseur = $fournisseur;

        return $this;
    }

    /**
     * @return Collection<int, StockEntrees>
     */
    public function getStockEntrees(): Collection
    {
        return $this->stockEntrees;
    }

    public function addStockEntree(StockEntrees $stockEntree): static
    {
        if (!$this->stockEntrees->contains($stockEntree)) {
            $this->stockEntrees->add($stockEntree);
            $stockEntree->setArticle($this);
        }

        return $this;
    }

    public function removeStockEntree(StockEntrees $stockEntree): static
    {
        if ($this->stockEntrees->removeElement($stockEntree)) {
            // set the owning side to null (unless already changed)
            if ($stockEntree->getArticle() === $this) {
                $stockEntree->setArticle(null);
            }
        }

        return $this;
    }

    /**
     * @return Collection<int, StockSorties>
     */
    public function getStockSorties(): Collection
    {
        return $this->stockSorties;
    }

    public function addStockSorty(StockSorties $stockSorty): static
    {
        if (!$this->stockSorties->contains($stockSorty)) {
            $this->stockSorties->add($stockSorty);
            $stockSorty->setArticle($this);
        }

        return $this;
    }

    public function removeStockSorty(StockSorties $stockSorty): static
    {
        if ($this->stockSorties->removeElement($stockSorty)) {
            // set the owning side to null (unless already changed)
            if ($stockSorty->getArticle() === $this) {
                $stockSorty->setArticle(null);
            }
        }

        return $this;
    }
}
