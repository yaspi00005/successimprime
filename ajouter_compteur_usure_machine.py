#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ajoute le suivi automatique du compteur d'usure des machines
(m2 ou feuilles selon le mode de facturation), incremente a chaque
impression terminee. Fonctionnalite jamais livree jusqu'ici -- le
code existait deja mais aucun script n'avait ete envoye.

Touche 5 endroits :
  1. Nouvelle migration : colonne machines.compteur_feuilles ;
  2. src/Entity/Machines.php : champ compteurFeuilles +
     methode enregistrerUsage() ;
  3. src/Controller/ProductionController.php : appel de
     enregistrerUsage() a la fin de chaque production ;
  4. src/Controller/MachinesController.php : lecture/ecriture du
     champ compteurFeuilles (creation/edition/AJAX) ;
  5. templates/machines/index.html.twig : affichage "Feuilles"
     et champs de saisie dans les modales creation/edition.

IMPORTANT : ce script modifie du code, il ne modifie PAS la base
de donnees. Executez ensuite obligatoirement :
    php bin/console doctrine:migrations:migrate
pour creer la colonne compteur_feuilles.

Usage:
    python3 ajouter_compteur_usure_machine.py /chemin/vers/successImprim
"""

import os
import subprocess
import sys


def erreur_fatale(message):
    print("\n[ERREUR FATALE] " + message)
    sys.exit(1)


def verifier_racine(racine):
    print("=" * 70)
    print("DIAGNOSTIC DE L'EMPLACEMENT")
    print("=" * 70)
    print("Repertoire courant (pwd)      : " + os.getcwd())
    print("Racine passee en argument     : " + racine)
    print("Racine resolue (chemin absolu): " + os.path.realpath(racine))

    composer_json = os.path.join(racine, "composer.json")
    if not os.path.isfile(composer_json):
        erreur_fatale(
            "Aucun 'composer.json' trouve dans " + os.path.realpath(racine) + "\n"
            "  => Relancez le script en pointant vers la racine du projet."
        )
    print("[OK] composer.json trouve : c'est bien la racine du projet.")
    print()




MIGRATION_CONTENU = '<?php\n\ndeclare(strict_types=1);\n\nnamespace DoctrineMigrations;\n\nuse Doctrine\\DBAL\\Schema\\Schema;\nuse Doctrine\\Migrations\\AbstractMigration;\n\nfinal class Version20260826120000 extends AbstractMigration\n{\n    public function getDescription(): string\n    {\n        return "Ajoute machines.compteur_feuilles (compteur d\'usure en "\n            . "feuilles A4-equivalent, pour les machines facturees a la feuille).";\n    }\n\n    public function up(Schema $schema): void\n    {\n        $this->addSql(\n            \'ALTER TABLE machines ADD compteur_feuilles INT DEFAULT 0 NOT NULL\'\n        );\n    }\n\n    public function down(Schema $schema): void\n    {\n        $this->addSql(\'ALTER TABLE machines DROP compteur_feuilles\');\n    }\n}\n'




def creer_migration(racine):
    chemin_relatif = "migrations/Version20260826120000.php"
    chemin_absolu = os.path.join(racine, chemin_relatif)

    if os.path.isfile(chemin_absolu):
        print("[SKIP] " + chemin_relatif + " existe deja (deja applique).")
        return True

    os.makedirs(os.path.dirname(chemin_absolu), exist_ok=True)

    with open(chemin_absolu, "w", encoding="utf-8", newline="") as f:
        f.write(MIGRATION_CONTENU)
        f.flush()
        os.fsync(f.fileno())

    print("[OK CREE] " + chemin_relatif)
    print("  Chemin reel : " + os.path.realpath(chemin_absolu))
    return True


def appliquer_paires(racine, chemin_relatif, marqueur, paires, diagnostic, repetitions=None):
    """
    paires: liste de (ancien, nouveau). Chaque paire est appliquee
    independamment (si une echoue, les autres sont quand meme
    tentees) ; repetitions permet de forcer un nombre de
    remplacements pour une paire donnee (par defaut 1).
    """
    chemin_absolu = os.path.join(racine, chemin_relatif)

    if not os.path.isfile(chemin_absolu):
        print("[ABSENT] " + chemin_relatif + " n'existe pas du tout sur le disque.")
        return False

    with open(chemin_absolu, "r", encoding="utf-8") as f:
        contenu = f.read()

    if marqueur in contenu:
        print("[SKIP] " + chemin_relatif + " contient deja le correctif (deja applique).")
        return True

    contenu_original = contenu
    tout_ok = True

    for index, ancien_nouveau in enumerate(paires):
        ancien, nouveau = ancien_nouveau[0], ancien_nouveau[1]
        n = repetitions.get(index, 1) if repetitions else 1

        if nouveau in contenu:
            print("  [SKIP bloc " + str(index) + "] deja present.")
            continue

        occurrences = contenu.count(ancien)

        if occurrences < n:
            print("  [ECHEC bloc " + str(index) + "] reference introuvable (" + str(occurrences) + " trouvee(s), " + str(n) + " attendue(s)).")
            tout_ok = False
            continue

        contenu = contenu.replace(ancien, nouveau, n)
        print("  [OK bloc " + str(index) + "] applique.")

    if contenu == contenu_original:
        print("[ECHEC] " + chemin_relatif + " : aucun bloc n'a pu etre applique -> abandon (rien ecrit).")
        print("  Copiez-moi le resultat de :")
        print("    " + diagnostic)
        return False

    with open(chemin_absolu, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
        f.flush()
        os.fsync(f.fileno())

    with open(chemin_absolu, "r", encoding="utf-8", newline="") as f:
        relu = f.read()

    if relu != contenu:
        print("[ECHEC VERIFICATION] " + chemin_relatif + " : le contenu relu ne correspond pas.")
        return False

    print("[OK VERIFIE] " + chemin_relatif + (" (partiel, voir ci-dessus)" if not tout_ok else ""))
    print("  Chemin reel : " + os.path.realpath(chemin_absolu))
    return tout_ok



MACHINES_PHP_PAIRES = [
    (
        '    #[ORM\\Column(type: Types::INTEGER)]\n    private ?int $nbTetes = null;\n\n    #[ORM\\Column(type: Types::DATE_MUTABLE)]\n    private ?\\DateTime $dateAchat = null;\n\n    #[ORM\\Column(type: Types::DATE_MUTABLE)]\n    private ?\\DateTime $DateMiseService = null;\n\n    #[ORM\\Column(type: Types::INTEGER)]\n    private ?int $compteurM2 = null;\n\n    #[ORM\\Column(type: Types::INTEGER)]\n    private ?int $compteurHeures = null;\n\n    #[ORM\\Column(length: 20)]\n    private ?string $etat = null;\n\n    #[ORM\\Column(length: 50, unique: true, nullable: true)]\n    private ?string $numeroMachine = null;\n\n    #[ORM\\Column(length: 45, unique: true)]\n    private ?string $adresseIp = null;\n\n    /*\n     * ============================================================\n     * RENTABILITÉ / AMORTISSEMENT\n     * ============================================================\n     */\n',
        "    #[ORM\\Column(type: Types::INTEGER)]\n    private ?int $nbTetes = null;\n\n    #[ORM\\Column(type: Types::DATE_MUTABLE)]\n    private ?\\DateTime $dateAchat = null;\n\n    #[ORM\\Column(type: Types::DATE_MUTABLE)]\n    private ?\\DateTime $DateMiseService = null;\n\n    #[ORM\\Column(type: Types::INTEGER)]\n    private ?int $compteurM2 = null;\n\n    #[ORM\\Column(type: Types::INTEGER)]\n    private ?int $compteurHeures = null;\n\n    /*\n     * Compteur en feuilles A4-équivalent (une A3 compte pour 2 A4),\n     * pour les machines facturées à la feuille. Distinct de\n     * compteurM2, réservé aux machines grand format.\n     */\n    #[ORM\\Column(type: Types::INTEGER, options: ['default' => 0])]\n    private int $compteurFeuilles = 0;\n\n    #[ORM\\Column(length: 20)]\n    private ?string $etat = null;\n\n    #[ORM\\Column(length: 50, unique: true, nullable: true)]\n    private ?string $numeroMachine = null;\n\n    #[ORM\\Column(length: 45, unique: true)]\n    private ?string $adresseIp = null;\n\n    /*\n     * ============================================================\n     * RENTABILITÉ / AMORTISSEMENT\n     * ============================================================\n     */\n",
    ),
    (
        '        return $this;\n    }\n\n    public function getCompteurHeures(): ?int\n    {\n        return $this->compteurHeures;\n    }\n\n    public function setCompteurHeures(int $compteurHeures): static\n    {\n        $this->compteurHeures = $compteurHeures;\n\n        return $this;\n    }\n\n    public function getEtat(): ?string\n    {\n        return $this->etat;\n    }\n\n    public function setEtat(string $etat): static\n    {\n        $this->etat = $etat;\n\n        return $this;\n    }\n\n    /**\n     * @return Collection<int, CommandesDetails>\n     */',
        '        return $this;\n    }\n\n    public function getCompteurHeures(): ?int\n    {\n        return $this->compteurHeures;\n    }\n\n    public function setCompteurHeures(int $compteurHeures): static\n    {\n        $this->compteurHeures = $compteurHeures;\n\n        return $this;\n    }\n\n    public function getCompteurFeuilles(): int\n    {\n        return $this->compteurFeuilles;\n    }\n\n    public function setCompteurFeuilles(int $compteurFeuilles): static\n    {\n        $this->compteurFeuilles = $compteurFeuilles;\n\n        return $this;\n    }\n\n    public function getEtat(): ?string\n    {\n        return $this->etat;\n    }\n\n    public function setEtat(string $etat): static\n    {\n        $this->etat = $etat;\n\n        return $this;\n    }\n\n    /**\n     * @return Collection<int, CommandesDetails>\n     */',
    ),
    (
        '    public function getModeFacturationLabel(): string\n    {\n        return self::MODES_FACTURATION_LABELS[$this->modeFacturation] ?? $this->modeFacturation;\n    }\n\n    public function utiliseSurface(): bool\n    {\n        return $this->modeFacturation === self::MODE_FACTURATION_METRE_CARRE;\n    }\n\n    public function utiliseFeuille(): bool\n    {\n        return $this->modeFacturation === self::MODE_FACTURATION_FEUILLE;\n    }\n\n    public function getPrixAchat(): ?int\n    {\n        return $this->prixAchat;\n    }\n\n    public function setPrixAchat(?int $prixAchat): static\n    {\n        $this->prixAchat = $prixAchat;\n\n        return $this;\n    }\n\n    public function getDureeAmortissementMois(): ?int\n    {\n        return $this->dureeAmortissementMois;',
        "    public function getModeFacturationLabel(): string\n    {\n        return self::MODES_FACTURATION_LABELS[$this->modeFacturation] ?? $this->modeFacturation;\n    }\n\n    public function utiliseSurface(): bool\n    {\n        return $this->modeFacturation === self::MODE_FACTURATION_METRE_CARRE;\n    }\n\n    public function utiliseFeuille(): bool\n    {\n        return $this->modeFacturation === self::MODE_FACTURATION_FEUILLE;\n    }\n\n    /*\n     * Surface d'une feuille A4, en m² (0,21 x 0,297) — sert de\n     * référence pour convertir une surface imprimée en nombre de\n     * feuilles A4-équivalent (une A3 compte pour 2 A4).\n     */\n    private const SURFACE_A4_M2 = 0.21 * 0.297;\n\n    /**\n     * Ajoute l'usage d'une impression au compteur d'usure de la\n     * machine, uniquement pour suivre la maintenance — n'affecte pas\n     * le calcul de l'amortissement (basé sur le temps écoulé, voir\n     * getChargeAmortissementMensuelle()). Le compteur alimenté dépend\n     * du mode de facturation de la machine.\n     */\n    public function enregistrerUsage(float $surfaceM2Totale): void\n    {\n        if ($surfaceM2Totale <= 0) {\n            return;\n        }\n\n        if ($this->utiliseSurface()) {\n            $this->compteurM2 = ($this->compteurM2 ?? 0) + (int) round($surfaceM2Totale);\n\n            return;\n        }\n\n        if ($this->utiliseFeuille()) {\n            $this->compteurFeuilles += (int) round(\n                $surfaceM2Totale / self::SURFACE_A4_M2\n            );\n        }\n    }\n\n    public function getPrixAchat(): ?int\n    {\n        return $this->prixAchat;\n    }\n\n    public function setPrixAchat(?int $prixAchat): static\n    {\n        $this->prixAchat = $prixAchat;\n\n        return $this;\n    }\n\n    public function getDureeAmortissementMois(): ?int\n    {\n        return $this->dureeAmortissementMois;",
    ),
]

PRODUCTION_PHP_PAIRES = [
    (
        '$ordre->terminer(\n            $utilisateur,\n            $quantiteProduite,\n            $quantiteRebut,\n            $observation\n        );\n\n        /*\n         * ========================================================\n         * NOTIFICATION',
        "$ordre->terminer(\n            $utilisateur,\n            $quantiteProduite,\n            $quantiteRebut,\n            $observation\n        );\n\n        /*\n         * ========================================================\n         * COMPTEUR D'USURE MACHINE\n         * ========================================================\n         *\n         * Suivi de l'usage uniquement (maintenance) : n'affecte pas\n         * l'amortissement, calculé sur le temps écoulé. Alimente\n         * compteurM2 ou compteurFeuilles selon le mode de facturation\n         * de la machine ; ignoré si la ligne n'a pas de dimensions\n         * (article en stock, saisie libre).\n         */\n        $machineUtilisee = $ordre->getMachine();\n\n        if ($machineUtilisee instanceof Machines) {\n            $largeurDetail = (float) ($detail->getLargeur() ?? 0);\n            $longueurDetail = (float) ($detail->getLongueur() ?? 0);\n\n            if ($largeurDetail > 0 && $longueurDetail > 0) {\n                $machineUtilisee->enregistrerUsage(\n                    $largeurDetail * $longueurDetail * $quantiteTraitee\n                );\n            }\n        }\n\n        /*\n         * ========================================================\n         * NOTIFICATION",
    ),
]

MACHINESCONTROLLER_PHP_PAIRES = [
    (
        "        /*\n         * Compteurs.\n         */\n        $compteurM2 = $this->recupererEntier(\n            $request,\n            'compteurM2',\n            0\n        );\n\n        $compteurHeures = $this->recupererEntier(\n            $request,\n            'compteurHeures',\n            0\n        );\n\n        /*\n         * Dates.\n         */\n        $dateAchat = $this->recupererDate(\n            $request,\n            'dateAchat'\n        );\n\n        $dateMiseService = $this->recupererDate(\n            $request,\n            'dateMiseService'\n        );\n\n        /*\n         * Rentabilité / amortissement.",
        "        /*\n         * Compteurs.\n         */\n        $compteurM2 = $this->recupererEntier(\n            $request,\n            'compteurM2',\n            0\n        );\n\n        $compteurHeures = $this->recupererEntier(\n            $request,\n            'compteurHeures',\n            0\n        );\n\n        $compteurFeuilles = $this->recupererEntier(\n            $request,\n            'compteurFeuilles',\n            0\n        );\n\n        /*\n         * Dates.\n         */\n        $dateAchat = $this->recupererDate(\n            $request,\n            'dateAchat'\n        );\n\n        $dateMiseService = $this->recupererDate(\n            $request,\n            'dateMiseService'\n        );\n\n        /*\n         * Rentabilité / amortissement.",
    ),
    (
        '\n        /*\n         * Affectation.\n         */\n        $machine\n            ->setNom($nom)\n            ->setAdresseIp($adresseIp)\n            ->setMarque($marque)\n            ->setModeles($modeles)\n            ->setNumeroSerie($numeroSerie)\n            ->setTypeMachine($typeMachine)\n            ->setLargeurImpression($largeurImpression)\n            ->setNbTetes($nbTetes)\n            ->setCompteurM2($compteurM2)\n            ->setCompteurHeures($compteurHeures)\n            ->setEtat($etat)\n            ->setModeFacturation($modeFacturation)\n            ->setPrixAchat($prixAchat)\n            ->setDureeAmortissementMois($dureeAmortissementMois)\n            ->setRevenuAvantSuivi($revenuAvantSuivi)\n            ->setDateDebutSuivi($dateDebutSuivi);\n\n        if ($dateAchat !== null) {\n            $machine->setDateAchat(\n                $dateAchat\n            );\n        }\n\n        if ($dateMiseService !== null) {\n            $machine->setDateMiseService(',
        '\n        /*\n         * Affectation.\n         */\n        $machine\n            ->setNom($nom)\n            ->setAdresseIp($adresseIp)\n            ->setMarque($marque)\n            ->setModeles($modeles)\n            ->setNumeroSerie($numeroSerie)\n            ->setTypeMachine($typeMachine)\n            ->setLargeurImpression($largeurImpression)\n            ->setNbTetes($nbTetes)\n            ->setCompteurM2($compteurM2)\n            ->setCompteurHeures($compteurHeures)\n            ->setCompteurFeuilles($compteurFeuilles)\n            ->setEtat($etat)\n            ->setModeFacturation($modeFacturation)\n            ->setPrixAchat($prixAchat)\n            ->setDureeAmortissementMois($dureeAmortissementMois)\n            ->setRevenuAvantSuivi($revenuAvantSuivi)\n            ->setDateDebutSuivi($dateDebutSuivi);\n\n        if ($dateAchat !== null) {\n            $machine->setDateAchat(\n                $dateAchat\n            );\n        }\n\n        if ($dateMiseService !== null) {\n            $machine->setDateMiseService(',
    ),
    (
        "                : null,\n\n            'dateMiseService' =>\n                $machine->getDateMiseService()\n                    ? $machine\n                        ->getDateMiseService()\n                        ->format('Y-m-d')\n                    : null,\n\n            'compteurM2' =>\n                $machine->getCompteurM2(),\n\n            'compteurHeures' =>\n                $machine->getCompteurHeures(),\n\n            'etat' => $machine->getEtat(),\n\n            'modeFacturation' => $machine->getModeFacturation(),\n            'prixAchat' => $machine->getPrixAchat(),\n            'dureeAmortissementMois' => $machine->getDureeAmortissementMois(),\n            'revenuAvantSuivi' => $machine->getRevenuAvantSuivi(),\n\n            'dateDebutSuivi' => $machine->getDateDebutSuivi()\n                ? $machine->getDateDebutSuivi()->format('Y-m-d')\n                : null,\n        ];\n    }\n\n    /*\n     * ============================================================",
        "                : null,\n\n            'dateMiseService' =>\n                $machine->getDateMiseService()\n                    ? $machine\n                        ->getDateMiseService()\n                        ->format('Y-m-d')\n                    : null,\n\n            'compteurM2' =>\n                $machine->getCompteurM2(),\n\n            'compteurHeures' =>\n                $machine->getCompteurHeures(),\n\n            'compteurFeuilles' =>\n                $machine->getCompteurFeuilles(),\n\n            'etat' => $machine->getEtat(),\n\n            'modeFacturation' => $machine->getModeFacturation(),\n            'prixAchat' => $machine->getPrixAchat(),\n            'dureeAmortissementMois' => $machine->getDureeAmortissementMois(),\n            'revenuAvantSuivi' => $machine->getRevenuAvantSuivi(),\n\n            'dateDebutSuivi' => $machine->getDateDebutSuivi()\n                ? $machine->getDateDebutSuivi()->format('Y-m-d')\n                : null,\n        ];\n    }\n\n    /*\n     * ============================================================",
    ),
]

MACHINES_TWIG_PAIRES = [
    (
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t{{ machine.compteurHeures\n                                                        is not null\n                                                        ? machine.compteurHeures\n                                                        : 0\n                                                    }}\n\t\t\t\t\t\t\t\t\t\t\t\t\t</strong>\n\t\t\t\t\t\t\t\t\t\t\t\t</div>\n\n\t\t\t\t\t\t\t\t\t\t\t</td>\n\n\n\t\t\t\t\t\t\t\t\t\t\t{# ==================================================\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t                                           ÉTAT\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t                                           ================================================== #}\n\t\t\t\t\t\t\t\t\t\t\t<td class="text-center\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t                                                   align-middle">',
        '\t\t\t\t\t\t\t\t\t\t\t\t\t\t{{ machine.compteurHeures\n                                                        is not null\n                                                        ? machine.compteurHeures\n                                                        : 0\n                                                    }}\n\t\t\t\t\t\t\t\t\t\t\t\t\t</strong>\n\t\t\t\t\t\t\t\t\t\t\t\t</div>\n\n\t\t\t\t\t\t\t\t\t\t\t\t<div>\n\t\t\t\t\t\t\t\t\t\t\t\t\t<small class="text-muted">\n\t\t\t\t\t\t\t\t\t\t\t\t\t\tFeuilles :\n\t\t\t\t\t\t\t\t\t\t\t\t\t</small>\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t<strong>\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t{{ machine.compteurFeuilles|default(0) }}\n\t\t\t\t\t\t\t\t\t\t\t\t\t</strong>\n\t\t\t\t\t\t\t\t\t\t\t\t</div>\n\n\t\t\t\t\t\t\t\t\t\t\t</td>\n\n\n\t\t\t\t\t\t\t\t\t\t\t{# ==================================================\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t                                           ÉTAT\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t                                           ================================================== #}\n\t\t\t\t\t\t\t\t\t\t\t<td class="text-center\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t                                                   align-middle">',
    ),
    (
        '\n\t\t\t\t\t\t\t\t<input type="number" id="machineCreateCompteurHeures" class="form-control" min="0" step="1" value="0">\n\n\t\t\t\t\t\t\t</div>\n\n\t\t\t\t\t\t</div>\n\n\n\t\t\t\t\t\t<div class="col-12">\n\t\t\t\t\t\t\t<hr>\n\t\t\t\t\t\t\t<h6 class="text-muted">Rentabilité / amortissement</h6>\n\t\t\t\t\t\t</div>\n\n\n\t\t\t\t\t\t{# MODE FACTURATION #}\n\t\t\t\t\t\t<div class="col-md-4">',
        '\n\t\t\t\t\t\t\t\t<input type="number" id="machineCreateCompteurHeures" class="form-control" min="0" step="1" value="0">\n\n\t\t\t\t\t\t\t</div>\n\n\t\t\t\t\t\t</div>\n\n\n\t\t\t\t\t\t{# COMPTEUR FEUILLES #}\n\t\t\t\t\t\t<div class="col-md-6">\n\n\t\t\t\t\t\t\t<div class="form-group">\n\n\t\t\t\t\t\t\t\t<label class="form-label" for="machineCreateCompteurFeuilles">\n\t\t\t\t\t\t\t\t\tCompteur feuilles (A4-équivalent)\n\t\t\t\t\t\t\t\t</label>\n\n\t\t\t\t\t\t\t\t<input type="number" id="machineCreateCompteurFeuilles" class="form-control" min="0" step="1" value="0">\n\n\t\t\t\t\t\t\t</div>\n\n\t\t\t\t\t\t</div>\n\n\n\t\t\t\t\t\t<div class="col-12">\n\t\t\t\t\t\t\t<hr>\n\t\t\t\t\t\t\t<h6 class="text-muted">Rentabilité / amortissement</h6>\n\t\t\t\t\t\t</div>\n\n\n\t\t\t\t\t\t{# MODE FACTURATION #}\n\t\t\t\t\t\t<div class="col-md-4">',
    ),
    (
        '\n\t\t\t\t\t\t\t\t<input type="number" id="machineEditCompteurHeures" class="form-control" min="0" step="1">\n\n\t\t\t\t\t\t\t</div>\n\n\t\t\t\t\t\t</div>\n\n\n\t\t\t\t\t\t<div class="col-12">\n\t\t\t\t\t\t\t<hr>\n\t\t\t\t\t\t\t<h6 class="text-muted">Rentabilité / amortissement</h6>\n\t\t\t\t\t\t</div>\n\n\n\t\t\t\t\t\t<div class="col-md-4">\n',
        '\n\t\t\t\t\t\t\t\t<input type="number" id="machineEditCompteurHeures" class="form-control" min="0" step="1">\n\n\t\t\t\t\t\t\t</div>\n\n\t\t\t\t\t\t</div>\n\n\n\t\t\t\t\t\t<div class="col-md-6">\n\n\t\t\t\t\t\t\t<div class="form-group">\n\n\t\t\t\t\t\t\t\t<label class="form-label" for="machineEditCompteurFeuilles">\n\t\t\t\t\t\t\t\t\tCompteur feuilles (A4-équivalent)\n\t\t\t\t\t\t\t\t</label>\n\n\t\t\t\t\t\t\t\t<input type="number" id="machineEditCompteurFeuilles" class="form-control" min="0" step="1">\n\n\t\t\t\t\t\t\t</div>\n\n\t\t\t\t\t\t</div>\n\n\n\t\t\t\t\t\t<div class="col-12">\n\t\t\t\t\t\t\t<hr>\n\t\t\t\t\t\t\t<h6 class="text-muted">Rentabilité / amortissement</h6>\n\t\t\t\t\t\t</div>\n\n\n\t\t\t\t\t\t<div class="col-md-4">\n',
    ),
    (
        "const dateAchat = valeur('machineCreateDateAchat');\n\nconst dateMiseService = valeur('machineCreateDateMiseService');\n\nconst compteurM2 = valeur('machineCreateCompteurM2');\n\nconst compteurHeures = valeur('machineCreateCompteurHeures');\n\nconst etat = valeur('machineCreateEtat');\n\nconst modeFacturation = valeur('machineCreateModeFacturation');\n\nconst prixAchat = valeur('machineCreatePrixAchat');\n\nconst dureeAmortissementMois = valeur('machineCreateDureeAmortissementMois');\n",
        "const dateAchat = valeur('machineCreateDateAchat');\n\nconst dateMiseService = valeur('machineCreateDateMiseService');\n\nconst compteurM2 = valeur('machineCreateCompteurM2');\n\nconst compteurHeures = valeur('machineCreateCompteurHeures');\n\nconst compteurFeuilles = valeur('machineCreateCompteurFeuilles');\n\nconst etat = valeur('machineCreateEtat');\n\nconst modeFacturation = valeur('machineCreateModeFacturation');\n\nconst prixAchat = valeur('machineCreatePrixAchat');\n\nconst dureeAmortissementMois = valeur('machineCreateDureeAmortissementMois');\n",
    ),
    (
        "formData.append('dateAchat', dateAchat);\n\nformData.append('dateMiseService', dateMiseService);\n\nformData.append('compteurM2', compteurM2 || '0');\n\nformData.append('compteurHeures', compteurHeures || '0');\n\nformData.append('etat', etat || 'disponible');\n\nformData.append('modeFacturation', modeFacturation || 'metre_carre');\n\nformData.append('prixAchat', prixAchat);\n\nformData.append('dureeAmortissementMois', dureeAmortissementMois);\n",
        "formData.append('dateAchat', dateAchat);\n\nformData.append('dateMiseService', dateMiseService);\n\nformData.append('compteurM2', compteurM2 || '0');\n\nformData.append('compteurHeures', compteurHeures || '0');\n\nformData.append('compteurFeuilles', compteurFeuilles || '0');\n\nformData.append('etat', etat || 'disponible');\n\nformData.append('modeFacturation', modeFacturation || 'metre_carre');\n\nformData.append('prixAchat', prixAchat);\n\nformData.append('dureeAmortissementMois', dureeAmortissementMois);\n",
    ),
    (
        "definirValeur('machineEditDateAchat', machine.dateAchat);\n\ndefinirValeur('machineEditDateMiseService', machine.dateMiseService);\n\ndefinirValeur('machineEditCompteurM2', machine.compteurM2 ?? 0);\n\ndefinirValeur('machineEditCompteurHeures', machine.compteurHeures ?? 0);\n\ndefinirValeur('machineEditEtat', machine.etat || 'disponible');\n\ndefinirValeur('machineEditModeFacturation', machine.modeFacturation || 'metre_carre');\n\ndefinirValeur('machineEditPrixAchat', machine.prixAchat);\n\ndefinirValeur('machineEditDureeAmortissementMois', machine.dureeAmortissementMois);\n",
        "definirValeur('machineEditDateAchat', machine.dateAchat);\n\ndefinirValeur('machineEditDateMiseService', machine.dateMiseService);\n\ndefinirValeur('machineEditCompteurM2', machine.compteurM2 ?? 0);\n\ndefinirValeur('machineEditCompteurHeures', machine.compteurHeures ?? 0);\n\ndefinirValeur('machineEditCompteurFeuilles', machine.compteurFeuilles ?? 0);\n\ndefinirValeur('machineEditEtat', machine.etat || 'disponible');\n\ndefinirValeur('machineEditModeFacturation', machine.modeFacturation || 'metre_carre');\n\ndefinirValeur('machineEditPrixAchat', machine.prixAchat);\n\ndefinirValeur('machineEditDureeAmortissementMois', machine.dureeAmortissementMois);\n",
    ),
    (
        "const dateAchat = valeur('machineEditDateAchat');\n\nconst dateMiseService = valeur('machineEditDateMiseService');\n\nconst compteurM2 = valeur('machineEditCompteurM2');\n\nconst compteurHeures = valeur('machineEditCompteurHeures');\n\nconst etat = valeur('machineEditEtat');\n\nconst modeFacturation = valeur('machineEditModeFacturation');\n\nconst prixAchat = valeur('machineEditPrixAchat');\n\nconst dureeAmortissementMois = valeur('machineEditDureeAmortissementMois');\n",
        "const dateAchat = valeur('machineEditDateAchat');\n\nconst dateMiseService = valeur('machineEditDateMiseService');\n\nconst compteurM2 = valeur('machineEditCompteurM2');\n\nconst compteurHeures = valeur('machineEditCompteurHeures');\n\nconst compteurFeuilles = valeur('machineEditCompteurFeuilles');\n\nconst etat = valeur('machineEditEtat');\n\nconst modeFacturation = valeur('machineEditModeFacturation');\n\nconst prixAchat = valeur('machineEditPrixAchat');\n\nconst dureeAmortissementMois = valeur('machineEditDureeAmortissementMois');\n",
    ),
]



MARQUEUR_MACHINES_PHP = "public function enregistrerUsage"
MARQUEUR_PRODUCTION_PHP = "COMPTEUR D'USURE MACHINE"
MARQUEUR_MACHINESCONTROLLER_PHP = "compteurFeuilles = $this->recupererEntier"
MARQUEUR_MACHINES_TWIG = "machineCreateCompteurFeuilles"


def main():
    racine = sys.argv[1] if len(sys.argv) >= 2 else "."
    verifier_racine(racine)

    resultats = []

    print("-" * 70)
    print("migrations/Version20260826120000.php (nouveau fichier)")
    print("-" * 70)
    resultats.append(creer_migration(racine))
    print()

    print("-" * 70)
    print("src/Entity/Machines.php")
    print("-" * 70)
    resultats.append(appliquer_paires(
        racine, "src/Entity/Machines.php", MARQUEUR_MACHINES_PHP,
        MACHINES_PHP_PAIRES,
        "grep -n -B2 -A10 \"compteurHeures\" src/Entity/Machines.php"
    ))
    print()

    print("-" * 70)
    print("src/Controller/ProductionController.php")
    print("-" * 70)
    resultats.append(appliquer_paires(
        racine, "src/Controller/ProductionController.php", MARQUEUR_PRODUCTION_PHP,
        PRODUCTION_PHP_PAIRES,
        "grep -n -B3 -A3 \"ordre->terminer\" src/Controller/ProductionController.php"
    ))
    print()

    print("-" * 70)
    print("src/Controller/MachinesController.php")
    print("-" * 70)
    resultats.append(appliquer_paires(
        racine, "src/Controller/MachinesController.php", MARQUEUR_MACHINESCONTROLLER_PHP,
        MACHINESCONTROLLER_PHP_PAIRES,
        "grep -n -B2 -A5 \"compteurHeures = \\$this\" src/Controller/MachinesController.php"
    ))
    print()

    print("-" * 70)
    print("templates/machines/index.html.twig")
    print("-" * 70)
    resultats.append(appliquer_paires(
        racine, "templates/machines/index.html.twig", MARQUEUR_MACHINES_TWIG,
        MACHINES_TWIG_PAIRES,
        "grep -n \"machineCreateCompteurHeures\\|machineEditCompteurHeures\" templates/machines/index.html.twig",
        repetitions={4: 2}
    ))
    print()

    try:
        r1 = subprocess.run(["php", "-l", os.path.join(racine, "src/Entity/Machines.php")], capture_output=True, text=True, timeout=30)
        print("php -l Machines.php : " + r1.stdout.strip() + r1.stderr.strip())

        r2 = subprocess.run(["php", "-l", os.path.join(racine, "src/Controller/ProductionController.php")], capture_output=True, text=True, timeout=30)
        print("php -l ProductionController.php : " + r2.stdout.strip() + r2.stderr.strip())

        r3 = subprocess.run(["php", "-l", os.path.join(racine, "src/Controller/MachinesController.php")], capture_output=True, text=True, timeout=30)
        print("php -l MachinesController.php : " + r3.stdout.strip() + r3.stderr.strip())
    except Exception:
        pass

    print()
    print("=" * 70)
    print("RESUME")
    print("=" * 70)

    if all(resultats):
        print("Tout est en place. Lancez maintenant, DANS CET ORDRE :")
        print("  php bin/console doctrine:migrations:migrate")
        print("  php bin/console cache:clear")
        print()
        print("A partir de maintenant, chaque impression terminee sur une")
        print("machine incremente automatiquement son compteur m2 (ou")
        print("feuilles, selon le mode de facturation de la machine).")
    else:
        print("Un ou plusieurs fichiers n'ont pas pu etre modifies (voir [ECHEC] ci-dessus).")
        print("Recopiez-moi TOUT ce resume, je corrige avant de vous renvoyer le script.")


if __name__ == "__main__":
    main()
