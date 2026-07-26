<?php

namespace App\Entity;

use App\Repository\ProduitConfigurationFinitionRepository;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity(
    repositoryClass: ProduitConfigurationFinitionRepository::class
)]
#[ORM\Table(name: 'produit_configuration_finition')]
#[ORM\UniqueConstraint(
    name: 'uniq_configuration_finition',
    columns: [
        'produit_configuration_id',
        'finition_id',
    ]
)]
class ProduitConfigurationFinition
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    private ?int $id = null;

    #[ORM\ManyToOne(
        inversedBy: 'configurationFinitions'
    )]
    #[ORM\JoinColumn(
        name: 'produit_configuration_id',
        nullable: false,
        onDelete: 'CASCADE'
    )]
    private ?ProduitConfiguration $produitConfiguration = null;

    #[ORM\ManyToOne]
    #[ORM\JoinColumn(
        name: 'finition_id',
        nullable: false,
        onDelete: 'CASCADE'
    )]
    private ?Finition $finition = null;

    /*
     * La finition doit obligatoirement être appliquée.
     * Exemple : montage dans une structure Roll-up.
     */
    #[ORM\Column]
    private bool $obligatoire = false;

    /*
     * La finition est cochée automatiquement,
     * mais l’utilisateur peut éventuellement la retirer.
     */
    #[ORM\Column]
    private bool $selectionneeParDefaut = false;

    /*
     * Certaines finitions sont incluses gratuitement.
     */
    #[ORM\Column]
    private bool $payante = false;

    /*
     * Prix de la finition en FCFA.
     * La signification dépend du mode de calcul.
     */
    #[ORM\Column]
    private int $prix = 0;

    /*
     * Modes possibles :
     *
     * forfait
     * unite
     * feuille
     * exemplaire
     * metre
     * metre_carre
     * point
     * face
     */
    #[ORM\Column(length: 30)]
    private string $modeCalcul = 'forfait';

    #[ORM\Column]
    private int $quantiteMinimale = 1;

    #[ORM\Column(nullable: true)]
    private ?int $quantiteMaximale = null;

    #[ORM\Column]
    private bool $active = true;

    #[ORM\Column]
    private int $ordre = 10;

    #[ORM\Column(length: 500, nullable: true)]
    private ?string $description = null;

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getProduitConfiguration(): ?ProduitConfiguration
    {
        return $this->produitConfiguration;
    }

    public function setProduitConfiguration(
        ?ProduitConfiguration $produitConfiguration
    ): static {
        $this->produitConfiguration = $produitConfiguration;

        return $this;
    }

    public function getFinition(): ?Finition
    {
        return $this->finition;
    }

    public function setFinition(?Finition $finition): static
    {
        $this->finition = $finition;

        return $this;
    }

    public function isObligatoire(): bool
    {
        return $this->obligatoire;
    }

    public function setObligatoire(bool $obligatoire): static
    {
        $this->obligatoire = $obligatoire;

        if ($obligatoire) {
            $this->selectionneeParDefaut = true;
        }

        return $this;
    }

    public function isSelectionneeParDefaut(): bool
    {
        return $this->selectionneeParDefaut;
    }

    public function setSelectionneeParDefaut(
        bool $selectionneeParDefaut
    ): static {
        $this->selectionneeParDefaut = $selectionneeParDefaut;

        return $this;
    }

    public function isPayante(): bool
    {
        return $this->payante;
    }

    public function setPayante(bool $payante): static
    {
        $this->payante = $payante;

        if (!$payante) {
            $this->prix = 0;
        }

        return $this;
    }

    public function getPrix(): int
    {
        return $this->prix;
    }

    public function setPrix(int $prix): static
    {
        $this->prix = max(0, $prix);
        $this->payante = $this->prix > 0;

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
            'feuille',
            'exemplaire',
            'metre',
            'metre_carre',
            'point',
            'face',
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
        $this->quantiteMinimale = max(1, $quantiteMinimale);

        return $this;
    }

    public function getQuantiteMaximale(): ?int
    {
        return $this->quantiteMaximale;
    }

    public function setQuantiteMaximale(
        ?int $quantiteMaximale
    ): static {
        $this->quantiteMaximale = $quantiteMaximale !== null
            ? max(1, $quantiteMaximale)
            : null;

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
        $this->description = $description !== null
            ? trim($description)
            : null;

        return $this;
    }

    public function calculerMontant(
        int $quantite = 1,
        ?float $surface = null,
        ?float $longueur = null,
        int $nombreFaces = 1,
        int $nombrePoints = 1
    ): int {
        if (!$this->payante || $this->prix <= 0) {
            return 0;
        }

        return match ($this->modeCalcul) {
            'unite',
            'feuille',
            'exemplaire' => $this->prix * max(1, $quantite),

            'metre' => (int) round(
                $this->prix * max(0, $longueur ?? 0)
            ),

            'metre_carre' => (int) round(
                $this->prix * max(0, $surface ?? 0)
            ),

            'face' => $this->prix * max(1, $nombreFaces),

            'point' => $this->prix * max(1, $nombrePoints),

            default => $this->prix,
        };
    }

    public function __toString(): string
    {
        return sprintf(
            '%s — %s',
            $this->produitConfiguration?->__toString()
                ?? 'Configuration',
            $this->finition?->getNom()
                ?? 'Finition'
        );
    }
}