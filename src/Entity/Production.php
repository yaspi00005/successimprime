<?php

namespace App\Entity;

use App\Repository\ProductionRepository;
use BcMath\Number;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\DBAL\Types\Types;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity(repositoryClass: ProductionRepository::class)]
class Production
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    private ?int $id = null;

    #[ORM\ManyToOne(inversedBy: 'productions')]
    private ?CommandesDetails $commandeDetails = null;

    #[ORM\ManyToOne(inversedBy: 'productions')]
    private ?Machines $machine = null;

    #[ORM\Column]
    private ?\DateTime $dateDebut = null;

    #[ORM\Column]
    private ?\DateTime $dateFin = null;

    #[ORM\Column(type: Types::INTEGER)]
    private ?int $temps = null;

    #[ORM\Column(type: Types::INTEGER)]
    private ?int $m2Imprimes = null;

    #[ORM\Column]
    private ?bool $etat = null;

    /**
     * @var Collection<int, ConsommationEncres>
     */
    #[ORM\OneToMany(targetEntity: ConsommationEncres::class, mappedBy: 'production')]
    private Collection $consommationEncres;

    public function __construct()
    {
        $this->consommationEncres = new ArrayCollection();
    }

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getCommandeDetails(): ?CommandesDetails
    {
        return $this->commandeDetails;
    }

    public function setCommandeDetails(?CommandesDetails $commandeDetails): static
    {
        $this->commandeDetails = $commandeDetails;

        return $this;
    }

    public function getMachine(): ?Machines
    {
        return $this->machine;
    }

    public function setMachine(?Machines $machine): static
    {
        $this->machine = $machine;

        return $this;
    }

    public function getDateDebut(): ?\DateTime
    {
        return $this->dateDebut;
    }

    public function setDateDebut(\DateTime $dateDebut): static
    {
        $this->dateDebut = $dateDebut;

        return $this;
    }

    public function getDateFin(): ?\DateTime
    {
        return $this->dateFin;
    }

    public function setDateFin(\DateTime $dateFin): static
    {
        $this->dateFin = $dateFin;

        return $this;
    }

    public function getTemps(): ?Number
    {
        return $this->temps;
    }

    public function setTemps(Number $temps): static
    {
        $this->temps = $temps;

        return $this;
    }

    public function getM2Imprimes(): ?Number
    {
        return $this->m2Imprimes;
    }

    public function setM2Imprimes(Number $m2Imprimes): static
    {
        $this->m2Imprimes = $m2Imprimes;

        return $this;
    }

    public function isEtat(): ?bool
    {
        return $this->etat;
    }

    public function setEtat(bool $etat): static
    {
        $this->etat = $etat;

        return $this;
    }

    /**
     * @return Collection<int, ConsommationEncres>
     */
    public function getConsommationEncres(): Collection
    {
        return $this->consommationEncres;
    }

    public function addConsommationEncre(ConsommationEncres $consommationEncre): static
    {
        if (!$this->consommationEncres->contains($consommationEncre)) {
            $this->consommationEncres->add($consommationEncre);
            $consommationEncre->setProduction($this);
        }

        return $this;
    }

    public function removeConsommationEncre(ConsommationEncres $consommationEncre): static
    {
        if ($this->consommationEncres->removeElement($consommationEncre)) {
            // set the owning side to null (unless already changed)
            if ($consommationEncre->getProduction() === $this) {
                $consommationEncre->setProduction(null);
            }
        }

        return $this;
    }
}
