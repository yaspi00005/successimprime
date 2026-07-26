<?php

namespace App\Entity;

use App\Repository\StockSortiesRepository;
use BcMath\Number;
use Doctrine\DBAL\Types\Types;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity(repositoryClass: StockSortiesRepository::class)]
class StockSorties
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    private ?int $id = null;

    #[ORM\ManyToOne(inversedBy: 'stockSorties')]
    private ?Articles $article = null;

    #[ORM\ManyToOne(inversedBy: 'stockSorties')]
    private ?CommandesDetails $commandeDetail = null;

    #[ORM\Column(type: Types::INTEGER)]
    private ?int $quantite = null;

    #[ORM\Column]
    private ?\DateTime $date = null;

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getArticle(): ?Articles
    {
        return $this->article;
    }

    public function setArticle(?Articles $article): static
    {
        $this->article = $article;

        return $this;
    }

    public function getCommandeDetail(): ?CommandesDetails
    {
        return $this->commandeDetail;
    }

    public function setCommandeDetail(?CommandesDetails $commandeDetail): static
    {
        $this->commandeDetail = $commandeDetail;

        return $this;
    }

    public function getQuantite(): ?Number
    {
        return $this->quantite;
    }

    public function setQuantite(Number $quantite): static
    {
        $this->quantite = $quantite;

        return $this;
    }

    public function getDate(): ?\DateTime
    {
        return $this->date;
    }

    public function setDate(\DateTime $date): static
    {
        $this->date = $date;

        return $this;
    }
}
