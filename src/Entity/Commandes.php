<?php

namespace App\Entity;

use App\Repository\CommandesRepository;
use BcMath\Number;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\DBAL\Types\Types;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity(repositoryClass: CommandesRepository::class)]
class Commandes
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    private ?int $id = null;

    #[ORM\Column(length: 30)]
    private ?string $commandes = null;

    #[ORM\ManyToOne(inversedBy: 'commandes')]
    #[ORM\JoinColumn(nullable: false)]
    private ?Clients $clients = null;

    #[ORM\Column(type: Types::INTEGER)]
    private ?int $montantTotal = null;

    #[ORM\Column]
    private ?int $remises = null;

    #[ORM\Column]
    private ?int $montantApayer = null;

    #[ORM\Column]
    private ?\DateTime $dateCommandes = null;

    #[ORM\Column]
    private ?\DateTime $dateLivraisons = null;

    #[ORM\ManyToOne(inversedBy: 'commandes')]
    #[ORM\JoinColumn(nullable: false)]
    private ?user $agents = null;

    #[ORM\Column]
    private ?bool $deleted = null;

    #[ORM\Column]
    private ?bool $statut = null;

    #[ORM\Column(length: 50)]
    private ?string $numero = null;

    #[ORM\Column(type: Types::DATE_MUTABLE)]
    private ?\DateTime $dateCommande = null;

    #[ORM\Column]
    private ?\DateTime $dateLivraison = null;

    #[ORM\Column]
    private ?bool $etat = null;

    #[ORM\Column(type: Types::INTEGER)]
    private ?int $remise = null;

    #[ORM\Column(type: Types::INTEGER)]
    private ?int $tva = null;

    #[ORM\Column(type: Types::INTEGER)]
    private ?int $totalHt = null;

    #[ORM\Column(type: Types::INTEGER)]
    private ?int $totalTtc = null;

    #[ORM\Column(type: Types::TEXT)]
    private ?string $observation = null;

    /**
     * @var Collection<int, CommandesDetails>
     */
    #[ORM\OneToMany(targetEntity: CommandesDetails::class, mappedBy: 'commande')]
    private Collection $commandesDetails;

    /**
     * @var Collection<int, Paiements>
     */
    #[ORM\OneToMany(targetEntity: Paiements::class, mappedBy: 'commande')]
    private Collection $paiements;

    /**
     * @var Collection<int, Factures>
     */
    #[ORM\OneToMany(targetEntity: Factures::class, mappedBy: 'commande')]
    private Collection $factures;

    public function __construct()
    {
        $this->commandesDetails = new ArrayCollection();
        $this->paiements = new ArrayCollection();
        $this->factures = new ArrayCollection();
    }

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getCommandes(): ?string
    {
        return $this->commandes;
    }

    public function setCommandes(string $commandes): static
    {
        $this->commandes = $commandes;

        return $this;
    }

    public function getClients(): ?CLients
    {
        return $this->clients;
    }

    public function setClients(?CLients $clients): static
    {
        $this->clients = $clients;

        return $this;
    }

    public function getMontantTotal(): ?Number
    {
        return $this->montantTotal;
    }

    public function setMontantTotal(Number $montantTotal): static
    {
        $this->montantTotal = $montantTotal;

        return $this;
    }

    public function getRemises(): ?int
    {
        return $this->remises;
    }

    public function setRemises(int $remises): static
    {
        $this->remises = $remises;

        return $this;
    }

    public function getMontantApayer(): ?int
    {
        return $this->montantApayer;
    }

    public function setMontantApayer(int $montantApayer): static
    {
        $this->montantApayer = $montantApayer;

        return $this;
    }

    public function getDateCommandes(): ?\DateTime
    {
        return $this->dateCommandes;
    }

    public function setDateCommandes(\DateTime $dateCommandes): static
    {
        $this->dateCommandes = $dateCommandes;

        return $this;
    }

    public function getDateLivraisons(): ?\DateTime
    {
        return $this->dateLivraisons;
    }

    public function setDateLivraisons(\DateTime $dateLivraisons): static
    {
        $this->dateLivraisons = $dateLivraisons;

        return $this;
    }

    public function getAgents(): ?user
    {
        return $this->agents;
    }

    public function setAgents(?user $agents): static
    {
        $this->agents = $agents;

        return $this;
    }

    public function isDeleted(): ?bool
    {
        return $this->deleted;
    }

    public function setDeleted(bool $deleted): static
    {
        $this->deleted = $deleted;

        return $this;
    }

    public function isStatut(): ?bool
    {
        return $this->statut;
    }

    public function setStatut(bool $statut): static
    {
        $this->statut = $statut;

        return $this;
    }

    public function getNumero(): ?string
    {
        return $this->numero;
    }

    public function setNumero(string $numero): static
    {
        $this->numero = $numero;

        return $this;
    }

    public function getDateCommande(): ?\DateTime
    {
        return $this->dateCommande;
    }

    public function setDateCommande(\DateTime $dateCommande): static
    {
        $this->dateCommande = $dateCommande;

        return $this;
    }

    public function getDateLivraison(): ?\DateTime
    {
        return $this->dateLivraison;
    }

    public function setDateLivraison(\DateTime $dateLivraison): static
    {
        $this->dateLivraison = $dateLivraison;

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

    public function getRemise(): ?Number
    {
        return $this->remise;
    }

    public function setRemise(Number $remise): static
    {
        $this->remise = $remise;

        return $this;
    }

    public function getTva(): ?Number
    {
        return $this->tva;
    }

    public function setTva(Number $tva): static
    {
        $this->tva = $tva;

        return $this;
    }

    public function getTotalHt(): ?Number
    {
        return $this->totalHt;
    }

    public function setTotalHt(Number $totalHt): static
    {
        $this->totalHt = $totalHt;

        return $this;
    }

    public function getTotalTtc(): ?Number
    {
        return $this->totalTtc;
    }

    public function setTotalTtc(Number $totalTtc): static
    {
        $this->totalTtc = $totalTtc;

        return $this;
    }

    public function getObservation(): ?string
    {
        return $this->observation;
    }

    public function setObservation(string $observation): static
    {
        $this->observation = $observation;

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
            $commandesDetail->setCommande($this);
        }

        return $this;
    }

    public function removeCommandesDetail(CommandesDetails $commandesDetail): static
    {
        if ($this->commandesDetails->removeElement($commandesDetail)) {
            // set the owning side to null (unless already changed)
            if ($commandesDetail->getCommande() === $this) {
                $commandesDetail->setCommande(null);
            }
        }

        return $this;
    }

    /**
     * @return Collection<int, Paiements>
     */
    public function getPaiements(): Collection
    {
        return $this->paiements;
    }

    public function addPaiement(Paiements $paiement): static
    {
        if (!$this->paiements->contains($paiement)) {
            $this->paiements->add($paiement);
            $paiement->setCommande($this);
        }

        return $this;
    }

    public function removePaiement(Paiements $paiement): static
    {
        if ($this->paiements->removeElement($paiement)) {
            // set the owning side to null (unless already changed)
            if ($paiement->getCommande() === $this) {
                $paiement->setCommande(null);
            }
        }

        return $this;
    }

    /**
     * @return Collection<int, Factures>
     */
    public function getFactures(): Collection
    {
        return $this->factures;
    }

    public function addFacture(Factures $facture): static
    {
        if (!$this->factures->contains($facture)) {
            $this->factures->add($facture);
            $facture->setCommande($this);
        }

        return $this;
    }

    public function removeFacture(Factures $facture): static
    {
        if ($this->factures->removeElement($facture)) {
            // set the owning side to null (unless already changed)
            if ($facture->getCommande() === $this) {
                $facture->setCommande(null);
            }
        }

        return $this;
    }
}
