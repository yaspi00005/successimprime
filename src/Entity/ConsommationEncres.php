<?php

namespace App\Entity;

use App\Repository\ConsommationEncresRepository;
use BcMath\Number;
use Doctrine\DBAL\Types\Types;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity(repositoryClass: ConsommationEncresRepository::class)]
class ConsommationEncres
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    private ?int $id = null;

    #[ORM\ManyToOne(inversedBy: 'consommationEncres')]
    private ?Production $production = null;

    #[ORM\Column(type: Types::INTEGER)]
    private ?int $encre = null;

    #[ORM\Column(type: Types::INTEGER)]
    private ?int $quantite = null;

    #[ORM\Column(length: 40)]
    private ?string $cout = null;

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getProduction(): ?Production
    {
        return $this->production;
    }

    public function setProduction(?Production $production): static
    {
        $this->production = $production;

        return $this;
    }

    public function getEncre(): ?Number
    {
        return $this->encre;
    }

    public function setEncre(Number $encre): static
    {
        $this->encre = $encre;

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

    public function getCout(): ?string
    {
        return $this->cout;
    }

    public function setCout(string $cout): static
    {
        $this->cout = $cout;

        return $this;
    }
}
