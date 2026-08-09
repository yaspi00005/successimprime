<?php

namespace App\Entity;

use App\Repository\UserRepository;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\ORM\Mapping as ORM;
use Symfony\Component\Security\Core\User\PasswordAuthenticatedUserInterface;
use Symfony\Component\Security\Core\User\UserInterface;

#[ORM\Entity(repositoryClass: UserRepository::class)]
#[ORM\Table(name: '`user`')]
#[ORM\UniqueConstraint(name: 'UNIQ_IDENTIFIER_USERNAME', fields: ['username'])]
class User implements UserInterface, PasswordAuthenticatedUserInterface
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    private ?int $id = null;

    #[ORM\Column(length: 180)]
    private ?string $username = null;

    /**
     * @var list<string> The user roles
     */
    #[ORM\Column]
    private array $roles = [];

    /**
     * @var string The hashed password
     */
    #[ORM\Column]
    private ?string $password = null;

    /**
     * @var Collection<int, Commandes>
     */
    #[ORM\OneToMany(targetEntity: Commandes::class, mappedBy: 'agents')]
    private Collection $commandes;

    #[ORM\Column(options: ['default' => true])]
    private ?bool $actif = null;

    #[ORM\OneToOne(inversedBy: 'user', cascade: ['persist'])]
    #[ORM\JoinColumn(nullable: false)]
    private ?Employes $employe = null;

    #[ORM\Column]
    private ?\DateTimeImmutable $dateAdd = null;

    #[ORM\Column]
    private ?\DateTimeImmutable $dateUpdate = null;

    /**
     * @var Collection<int, Paiements>
     */
    #[ORM\OneToMany(targetEntity: Paiements::class, mappedBy: 'encaissePar')]
    private Collection $paiements;

    public function __construct()
    {
        $this->commandes = new ArrayCollection();
        $this->paiements = new ArrayCollection();

        $maintenant = new \DateTimeImmutable();
        $this->dateAdd = $maintenant;
        $this->dateUpdate = $maintenant;
    }

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getUsername(): ?string
    {
        return $this->username;
    }

    public function setUsername(string $username): static
    {
        $this->username = $username;

        return $this;
    }

    /**
     * A visual identifier that represents this user.
     *
     * @see UserInterface
     */
    public function getUserIdentifier(): string
    {
        return (string) $this->username;
    }

    /**
     * @see UserInterface
     */
    public function getRoles(): array
    {
        $roles = $this->roles;
        // guarantee every user at least has ROLE_USER
        $roles[] = 'ROLE_USER';

        return array_unique($roles);
    }

    /**
     * @param list<string> $roles
     */
    public function setRoles(array $roles): static
    {
        $this->roles = $roles;

        return $this;
    }

    /**
     * @see PasswordAuthenticatedUserInterface
     */
    public function getPassword(): ?string
    {
        return $this->password;
    }

    public function setPassword(string $password): static
    {
        $this->password = $password;

        return $this;
    }

    /**
     * Ensure the session doesn't contain actual password hashes by CRC32C-hashing them, as supported since Symfony 7.3.
     */
    public function __serialize(): array
    {
        $data = (array) $this;
        $data["\0" . self::class . "\0password"] = hash('crc32c', $this->password);

        return $data;
    }

    /**
     * @return Collection<int, Commandes>
     */
    public function getCommandes(): Collection
    {
        return $this->commandes;
    }

    public function addCommande(Commandes $commande): static
    {
        if (!$this->commandes->contains($commande)) {
            $this->commandes->add($commande);
            $commande->setAgents($this);
        }

        return $this;
    }

    public function removeCommande(Commandes $commande): static
    {
        if ($this->commandes->removeElement($commande)) {
            // set the owning side to null (unless already changed)
            if ($commande->getAgents() === $this) {
                $commande->setAgents(null);
            }
        }

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

    public function getEmploye(): ?Employes
    {
        return $this->employe;
    }

    public function setEmploye(?Employes $employe): static
    {
        $this->employe = $employe;

        return $this;
    }

    public function getDateAdd(): \DateTimeImmutable
    {
        return $this->dateAdd;
    }

    public function setDateAdd(\DateTimeImmutable $dateAdd): static
    {
        $this->dateAdd = $dateAdd;

        return $this;
    }

    public function getDateUpdate(): \DateTimeImmutable
    {
        return $this->dateUpdate;
    }

    public function setDateUpdate(\DateTimeImmutable $dateUpdate): static
    {
        $this->dateUpdate = $dateUpdate;

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
            $paiement->setEncaissePar($this);
        }

        return $this;
    }

    public function removePaiement(Paiements $paiement): static
    {
        if ($this->paiements->removeElement($paiement)) {
            // set the owning side to null (unless already changed)
            if ($paiement->getEncaissePar() === $this) {
                $paiement->setEncaissePar(null);
            }
        }

        return $this;
    }
    public function __toString(): string
    {
        if ($this->employe !== null) {
            return trim(
                ($this->employe->getPrenom() ?? '') . ' ' .
                    ($this->employe->getNom() ?? '')
            );
        }

        return $this->username ?? $this->email ?? 'Utilisateur';
    }
}
