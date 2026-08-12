<?php

namespace App\Entity;

use App\Repository\ClientsRepository;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\DBAL\Types\Types;
use Doctrine\ORM\Mapping as ORM;
use Symfony\Component\Validator\Constraints as Assert;
use Symfony\Bridge\Doctrine\Validator\Constraints\UniqueEntity;
use Symfony\Bridge\Doctrine\Types\UuidType;
use Symfony\Component\Uid\Uuid;



#[UniqueEntity(
    fields: ['telephone'],
    message: 'Un client avec ce numéro de téléphone existe déjà.',
    errorPath: 'telephone'
)]
#[ORM\Entity(repositoryClass: ClientsRepository::class)]
#[ORM\HasLifecycleCallbacks]
class Clients
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    private ?int $id = null;

    #[ORM\Column(length: 50, unique: true)]
    #[Assert\NotBlank(message: 'Le code client est obligatoire.')]
    private ?string $code = null;

    #[ORM\Column(length: 100, nullable: true)]
    private ?string $raisonSociale = null;

    #[ORM\Column(length: 50, nullable: false)]
    private ?string $nom = null;

    #[ORM\Column(length: 50, nullable: false)]
    private ?string $prenom = null;

    
    #[ORM\Column(
        length: 30,
        unique: true
    )]
    #[Assert\NotBlank(
        message: 'Le numéro de téléphone est obligatoire.'
    )]
    #[Assert\Length(
        min: 8,
        max: 30,
        minMessage: 'Le numéro de téléphone doit contenir au moins {{ limit }} caractères.',
        maxMessage: 'Le numéro de téléphone ne peut pas dépasser {{ limit }} caractères.'
    )]
    private ?string $telephone = null;

    #[ORM\Column(length: 30, nullable: true)]
    private ?string $telephone2 = null;

    #[ORM\Column(length: 255, nullable: true)]
    #[Assert\Email(
        message: 'L’adresse email n’est pas valide.'
    )]
    private ?string $email = null;

    #[ORM\Column(length: 255, nullable: true)]
    private ?string $adresse = null;

    #[ORM\Column(length: 100, nullable: true)]
    private ?string $ville = null;

    #[ORM\Column(length: 30, nullable: true)]
    private ?string $nif = null;

    #[ORM\Column(length: 50, nullable: true)]
    private ?string $rccm = null;

    #[ORM\Column(
        length: 10,
        options: ['default' => 'B2C']
    )]
    #[Assert\Choice(
        choices: ['B2C', 'B2B'],
        message: 'Le type de client doit être B2C ou B2B.'
    )]
    private string $typeClient = 'B2C';

    #[ORM\Column(nullable: true)]
    #[Assert\PositiveOrZero(
        message: 'Le plafond de crédit ne peut pas être négatif.'
    )]
    private ?int $plafondCredit = 0;

    #[ORM\Column(type: Types::TEXT, nullable: true)]
    private ?string $observation = null;

    #[ORM\Column]
    private ?\DateTime $createdAt = null;

    #[ORM\Column]
    private ?\DateTime $updatedAt = null;

    #[ORM\Column]
    private ?bool $statut = null;

    /**
     * @var Collection<int, Devis>
     */
    #[ORM\OneToMany(
        targetEntity: Devis::class,
        mappedBy: 'clients'
    )]
    private Collection $devis;

    #[ORM\Column(
        type: UuidType::NAME,
        unique: true
    )]
    private Uuid $publicId;


    public function __construct()
    {
        $this->devis = new ArrayCollection();
        $this->publicId = Uuid::v7();
    }

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getCode(): ?string
    {
        return $this->code;
    }

    public function setCode(string $code): static
    {
        $this->code = strtoupper(trim($code));

        return $this;
    }

    public function getRaisonSociale(): ?string
    {
        return $this->raisonSociale;
    }

    public function setRaisonSociale(
        ?string $raisonSociale
    ): static {
        $this->raisonSociale = $this->normaliserValeur(
            $raisonSociale
        );

        return $this;
    }

    public function getNom(): ?string
    {
        return $this->nom;
    }

    public function setNom(?string $nom): static
    {
        $this->nom = $this->normaliserValeur($nom);

        return $this;
    }

    public function getPrenom(): ?string
    {
        return $this->prenom;
    }

    public function setPrenom(?string $prenom): static
    {
        $this->prenom = $this->normaliserValeur($prenom);

        return $this;
    }

    public function getTelephone(): ?string
    {
        return $this->telephone;
    }

    public function setTelephone(?string $telephone): static
    {
        if ($telephone === null) {
            $this->telephone = null;

            return $this;
        }

        $telephone = trim($telephone);

        // Conserve uniquement les chiffres et éventuellement le + initial.
        $telephone = preg_replace(
            '/(?!^\+)[^\d]/',
            '',
            $telephone
        );

        $this->telephone = $telephone;

        return $this;
    }

    public function getTelephone2(): ?string
    {
        return $this->telephone2;
    }

    public function setTelephone2(?string $telephone2): static
    {
        $this->telephone2 = $this->normaliserValeur(
            $telephone2
        );

        return $this;
    }

    public function getEmail(): ?string
    {
        return $this->email;
    }

    public function setEmail(?string $email): static
    {
        $email = $this->normaliserValeur($email);

        $this->email = $email !== null
            ? strtolower($email)
            : null;

        return $this;
    }

    public function getAdresse(): ?string
    {
        return $this->adresse;
    }

    public function setAdresse(?string $adresse): static
    {
        $this->adresse = $this->normaliserValeur($adresse);

        return $this;
    }

    public function getVille(): ?string
    {
        return $this->ville;
    }

    public function setVille(?string $ville): static
    {
        $this->ville = $this->normaliserValeur($ville);

        return $this;
    }

    public function getNif(): ?string
    {
        return $this->nif;
    }

    public function setNif(?string $nif): static
    {
        $this->nif = $this->normaliserValeur($nif);

        return $this;
    }

    public function getRccm(): ?string
    {
        return $this->rccm;
    }

    public function setRccm(?string $rccm): static
    {
        $this->rccm = $this->normaliserValeur($rccm);

        return $this;
    }

    public function getTypeClient(): string
    {
        return $this->typeClient;
    }

    public function setTypeClient(string $typeClient): static
    {
        $typeClient = strtoupper(trim($typeClient));

        $this->typeClient = in_array(
            $typeClient,
            ['B2C', 'B2B'],
            true
        ) ? $typeClient : 'B2C';

        return $this;
    }

    public function isB2B(): bool
    {
        return $this->typeClient === 'B2B';
    }

    public function isB2C(): bool
    {
        return $this->typeClient === 'B2C';
    }

    public function getPlafondCredit(): ?int
    {
        return $this->plafondCredit;
    }

    public function setPlafondCredit(
        ?int $plafondCredit
    ): static {
        $this->plafondCredit = $plafondCredit;

        return $this;
    }

    public function getObservation(): ?string
    {
        return $this->observation;
    }

    public function setObservation(
        ?string $observation
    ): static {
        $this->observation = $this->normaliserValeur(
            $observation
        );

        return $this;
    }

    public function getCreatedAt(): ?\DateTime
    {
        return $this->createdAt;
    }

    public function setCreatedAt(
        \DateTime $createdAt
    ): static {
        $this->createdAt = $createdAt;

        return $this;
    }

    public function getUpdatedAt(): ?\DateTime
    {
        return $this->updatedAt;
    }

    public function setUpdatedAt(
        \DateTime $updatedAt
    ): static {
        $this->updatedAt = $updatedAt;

        return $this;
    }

    #[ORM\PrePersist]
    public function initialiserDates(): void
    {
        $maintenant = new \DateTime();

        if ($this->createdAt === null) {
            $this->createdAt = $maintenant;
        }

        $this->updatedAt = $maintenant;
    }

    #[ORM\PreUpdate]
    public function actualiserDate(): void
    {
        $this->updatedAt = new \DateTime();
    }

    public function __toString(): string
    {
        if (
            $this->isB2B()
            && $this->raisonSociale !== null
        ) {
            return $this->raisonSociale;
        }

        $nomComplet = trim(sprintf(
            '%s %s',
            $this->prenom ?? '',
            $this->nom ?? ''
        ));

        return $nomComplet !== ''
            ? $nomComplet
            : ($this->code ?? 'Client');
    }

    private function normaliserValeur(
        ?string $valeur
    ): ?string {
        if ($valeur === null) {
            return null;
        }

        $valeur = trim($valeur);

        return $valeur === '' ? null : $valeur;
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
    public function genererCodeDepuisId(): void
    {
        if ($this->id === null) {
            throw new \LogicException(
                'Le client doit être enregistré avant de générer son code.'
            );
        }

        $this->code = sprintf('CLI-%06d', $this->id);
    }

    /**
     * @return Collection<int, Devis>
     */
    public function getDevis(): Collection
    {
        return $this->devis;
    }

    public function addDevi(Devis $devi): static
    {
        if (!$this->devis->contains($devi)) {
            $this->devis->add($devi);
            $devi->setClients($this);
        }

        return $this;
    }

    public function removeDevi(Devis $devi): static
    {
        if (
            $this->devis->removeElement($devi)
            && $devi->getClients() === $this
        ) {
            /*
         * La relation est obligatoire dans Devis.
         * Le devis doit être associé à un autre client
         * avant son retrait définitif.
         */
        }

        return $this;
    }
    public function getPublicId(): Uuid
    {
        return $this->publicId;
    }
}
