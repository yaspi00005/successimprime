<?php

namespace App\Entity;

use App\Repository\MachinesRepository;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\DBAL\Types\Types;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity(repositoryClass: MachinesRepository::class)]
class Machines
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    private ?int $id = null;

    #[ORM\Column(length: 255)]
    private ?string $nom = null;

    #[ORM\Column(length: 100)]
    private ?string $marque = null;

    #[ORM\Column(length: 100)]
    private ?string $modeles = null;

    #[ORM\Column(length: 100)]
    private ?string $numeroSerie = null;

    #[ORM\Column(length: 100)]
    private ?string $typeMachine = null;

    #[ORM\Column(length: 10)]
    private ?string $largeurImpression = null;

    #[ORM\Column(type: Types::INTEGER)]
    private ?int $nbTetes = null;

    #[ORM\Column(type: Types::DATE_MUTABLE)]
    private ?\DateTime $dateAchat = null;

    #[ORM\Column(type: Types::DATE_MUTABLE)]
    private ?\DateTime $DateMiseService = null;

    #[ORM\Column(type: Types::INTEGER)]
    private ?int $compteurM2 = null;

    #[ORM\Column(type: Types::INTEGER)]
    private ?int $compteurHeures = null;

    #[ORM\Column(length: 20)]
    private ?string $etat = null;

    #[ORM\Column(length: 50, unique: true, nullable: true)]
    private ?string $numeroMachine = null;

    #[ORM\Column(length: 45, unique: true)]
    private ?string $adresseIp = null;

    /**
     * @var Collection<int, CommandesDetails>
     */
    #[ORM\OneToMany(targetEntity: CommandesDetails::class, mappedBy: 'machine')]
    private Collection $commandesDetails;

    /**
     * @var Collection<int, Production>
     */
    #[ORM\OneToMany(targetEntity: Production::class, mappedBy: 'machine')]
    private Collection $productions;

    /**
     * @var Collection<int, Maintenance>
     */
    #[ORM\OneToMany(targetEntity: Maintenance::class, mappedBy: 'machine')]
    private Collection $maintenances;

    public function __construct()
    {
        $this->commandesDetails = new ArrayCollection();
        $this->productions = new ArrayCollection();
        $this->maintenances = new ArrayCollection();
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

    public function getMarque(): ?string
    {
        return $this->marque;
    }

    public function setMarque(string $marque): static
    {
        $this->marque = $marque;

        return $this;
    }

    public function getModeles(): ?string
    {
        return $this->modeles;
    }

    public function setModeles(string $modeles): static
    {
        $this->modeles = $modeles;

        return $this;
    }

    public function getNumeroSerie(): ?string
    {
        return $this->numeroSerie;
    }

    public function setNumeroSerie(string $numeroSerie): static
    {
        $this->numeroSerie = $numeroSerie;

        return $this;
    }

    public function getTypeMachine(): ?string
    {
        return $this->typeMachine;
    }

    public function setTypeMachine(string $typeMachine): static
    {
        $this->typeMachine = $typeMachine;

        return $this;
    }

    public function getLargeurImpression(): ?string
    {
        return $this->largeurImpression;
    }

    public function setLargeurImpression(string $largeurImpression): static
    {
        $this->largeurImpression = $largeurImpression;

        return $this;
    }

    public function getNbTetes(): ?int
    {
        return $this->nbTetes;
    }

    public function setNbTetes(int $nbTetes): static
    {
        $this->nbTetes = $nbTetes;

        return $this;
    }

    public function getDateAchat(): ?\DateTime
    {
        return $this->dateAchat;
    }

    public function setDateAchat(\DateTime $dateAchat): static
    {
        $this->dateAchat = $dateAchat;

        return $this;
    }

    public function getDateMiseService(): ?\DateTime
    {
        return $this->DateMiseService;
    }

    public function setDateMiseService(\DateTime $DateMiseService): static
    {
        $this->DateMiseService = $DateMiseService;

        return $this;
    }

    public function getCompteurM2(): ?int
    {
        return $this->compteurM2;
    }

    public function setCompteurM2(int $compteurM2): static
    {
        $this->compteurM2 = $compteurM2;

        return $this;
    }

    public function getCompteurHeures(): ?int
    {
        return $this->compteurHeures;
    }

    public function setCompteurHeures(int $compteurHeures): static
    {
        $this->compteurHeures = $compteurHeures;

        return $this;
    }

    public function getEtat(): ?string
    {
        return $this->etat;
    }

    public function setEtat(string $etat): static
    {
        $this->etat = $etat;

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
            $commandesDetail->setMachine($this);
        }

        return $this;
    }

    public function removeCommandesDetail(CommandesDetails $commandesDetail): static
    {
        if ($this->commandesDetails->removeElement($commandesDetail)) {
            // set the owning side to null (unless already changed)
            if ($commandesDetail->getMachine() === $this) {
                $commandesDetail->setMachine(null);
            }
        }

        return $this;
    }

    /**
     * @return Collection<int, Production>
     */
    public function getProductions(): Collection
    {
        return $this->productions;
    }

    public function addProduction(Production $production): static
    {
        if (!$this->productions->contains($production)) {
            $this->productions->add($production);
            $production->setMachine($this);
        }

        return $this;
    }

    public function removeProduction(Production $production): static
    {
        if ($this->productions->removeElement($production)) {
            // set the owning side to null (unless already changed)
            if ($production->getMachine() === $this) {
                $production->setMachine(null);
            }
        }

        return $this;
    }

    /**
     * @return Collection<int, Maintenance>
     */
    public function getMaintenances(): Collection
    {
        return $this->maintenances;
    }

    public function addMaintenance(Maintenance $maintenance): static
    {
        if (!$this->maintenances->contains($maintenance)) {
            $this->maintenances->add($maintenance);
            $maintenance->setMachine($this);
        }

        return $this;
    }

    public function removeMaintenance(Maintenance $maintenance): static
    {
        if ($this->maintenances->removeElement($maintenance)) {
            // set the owning side to null (unless already changed)
            if ($maintenance->getMachine() === $this) {
                $maintenance->setMachine(null);
            }
        }

        return $this;
    }

    public function getNumeroMachine(): ?string
    {
        return $this->numeroMachine;
    }

    public function setNumeroMachine(?string $numeroMachine): static
    {
        $this->numeroMachine = $numeroMachine;

        return $this;
    }

    

   public function getAdresseIp(): ?string
{
    return $this->adresseIp;
}

public function setAdresseIp(string $adresseIp): static
{
    $adresseIp = trim($adresseIp);

    if (!filter_var($adresseIp, FILTER_VALIDATE_IP)) {
        throw new \InvalidArgumentException(
            'L’adresse IP de la machine est invalide.'
        );
    }

    $this->adresseIp = $adresseIp;

    return $this;
}

    public function __toString(): string
    {
        return $this->nom ?? 'Machine';
        return $this->nom ?? 'Machine';
    }

    
}
