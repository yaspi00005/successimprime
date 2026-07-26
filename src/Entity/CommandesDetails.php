<?php

namespace App\Entity;

use App\Repository\CommandesDetailsRepository;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\DBAL\Types\Types;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity(repositoryClass: CommandesDetailsRepository::class)]
#[ORM\Table(name: 'commandes_details')]
class CommandesDetails
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    private ?int $id = null;

    /*
     * =========================================================
     * RELATIONS PRINCIPALES
     * =========================================================
     */

    #[ORM\ManyToOne(inversedBy: 'commandesDetails')]
    #[ORM\JoinColumn(nullable: false, onDelete: 'CASCADE')]
    private ?Commandes $commande = null;

    /*
     * Remplace Produits par Produit si ton entité est au singulier.
     */
    #[ORM\ManyToOne(inversedBy: 'commandesDetails')]
    #[ORM\JoinColumn(nullable: true, onDelete: 'SET NULL')]
    private ?Produits $produit = null;

    #[ORM\ManyToOne(inversedBy: 'commandesDetails')]
    #[ORM\JoinColumn(nullable: true, onDelete: 'SET NULL')]
    private ?TypesImpression $typeImpression = null;

    #[ORM\ManyToOne(inversedBy: 'commandesDetails')]
    #[ORM\JoinColumn(nullable: true, onDelete: 'SET NULL')]
    private ?Supports $support = null;

    #[ORM\ManyToOne(inversedBy: 'commandesDetails')]
    #[ORM\JoinColumn(nullable: true, onDelete: 'SET NULL')]
    private ?Machines $machine = null;

    #[ORM\ManyToOne(inversedBy: 'commandesDetails')]
    #[ORM\JoinColumn(nullable: true, onDelete: 'SET NULL')]
    private ?Format $format = null;

    /*
     * =========================================================
     * INFORMATIONS DU PRODUIT
     * =========================================================
     */

    #[ORM\Column(length: 255)]
    private ?string $designation = null;

    #[ORM\Column(type: Types::DECIMAL, precision: 10, scale: 2, nullable: true)]
    private ?string $largeur = null;

    #[ORM\Column(type: Types::DECIMAL, precision: 10, scale: 2, nullable: true)]
    private ?string $longueur = null;

    #[ORM\Column(type: Types::DECIMAL, precision: 12, scale: 4, nullable: true)]
    private ?string $surface = null;

    #[ORM\Column]
    private int $quantite = 1;

    /*
     * Les montants sont enregistrés en entier.
     * Cela convient au FCFA, qui n’utilise généralement pas de centimes.
     */
    #[ORM\Column]
    private int $prixUnitaire = 0;

    #[ORM\Column]
    private int $coutRevient = 0;

    #[ORM\Column]
    private int $remise = 0;

    #[ORM\Column]
    private int $tva = 0;

    #[ORM\Column]
    private int $totalHt = 0;

    #[ORM\Column]
    private int $totalTtc = 0;

    /*
     * =========================================================
     * PARAMÈTRES D’IMPRESSION
     * =========================================================
     */

    #[ORM\Column(length: 20, nullable: true)]
    private ?string $profilCouleurs = null;

    #[ORM\Column(length: 50, nullable: true)]
    private ?string $resolution = null;

    #[ORM\Column(length: 100, nullable: true)]
    private ?string $grammage = null;

    #[ORM\Column(length: 50, nullable: true)]
    private ?string $epaisseur = null;

    #[ORM\Column]
    private bool $rectoVerso = false;

    #[ORM\Column]
    private int $nombreFaces = 1;

    /*
     * =========================================================
     * FINITIONS ET OPTIONS
     * =========================================================
     */

    #[ORM\Column(length: 255, nullable: true)]
    private ?string $laminage = null;

    #[ORM\Column]
    private bool $oeillets = false;

    #[ORM\Column]
    private bool $decoupe = false;

    #[ORM\Column(length: 100, nullable: true)]
    private ?string $pliage = null;

    #[ORM\Column]
    private bool $emballage = false;

    /*
     * =========================================================
     * PRODUCTION
     * =========================================================
     */

    #[ORM\Column]
    private bool $batValide = false;

    #[ORM\Column]
    private bool $etat = true;

    #[ORM\Column(length: 30)]
    private string $priorite = 'normale';

    #[ORM\Column(nullable: true)]
    private ?int $tempsEstime = null;

    #[ORM\Column(nullable: true)]
    private ?int $tempsReel = null;

    #[ORM\Column(length: 255, nullable: true)]
    private ?string $fichier = null;

    #[ORM\Column(type: Types::TEXT, nullable: true)]
    private ?string $observation = null;

    /*
     * =========================================================
     * COLLECTIONS
     * =========================================================
     */

    /**
     * @var Collection<int, Production>
     */
    #[ORM\OneToMany(
        targetEntity: Production::class,
        mappedBy: 'commandeDetails'
    )]
    private Collection $productions;

    /**
     * @var Collection<int, StockSorties>
     */
    #[ORM\OneToMany(
        targetEntity: StockSorties::class,
        mappedBy: 'commandeDetail'
    )]
    private Collection $stockSorties;

    public function __construct()
    {
        $this->productions = new ArrayCollection();
        $this->stockSorties = new ArrayCollection();
    }

    /*
     * =========================================================
     * IDENTIFIANT
     * =========================================================
     */

    public function getId(): ?int
    {
        return $this->id;
    }

    /*
     * =========================================================
     * COMMANDE
     * =========================================================
     */

    public function getCommande(): ?Commandes
    {
        return $this->commande;
    }

    public function setCommande(?Commandes $commande): static
    {
        $this->commande = $commande;

        return $this;
    }

    /*
     * =========================================================
     * PRODUIT
     * =========================================================
     */

    public function getProduit(): ?Produits
    {
        return $this->produit;
    }

    public function setProduit(?Produits $produit): static
    {
        $this->produit = $produit;

        return $this;
    }

    /*
     * =========================================================
     * TYPE D’IMPRESSION
     * =========================================================
     */

    public function getTypeImpression(): ?TypesImpression
    {
        return $this->typeImpression;
    }

    public function setTypeImpression(
        ?TypesImpression $typeImpression
    ): static {
        $this->typeImpression = $typeImpression;

        return $this;
    }

    /*
     * =========================================================
     * SUPPORT
     * =========================================================
     */

    public function getSupport(): ?Supports
    {
        return $this->support;
    }

    public function setSupport(?Supports $support): static
    {
        $this->support = $support;

        return $this;
    }

    /*
     * =========================================================
     * MACHINE
     * =========================================================
     */

    public function getMachine(): ?Machines
    {
        return $this->machine;
    }

    public function setMachine(?Machines $machine): static
    {
        $this->machine = $machine;

        return $this;
    }

    /*
     * =========================================================
     * FORMAT
     * =========================================================
     */

    public function getFormat(): ?Format
    {
        return $this->format;
    }

    public function setFormat(?Format $format): static
    {
        $this->format = $format;

        return $this;
    }

    /*
     * =========================================================
     * DÉSIGNATION
     * =========================================================
     */

    public function getDesignation(): ?string
    {
        return $this->designation;
    }

    public function setDesignation(string $designation): static
    {
        $this->designation = trim($designation);

        return $this;
    }

    /*
     * =========================================================
     * DIMENSIONS
     * =========================================================
     */

    public function getLargeur(): ?string
    {
        return $this->largeur;
    }

    public function setLargeur(?string $largeur): static
    {
        $this->largeur = $largeur;

        return $this;
    }

    public function getLongueur(): ?string
    {
        return $this->longueur;
    }

    public function setLongueur(?string $longueur): static
    {
        $this->longueur = $longueur;

        return $this;
    }

    public function getSurface(): ?string
    {
        return $this->surface;
    }

    public function setSurface(?string $surface): static
    {
        $this->surface = $surface;

        return $this;
    }

    /*
     * Recalcule la surface à partir de la largeur et de la longueur.
     *
     * Cette méthode suppose que les deux dimensions utilisent
     * la même unité.
     */
    public function calculerSurface(): static
    {
        if ($this->largeur === null || $this->longueur === null) {
            $this->surface = null;

            return $this;
        }

        $surface = (float) $this->largeur * (float) $this->longueur;

        $this->surface = number_format(
            $surface,
            4,
            '.',
            ''
        );

        return $this;
    }

    /*
     * =========================================================
     * QUANTITÉ ET TARIFICATION
     * =========================================================
     */

    public function getQuantite(): int
    {
        return $this->quantite;
    }

    public function setQuantite(int $quantite): static
    {
        $this->quantite = max(1, $quantite);

        return $this;
    }

    public function getPrixUnitaire(): int
    {
        return $this->prixUnitaire;
    }

    public function setPrixUnitaire(int $prixUnitaire): static
    {
        $this->prixUnitaire = max(0, $prixUnitaire);

        return $this;
    }

    public function getCoutRevient(): int
    {
        return $this->coutRevient;
    }

    public function setCoutRevient(int $coutRevient): static
    {
        $this->coutRevient = max(0, $coutRevient);

        return $this;
    }

    public function getRemise(): int
    {
        return $this->remise;
    }

    public function setRemise(int $remise): static
    {
        $this->remise = max(0, $remise);

        return $this;
    }

    public function getTva(): int
    {
        return $this->tva;
    }

    public function setTva(int $tva): static
    {
        $this->tva = max(0, $tva);

        return $this;
    }

    public function getTotalHt(): int
    {
        return $this->totalHt;
    }

    public function setTotalHt(int $totalHt): static
    {
        $this->totalHt = max(0, $totalHt);

        return $this;
    }

    public function getTotalTtc(): int
    {
        return $this->totalTtc;
    }

    public function setTotalTtc(int $totalTtc): static
    {
        $this->totalTtc = max(0, $totalTtc);

        return $this;
    }

    /*
     * Recalcule les montants.
     *
     * La remise et la TVA sont considérées ici comme des
     * pourcentages entiers.
     */
    public function calculerTotaux(): static
    {
        $montantBrut = $this->prixUnitaire * $this->quantite;

        $montantRemise = (int) round(
            $montantBrut * $this->remise / 100
        );

        $this->totalHt = max(
            0,
            $montantBrut - $montantRemise
        );

        $montantTva = (int) round(
            $this->totalHt * $this->tva / 100
        );

        $this->totalTtc = $this->totalHt + $montantTva;

        return $this;
    }

    /*
     * =========================================================
     * PARAMÈTRES D’IMPRESSION
     * =========================================================
     */

    public function getProfilCouleurs(): ?string
    {
        return $this->profilCouleurs;
    }

    public function setProfilCouleurs(
        ?string $profilCouleurs
    ): static {
        $this->profilCouleurs = $profilCouleurs !== null
            ? trim($profilCouleurs)
            : null;

        return $this;
    }

    public function getResolution(): ?string
    {
        return $this->resolution;
    }

    public function setResolution(?string $resolution): static
    {
        $this->resolution = $resolution !== null
            ? trim($resolution)
            : null;

        return $this;
    }

    public function getGrammage(): ?string
    {
        return $this->grammage;
    }

    public function setGrammage(?string $grammage): static
    {
        $this->grammage = $grammage !== null
            ? trim($grammage)
            : null;

        return $this;
    }

    public function getEpaisseur(): ?string
    {
        return $this->epaisseur;
    }

    public function setEpaisseur(?string $epaisseur): static
    {
        $this->epaisseur = $epaisseur !== null
            ? trim($epaisseur)
            : null;

        return $this;
    }

    public function isRectoVerso(): bool
    {
        return $this->rectoVerso;
    }

    public function setRectoVerso(bool $rectoVerso): static
    {
        $this->rectoVerso = $rectoVerso;

        return $this;
    }

    public function getNombreFaces(): int
    {
        return $this->nombreFaces;
    }

    public function setNombreFaces(int $nombreFaces): static
    {
        $this->nombreFaces = max(1, $nombreFaces);

        return $this;
    }

    /*
     * =========================================================
     * FINITIONS ET OPTIONS
     * =========================================================
     */

    public function getLaminage(): ?string
    {
        return $this->laminage;
    }

    public function setLaminage(?string $laminage): static
    {
        $this->laminage = $laminage !== null
            ? trim($laminage)
            : null;

        return $this;
    }

    public function isOeillets(): bool
    {
        return $this->oeillets;
    }

    public function setOeillets(bool $oeillets): static
    {
        $this->oeillets = $oeillets;

        return $this;
    }

    public function isDecoupe(): bool
    {
        return $this->decoupe;
    }

    public function setDecoupe(bool $decoupe): static
    {
        $this->decoupe = $decoupe;

        return $this;
    }

    public function getPliage(): ?string
    {
        return $this->pliage;
    }

    public function setPliage(?string $pliage): static
    {
        $this->pliage = $pliage !== null
            ? trim($pliage)
            : null;

        return $this;
    }

    public function isEmballage(): bool
    {
        return $this->emballage;
    }

    public function setEmballage(bool $emballage): static
    {
        $this->emballage = $emballage;

        return $this;
    }

    /*
     * =========================================================
     * BAT ET ÉTAT DE PRODUCTION
     * =========================================================
     */

    public function isBatValide(): bool
    {
        return $this->batValide;
    }

    public function setBatValide(bool $batValide): static
    {
        $this->batValide = $batValide;

        return $this;
    }

    public function isEtat(): bool
    {
        return $this->etat;
    }

    public function setEtat(bool $etat): static
    {
        $this->etat = $etat;

        return $this;
    }

    public function getPriorite(): string
    {
        return $this->priorite;
    }

    public function setPriorite(string $priorite): static
    {
        $prioritesAutorisees = [
            'basse',
            'normale',
            'haute',
            'urgente',
        ];

        $priorite = strtolower(trim($priorite));

        $this->priorite = in_array(
            $priorite,
            $prioritesAutorisees,
            true
        )
            ? $priorite
            : 'normale';

        return $this;
    }

    public function getTempsEstime(): ?int
    {
        return $this->tempsEstime;
    }

    public function setTempsEstime(?int $tempsEstime): static
    {
        $this->tempsEstime = $tempsEstime !== null
            ? max(0, $tempsEstime)
            : null;

        return $this;
    }

    public function getTempsReel(): ?int
    {
        return $this->tempsReel;
    }

    public function setTempsReel(?int $tempsReel): static
    {
        $this->tempsReel = $tempsReel !== null
            ? max(0, $tempsReel)
            : null;

        return $this;
    }

    public function getFichier(): ?string
    {
        return $this->fichier;
    }

    public function setFichier(?string $fichier): static
    {
        $this->fichier = $fichier !== null
            ? trim($fichier)
            : null;

        return $this;
    }

    public function getObservation(): ?string
    {
        return $this->observation;
    }

    public function setObservation(?string $observation): static
    {
        $this->observation = $observation !== null
            ? trim($observation)
            : null;

        return $this;
    }

    /*
     * =========================================================
     * PRODUCTIONS
     * =========================================================
     */

    /**
     * @return Collection<int, Production>
     */
    public function getProductions(): Collection
    {
        return $this->productions;
    }

    public function addProduction(
        Production $production
    ): static {
        if (!$this->productions->contains($production)) {
            $this->productions->add($production);
            $production->setCommandeDetails($this);
        }

        return $this;
    }

    public function removeProduction(
        Production $production
    ): static {
        if ($this->productions->removeElement($production)) {
            if ($production->getCommandeDetails() === $this) {
                $production->setCommandeDetails(null);
            }
        }

        return $this;
    }

    /*
     * =========================================================
     * SORTIES DE STOCK
     * =========================================================
     */

    /**
     * @return Collection<int, StockSorties>
     */
    public function getStockSorties(): Collection
    {
        return $this->stockSorties;
    }

    public function addStockSorty(
        StockSorties $stockSorty
    ): static {
        if (!$this->stockSorties->contains($stockSorty)) {
            $this->stockSorties->add($stockSorty);
            $stockSorty->setCommandeDetail($this);
        }

        return $this;
    }

    public function removeStockSorty(
        StockSorties $stockSorty
    ): static {
        if ($this->stockSorties->removeElement($stockSorty)) {
            if ($stockSorty->getCommandeDetail() === $this) {
                $stockSorty->setCommandeDetail(null);
            }
        }

        return $this;
    }

    /*
     * =========================================================
     * AFFICHAGE
     * =========================================================
     */

    public function __toString(): string
    {
        return sprintf(
            '%s — %d unité(s)',
            $this->designation ?? 'Détail de commande',
            $this->quantite
        );
    }
}