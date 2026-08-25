#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ajoute les decaissements automatiques (mensuels ou annuels) sur les
comptes de tresorerie : frais bancaires, remboursement de credit,
loyer... tout ce qui revient chaque mois/annee sans ressaisie
manuelle.

Cree :
  - src/Entity/DecaissementRecurrent.php
  - src/Repository/DecaissementRecurrentRepository.php
  - src/Service/DecaissementRecurrentService.php
  - src/Command/ExecuterDecaissementsRecurrentsCommand.php
  - src/Controller/DecaissementRecurrentController.php
  - src/Form/DecaissementRecurrentType.php
  - templates/decaissement_recurrent/index.html.twig
  - templates/decaissement_recurrent/_form.html.twig
  - templates/decaissement_recurrent/new.html.twig
  - templates/decaissement_recurrent/edit.html.twig
  - migrations/Version20260825090000.php
  - scripts/windows/decaissements_recurrents.bat
  - scripts/windows/installer_tache_decaissements_recurrents.bat

Modifie :
  - src/Entity/MouvementTresorerie.php (nouvelles categories "Frais
    bancaires" / "Remboursement de credit")
  - templates/base.html.twig (nouveau lien de menu, sous Tresorerie)

Usage:
    python3 ajouter_decaissements_recurrents.py /chemin/vers/successImprim

Apres application :
    php bin/console doctrine:migrations:migrate
    php bin/console cache:clear

Puis, UNE SEULE FOIS, en administrateur (clic droit "Executer en
tant qu'administrateur") :
    scripts\\windows\\installer_tache_decaissements_recurrents.bat
"""

import os
import sys
import shutil
import subprocess


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


PHP_LINT_DISPONIBLE = shutil.which("php") is not None


def lint_php_si_possible(chemin_absolu):
    if not PHP_LINT_DISPONIBLE:
        return
    try:
        resultat = subprocess.run(
            ["php", "-l", chemin_absolu],
            capture_output=True, text=True, timeout=10,
        )
        sortie = (resultat.stdout + resultat.stderr).strip()
        if resultat.returncode == 0:
            print("  php -l : OK")
        else:
            print("  [ATTENTION] php -l a signale un probleme :")
            print("  " + sortie.replace("\n", "\n  "))
    except Exception as exc:
        print("  (php -l ignore : " + repr(exc) + ")")


def appliquer_blocs_verifie(racine, chemin_relatif, marqueur, blocs):
    chemin_absolu = os.path.join(racine, chemin_relatif)

    if not os.path.isfile(chemin_absolu):
        print("[ABSENT] " + chemin_relatif + " n'existe pas du tout sur le disque.")
        return False

    with open(chemin_absolu, "r", encoding="utf-8") as f:
        contenu_original = f.read()

    if marqueur in contenu_original:
        print("[SKIP] " + chemin_relatif + " contient deja '" + marqueur + "' (deja applique).")
        return True

    contenu = contenu_original
    for idx, (ancien, nouveau) in enumerate(blocs, start=1):
        occurrences = contenu.count(ancien)
        if occurrences != 1:
            print("[ECHEC] " + chemin_relatif + " : bloc " + str(idx) + "/" + str(len(blocs)) +
                  " trouve " + str(occurrences) + " fois au lieu de 1 -> abandon (rien ecrit sur ce fichier).")
            print("  Extrait attendu (debut) : " + repr(ancien[:150]))
            return False
        contenu = contenu.replace(ancien, nouveau, 1)

    with open(chemin_absolu, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
        f.flush()
        os.fsync(f.fileno())

    with open(chemin_absolu, "r", encoding="utf-8", newline="") as f:
        relu = f.read()

    if relu != contenu:
        print("[ECHEC VERIFICATION] " + chemin_relatif + " : le contenu relu ne correspond pas.")
        return False

    print("[OK VERIFIE] " + chemin_relatif + " (" + str(len(blocs)) + " bloc(s) applique(s))")
    print("  Chemin reel : " + os.path.realpath(chemin_absolu))
    if chemin_relatif.endswith(".php"):
        lint_php_si_possible(chemin_absolu)
    return True


def creer_fichier_verifie(racine, chemin_relatif, contenu_attendu):
    chemin_absolu = os.path.join(racine, chemin_relatif)

    if os.path.isfile(chemin_absolu):
        with open(chemin_absolu, "r", encoding="utf-8") as f:
            contenu_existant = f.read()
        if contenu_existant == contenu_attendu:
            print("[SKIP] " + chemin_relatif + " existe deja et est identique (deja applique).")
            return True
        print("[ECHEC] " + chemin_relatif + " existe deja mais avec un contenu different -> abandon (rien ecrit).")
        return False

    dossier = os.path.dirname(chemin_absolu)
    if dossier and not os.path.isdir(dossier):
        os.makedirs(dossier, exist_ok=True)

    with open(chemin_absolu, "w", encoding="utf-8", newline="") as f:
        f.write(contenu_attendu)
        f.flush()
        os.fsync(f.fileno())

    with open(chemin_absolu, "r", encoding="utf-8", newline="") as f:
        relu = f.read()

    if relu != contenu_attendu:
        print("[ECHEC VERIFICATION] " + chemin_relatif + " : le contenu relu ne correspond pas.")
        return False

    print("[OK VERIFIE] " + chemin_relatif + " (fichier cree, " + str(len(contenu_attendu)) + " octets)")
    print("  Chemin reel : " + os.path.realpath(chemin_absolu))
    if chemin_relatif.endswith(".php"):
        lint_php_si_possible(chemin_absolu)
    return True


# ============================================================
# 1) src/Entity/MouvementTresorerie.php
# ============================================================

MVT_BLOC_1_ANCIEN = r"""    public const CATEGORIE_AJUSTEMENT =
        'ajustement';


    public const CATEGORIES = [
        self::CATEGORIE_VENTE,
        self::CATEGORIE_AUTRE_PRODUIT,
        self::CATEGORIE_SALAIRE,
        self::CATEGORIE_ACHAT,
        self::CATEGORIE_CARBURANT,
        self::CATEGORIE_TRANSPORT,
        self::CATEGORIE_ENTRETIEN,
        self::CATEGORIE_ELECTRICITE,
        self::CATEGORIE_LOYER,
        self::CATEGORIE_AUTRE_CHARGE,
        self::CATEGORIE_TRANSFERT_INTERNE,
        self::CATEGORIE_AJUSTEMENT,
    ];"""

MVT_BLOC_1_NOUVEAU = r"""    public const CATEGORIE_AJUSTEMENT =
        'ajustement';

    public const CATEGORIE_FRAIS_BANCAIRE =
        'frais_bancaire';

    public const CATEGORIE_REMBOURSEMENT_CREDIT =
        'remboursement_credit';


    public const CATEGORIES = [
        self::CATEGORIE_VENTE,
        self::CATEGORIE_AUTRE_PRODUIT,
        self::CATEGORIE_SALAIRE,
        self::CATEGORIE_ACHAT,
        self::CATEGORIE_CARBURANT,
        self::CATEGORIE_TRANSPORT,
        self::CATEGORIE_ENTRETIEN,
        self::CATEGORIE_ELECTRICITE,
        self::CATEGORIE_LOYER,
        self::CATEGORIE_AUTRE_CHARGE,
        self::CATEGORIE_TRANSFERT_INTERNE,
        self::CATEGORIE_AJUSTEMENT,
        self::CATEGORIE_FRAIS_BANCAIRE,
        self::CATEGORIE_REMBOURSEMENT_CREDIT,
    ];"""

MVT_BLOC_2_ANCIEN = r"""        self::CATEGORIE_AJUSTEMENT =>
            'Ajustement de trésorerie',
    ];"""

MVT_BLOC_2_NOUVEAU = r"""        self::CATEGORIE_AJUSTEMENT =>
            'Ajustement de trésorerie',

        self::CATEGORIE_FRAIS_BANCAIRE =>
            'Frais bancaires',

        self::CATEGORIE_REMBOURSEMENT_CREDIT =>
            'Remboursement de crédit',
    ];"""

MVT_BLOC_3_ANCIEN = r"""    public static function getCategoriesCharges(): array
    {
        return [
            self::CATEGORIE_SALAIRE,
            self::CATEGORIE_ACHAT,
            self::CATEGORIE_CARBURANT,
            self::CATEGORIE_TRANSPORT,
            self::CATEGORIE_ENTRETIEN,
            self::CATEGORIE_ELECTRICITE,
            self::CATEGORIE_LOYER,
            self::CATEGORIE_AUTRE_CHARGE,
        ];
    }"""

MVT_BLOC_3_NOUVEAU = r"""    public static function getCategoriesCharges(): array
    {
        return [
            self::CATEGORIE_SALAIRE,
            self::CATEGORIE_ACHAT,
            self::CATEGORIE_CARBURANT,
            self::CATEGORIE_TRANSPORT,
            self::CATEGORIE_ENTRETIEN,
            self::CATEGORIE_ELECTRICITE,
            self::CATEGORIE_LOYER,
            self::CATEGORIE_AUTRE_CHARGE,
            self::CATEGORIE_FRAIS_BANCAIRE,
            self::CATEGORIE_REMBOURSEMENT_CREDIT,
        ];
    }

    /**
     * Catégories pertinentes pour un décaissement récurrent
     * (frais bancaires, remboursement de crédit, ou toute autre
     * charge fixe qui revient chaque mois ou chaque année).
     *
     * @return array<int, string>
     */
    public static function getCategoriesDecaissementRecurrent(): array
    {
        return [
            self::CATEGORIE_FRAIS_BANCAIRE,
            self::CATEGORIE_REMBOURSEMENT_CREDIT,
            self::CATEGORIE_LOYER,
            self::CATEGORIE_AUTRE_CHARGE,
        ];
    }"""

MVT_MARQUEUR = "getCategoriesDecaissementRecurrent"


# ============================================================
# 2) templates/base.html.twig
# ============================================================

BASE_BLOC_ANCIEN = 'Mouvements de trésorerie\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t</a>\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t{% endif %}\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t{% endif %}'

BASE_BLOC_NOUVEAU = 'Mouvements de trésorerie\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t</a>\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t{% endif %}\n\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t{% if peutVoirComptesTresorerie %}\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t<a href="{{ path( \'app_decaissement_recurrent_index\' ) }}" class="\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tslide-item\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t{{\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\trouteCourante\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tstarts with\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\'app_decaissement_recurrent_\'\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t? \'active\'\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t: \'\'\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t}}\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t">\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t<i class="\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tfa\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tfa-refresh\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tmr-2\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t"></i>\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tDécaissements automatiques\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t</a>\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t{% endif %}\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t{% endif %}'


BASE_MARQUEUR = "app_decaissement_recurrent_index"


def main():
    racine = sys.argv[1] if len(sys.argv) >= 2 else "."
    verifier_racine(racine)

    if not PHP_LINT_DISPONIBLE:
        print("(info : commande 'php' introuvable ici, le controle 'php -l' sera saute)")
        print()

    resultats = []

    print("-" * 70)
    print("1) src/Entity/MouvementTresorerie.php")
    print("-" * 70)
    resultats.append(appliquer_blocs_verifie(
        racine,
        "src/Entity/MouvementTresorerie.php",
        MVT_MARQUEUR,
        [
            (MVT_BLOC_1_ANCIEN, MVT_BLOC_1_NOUVEAU),
            (MVT_BLOC_2_ANCIEN, MVT_BLOC_2_NOUVEAU),
            (MVT_BLOC_3_ANCIEN, MVT_BLOC_3_NOUVEAU),
        ]
    ))
    print()

    print("-" * 70)
    print("2) templates/base.html.twig")
    print("-" * 70)
    resultats.append(appliquer_blocs_verifie(
        racine,
        "templates/base.html.twig",
        BASE_MARQUEUR,
        [
            (BASE_BLOC_ANCIEN, BASE_BLOC_NOUVEAU),
        ]
    ))
    print()

    nouveaux_fichiers = [
        ("src/Entity/DecaissementRecurrent.php", DECAISSEMENT_RECURRENT_ENTITY_PHP),
        ("src/Repository/DecaissementRecurrentRepository.php", DECAISSEMENT_RECURRENT_REPOSITORY_PHP),
        ("src/Service/DecaissementRecurrentService.php", DECAISSEMENT_RECURRENT_SERVICE_PHP),
        ("src/Command/ExecuterDecaissementsRecurrentsCommand.php", EXECUTER_DECAISSEMENTS_COMMAND_PHP),
        ("src/Controller/DecaissementRecurrentController.php", DECAISSEMENT_RECURRENT_CONTROLLER_PHP),
        ("src/Form/DecaissementRecurrentType.php", DECAISSEMENT_RECURRENT_TYPE_PHP),
        ("templates/decaissement_recurrent/_form.html.twig", DECAISSEMENT_RECURRENT_FORM_TWIG),
        ("templates/decaissement_recurrent/new.html.twig", DECAISSEMENT_RECURRENT_NEW_TWIG),
        ("templates/decaissement_recurrent/edit.html.twig", DECAISSEMENT_RECURRENT_EDIT_TWIG),
        ("templates/decaissement_recurrent/index.html.twig", DECAISSEMENT_RECURRENT_INDEX_TWIG),
        ("migrations/Version20260825090000.php", MIGRATION_PHP),
        ("scripts/windows/decaissements_recurrents.bat", DECAISSEMENTS_BAT),
        ("scripts/windows/installer_tache_decaissements_recurrents.bat", INSTALLER_TACHE_BAT),
    ]

    for idx, (chemin_relatif, contenu) in enumerate(nouveaux_fichiers, start=3):
        print("-" * 70)
        print(str(idx) + ") " + chemin_relatif + " (nouveau fichier)")
        print("-" * 70)
        resultats.append(creer_fichier_verifie(racine, chemin_relatif, contenu))
        print()

    print("=" * 70)
    print("RESUME")
    print("=" * 70)

    if all(resultats):
        print("Tout est en place. Lancez maintenant, dans l'ordre :")
        print()
        print("  1) php bin/console doctrine:migrations:migrate")
        print("     (cree la nouvelle table decaissement_recurrent -")
        print("      repondez 'yes' si demande)")
        print()
        print("  2) php bin/console cache:clear")
        print()
        print("  3) Dans le menu, sous Tresorerie, ouvrez 'Decaissements")
        print("     automatiques' et ajoutez vos charges (frais bancaires,")
        print("     credit...) avec leur frequence et leur montant.")
        print()
        print("  4) IMPORTANT - sans cette derniere etape, rien ne se")
        print("     declenche automatiquement : faites un clic droit sur")
        print("     scripts\\windows\\installer_tache_decaissements_recurrents.bat")
        print("     et choisissez 'Executer en tant qu'administrateur'.")
        print("     Cela installe une tache planifiee Windows qui verifie")
        print("     chaque jour a 06h00 si une charge arrive a echeance.")
        print()
        print("Vous pouvez tester tout de suite sans attendre le lendemain :")
        print("  schtasks /run /tn \"SuccessImprim_DecaissementsRecurrents\"")
    else:
        print("Au moins un fichier n'a pas pu etre modifie (voir [ECHEC] ci-dessus).")
        print("Recopiez-moi TOUT ce resume, je corrige avant de vous renvoyer le script.")


DECAISSEMENT_RECURRENT_ENTITY_PHP = "<?php\n\nnamespace App\\Entity;\n\nuse App\\Repository\\DecaissementRecurrentRepository;\nuse Doctrine\\DBAL\\Types\\Types;\nuse Doctrine\\ORM\\Mapping as ORM;\nuse Symfony\\Component\\Validator\\Constraints as Assert;\nuse Symfony\\Component\\Validator\\Context\\ExecutionContextInterface;\n\n/**\n * Charge fixe qui doit être décaissée automatiquement, chaque mois ou\n * chaque année, sans ressaisie manuelle : frais bancaires, remboursement\n * d'un crédit, loyer... La commande app:executer-decaissements-recurrents\n * (lancée par une tâche planifiée) crée le MouvementTresorerie dès que\n * prochaineDateExecution est atteinte.\n */\n#[ORM\\Entity(repositoryClass: DecaissementRecurrentRepository::class)]\n#[ORM\\Table(name: 'decaissement_recurrent')]\nclass DecaissementRecurrent\n{\n    public const FREQUENCE_MENSUELLE = 'mensuelle';\n    public const FREQUENCE_ANNUELLE = 'annuelle';\n\n    public const FREQUENCES = [\n        self::FREQUENCE_MENSUELLE,\n        self::FREQUENCE_ANNUELLE,\n    ];\n\n    public const FREQUENCES_LABELS = [\n        self::FREQUENCE_MENSUELLE => 'Tous les mois',\n        self::FREQUENCE_ANNUELLE => 'Tous les ans',\n    ];\n\n    #[ORM\\Id]\n    #[ORM\\GeneratedValue]\n    #[ORM\\Column]\n    private ?int $id = null;\n\n    #[ORM\\Column(length: 255)]\n    #[Assert\\NotBlank(message: 'Le libellé est obligatoire.')]\n    private string $libelle = '';\n\n    #[ORM\\ManyToOne(targetEntity: CompteTresorerie::class)]\n    #[ORM\\JoinColumn(nullable: false, onDelete: 'RESTRICT')]\n    #[Assert\\NotNull(message: 'Le compte à débiter est obligatoire.')]\n    private ?CompteTresorerie $compteSource = null;\n\n    #[ORM\\Column(length: 30)]\n    #[Assert\\Choice(\n        callback: [MouvementTresorerie::class, 'getCategoriesDisponibles'],\n        message: 'La catégorie sélectionnée est invalide.'\n    )]\n    private string $categorie = MouvementTresorerie::CATEGORIE_AUTRE_CHARGE;\n\n    #[ORM\\Column]\n    #[Assert\\Positive(message: 'Le montant doit être supérieur à zéro.')]\n    private int $montant = 0;\n\n    #[ORM\\Column(length: 20)]\n    #[Assert\\Choice(choices: self::FREQUENCES, message: 'La fréquence sélectionnée est invalide.')]\n    private string $frequence = self::FREQUENCE_MENSUELLE;\n\n    #[ORM\\Column]\n    #[Assert\\Range(min: 1, max: 28, notInRangeMessage: 'Le jour du mois doit être compris entre 1 et 28 (pour rester valable tous les mois).')]\n    private int $jourDuMois = 1;\n\n    #[ORM\\Column(nullable: true)]\n    private ?int $moisDeLAnnee = null;\n\n    #[ORM\\Column]\n    private bool $actif = true;\n\n    #[ORM\\Column(type: Types::DATE_IMMUTABLE)]\n    #[Assert\\NotNull(message: 'La date de début est obligatoire.')]\n    private ?\\DateTimeImmutable $dateDebut = null;\n\n    #[ORM\\Column(type: Types::DATE_IMMUTABLE)]\n    private ?\\DateTimeImmutable $prochaineDateExecution = null;\n\n    #[ORM\\Column(type: Types::DATE_IMMUTABLE, nullable: true)]\n    private ?\\DateTimeImmutable $derniereDateExecution = null;\n\n    #[ORM\\ManyToOne(targetEntity: User::class)]\n    #[ORM\\JoinColumn(nullable: true, onDelete: 'SET NULL')]\n    private ?User $creePar = null;\n\n    #[ORM\\Column(type: Types::DATETIME_IMMUTABLE)]\n    private ?\\DateTimeImmutable $dateCreation = null;\n\n    #[ORM\\Column(type: Types::TEXT, nullable: true)]\n    private ?string $notes = null;\n\n    #[ORM\\PrePersist]\n    public function initialiser(): void\n    {\n        if ($this->dateCreation === null) {\n            $this->dateCreation = new \\DateTimeImmutable();\n        }\n\n        if ($this->prochaineDateExecution === null && $this->dateDebut !== null) {\n            $this->prochaineDateExecution = $this->calculerPremiereDateExecution($this->dateDebut);\n        }\n    }\n\n    #[Assert\\Callback]\n    public function validerMoisAnnuel(ExecutionContextInterface $context): void\n    {\n        if ($this->frequence !== self::FREQUENCE_ANNUELLE) {\n            return;\n        }\n\n        if ($this->moisDeLAnnee === null || $this->moisDeLAnnee < 1 || $this->moisDeLAnnee > 12) {\n            $context->buildViolation('Le mois est obligatoire pour une charge annuelle.')\n                ->atPath('moisDeLAnnee')\n                ->addViolation();\n        }\n    }\n\n    /**\n     * Première échéance à partir d'une date donnée (utilisée à la\n     * création, quand aucune échéance n'a encore été calculée).\n     */\n    public function calculerPremiereDateExecution(\\DateTimeImmutable $depuis): \\DateTimeImmutable\n    {\n        $annee = (int) $depuis->format('Y');\n        $mois = $this->frequence === self::FREQUENCE_ANNUELLE\n            ? (int) ($this->moisDeLAnnee ?? 1)\n            : (int) $depuis->format('n');\n\n        $candidate = new \\DateTimeImmutable(sprintf('%04d-%02d-%02d', $annee, $mois, $this->jourDuMois));\n\n        if ($candidate < $depuis) {\n            $candidate = $this->avancerDate($candidate);\n        }\n\n        return $candidate;\n    }\n\n    private function avancerDate(\\DateTimeImmutable $date): \\DateTimeImmutable\n    {\n        return $this->frequence === self::FREQUENCE_ANNUELLE\n            ? $date->modify('+1 year')\n            : $date->modify('+1 month');\n    }\n\n    public function estDue(\\DateTimeImmutable $reference): bool\n    {\n        return $this->actif\n            && $this->prochaineDateExecution !== null\n            && $this->prochaineDateExecution <= $reference;\n    }\n\n    /**\n     * Appelée après avoir effectivement créé le décaissement pour\n     * l'échéance en cours : avance à l'échéance suivante.\n     */\n    public function marquerExecutee(\\DateTimeImmutable $dateExecution): static\n    {\n        $this->derniereDateExecution = $dateExecution;\n        $this->prochaineDateExecution = $this->avancerDate(\n            $this->prochaineDateExecution ?? $dateExecution\n        );\n\n        return $this;\n    }\n\n    public function getId(): ?int\n    {\n        return $this->id;\n    }\n\n    public function getLibelle(): string\n    {\n        return $this->libelle;\n    }\n\n    public function setLibelle(string $libelle): static\n    {\n        $this->libelle = trim($libelle);\n\n        return $this;\n    }\n\n    public function getCompteSource(): ?CompteTresorerie\n    {\n        return $this->compteSource;\n    }\n\n    public function setCompteSource(?CompteTresorerie $compteSource): static\n    {\n        $this->compteSource = $compteSource;\n\n        return $this;\n    }\n\n    public function getCategorie(): string\n    {\n        return $this->categorie;\n    }\n\n    public function setCategorie(string $categorie): static\n    {\n        $this->categorie = $categorie;\n\n        return $this;\n    }\n\n    public function getMontant(): int\n    {\n        return $this->montant;\n    }\n\n    public function setMontant(int $montant): static\n    {\n        $this->montant = $montant;\n\n        return $this;\n    }\n\n    public function getFrequence(): string\n    {\n        return $this->frequence;\n    }\n\n    public function setFrequence(string $frequence): static\n    {\n        $this->frequence = $frequence;\n\n        return $this;\n    }\n\n    public function getJourDuMois(): int\n    {\n        return $this->jourDuMois;\n    }\n\n    public function setJourDuMois(int $jourDuMois): static\n    {\n        $this->jourDuMois = $jourDuMois;\n\n        return $this;\n    }\n\n    public function getMoisDeLAnnee(): ?int\n    {\n        return $this->moisDeLAnnee;\n    }\n\n    public function setMoisDeLAnnee(?int $moisDeLAnnee): static\n    {\n        $this->moisDeLAnnee = $this->frequence === self::FREQUENCE_ANNUELLE\n            ? $moisDeLAnnee\n            : null;\n\n        return $this;\n    }\n\n    public function isActif(): bool\n    {\n        return $this->actif;\n    }\n\n    public function setActif(bool $actif): static\n    {\n        $this->actif = $actif;\n\n        return $this;\n    }\n\n    public function getDateDebut(): ?\\DateTimeImmutable\n    {\n        return $this->dateDebut;\n    }\n\n    public function setDateDebut(?\\DateTimeImmutable $dateDebut): static\n    {\n        $this->dateDebut = $dateDebut;\n\n        return $this;\n    }\n\n    public function getProchaineDateExecution(): ?\\DateTimeImmutable\n    {\n        return $this->prochaineDateExecution;\n    }\n\n    public function setProchaineDateExecution(?\\DateTimeImmutable $prochaineDateExecution): static\n    {\n        $this->prochaineDateExecution = $prochaineDateExecution;\n\n        return $this;\n    }\n\n    public function getDerniereDateExecution(): ?\\DateTimeImmutable\n    {\n        return $this->derniereDateExecution;\n    }\n\n    public function getCreePar(): ?User\n    {\n        return $this->creePar;\n    }\n\n    public function setCreePar(?User $creePar): static\n    {\n        $this->creePar = $creePar;\n\n        return $this;\n    }\n\n    public function getDateCreation(): ?\\DateTimeImmutable\n    {\n        return $this->dateCreation;\n    }\n\n    public function getNotes(): ?string\n    {\n        return $this->notes;\n    }\n\n    public function setNotes(?string $notes): static\n    {\n        $this->notes = $notes !== null && trim($notes) !== '' ? trim($notes) : null;\n\n        return $this;\n    }\n}\n"

DECAISSEMENT_RECURRENT_REPOSITORY_PHP = "<?php\n\nnamespace App\\Repository;\n\nuse App\\Entity\\DecaissementRecurrent;\nuse Doctrine\\Bundle\\DoctrineBundle\\Repository\\ServiceEntityRepository;\nuse Doctrine\\Persistence\\ManagerRegistry;\n\n/**\n * @extends ServiceEntityRepository<DecaissementRecurrent>\n */\nclass DecaissementRecurrentRepository extends ServiceEntityRepository\n{\n    public function __construct(ManagerRegistry $registry)\n    {\n        parent::__construct($registry, DecaissementRecurrent::class);\n    }\n\n    /**\n     * Charges actives dont l'échéance est atteinte (ou dépassée).\n     *\n     * @return array<int, DecaissementRecurrent>\n     */\n    public function findActifsDus(\\DateTimeImmutable $reference): array\n    {\n        return $this->createQueryBuilder('charge')\n            ->andWhere('charge.actif = :actif')\n            ->andWhere('charge.prochaineDateExecution <= :reference')\n            ->setParameter('actif', true)\n            ->setParameter('reference', $reference)\n            ->orderBy('charge.prochaineDateExecution', 'ASC')\n            ->getQuery()\n            ->getResult();\n    }\n\n    /**\n     * @return array<int, DecaissementRecurrent>\n     */\n    public function findToutes(): array\n    {\n        return $this->createQueryBuilder('charge')\n            ->leftJoin('charge.compteSource', 'compte')\n            ->addSelect('compte')\n            ->orderBy('charge.actif', 'DESC')\n            ->addOrderBy('charge.prochaineDateExecution', 'ASC')\n            ->getQuery()\n            ->getResult();\n    }\n}\n"

DECAISSEMENT_RECURRENT_SERVICE_PHP = '<?php\n\nnamespace App\\Service;\n\nuse App\\Entity\\DecaissementRecurrent;\nuse App\\Entity\\MouvementTresorerie;\nuse App\\Repository\\DecaissementRecurrentRepository;\nuse Doctrine\\ORM\\EntityManagerInterface;\n\n/**\n * Génère automatiquement les MouvementTresorerie des charges\n * récurrentes (frais bancaires, remboursement de crédit...) dont\n * l\'échéance est atteinte. Appelée par la commande\n * app:executer-decaissements-recurrents (tâche planifiée).\n */\nclass DecaissementRecurrentService\n{\n    /**\n     * Si une charge n\'a pas pu tourner depuis longtemps (poste\n     * éteint plusieurs mois, tâche planifiée non installée...), on\n     * rattrape les échéances manquées une par une, mais jamais plus\n     * que ça d\'un coup : au-delà, mieux vaut que l\'utilisateur\n     * vérifie la charge lui-même plutôt que de débiter le compte\n     * en boucle sans surveillance.\n     */\n    private const MAX_RATTRAPAGE_PAR_CHARGE = 24;\n\n    public function __construct(\n        private readonly DecaissementRecurrentRepository $decaissementRecurrentRepository,\n        private readonly MouvementTresorerieService $mouvementTresorerieService,\n        private readonly NotificationService $notificationService,\n        private readonly EntityManagerInterface $entityManager\n    ) {\n    }\n\n    /**\n     * @return array{executes: int, echecs: int, details: string[]}\n     */\n    public function executerDecaissementsDus(?\\DateTimeImmutable $reference = null): array\n    {\n        $reference = $reference ?? new \\DateTimeImmutable(\'today\');\n\n        $charges = $this->decaissementRecurrentRepository->findActifsDus($reference);\n\n        $executes = 0;\n        $echecs = 0;\n        $details = [];\n\n        foreach ($charges as $charge) {\n            $iterations = 0;\n\n            while ($charge->estDue($reference) && $iterations < self::MAX_RATTRAPAGE_PAR_CHARGE) {\n                $iterations++;\n\n                $resultat = $this->executerUneEcheance($charge, $reference);\n\n                $details[] = $resultat[\'message\'];\n\n                if ($resultat[\'succes\']) {\n                    $executes++;\n                } else {\n                    $echecs++;\n\n                    /*\n                     * Un échec (compte insuffisant, compte inactif...)\n                     * n\'a pas fait avancer l\'échéance : inutile de\n                     * retenter la même charge dans cette exécution,\n                     * elle échouera de la même façon. On passe à la\n                     * charge suivante et on réessaiera au prochain\n                     * passage de la tâche planifiée.\n                     */\n                    break;\n                }\n            }\n        }\n\n        return [\n            \'executes\' => $executes,\n            \'echecs\' => $echecs,\n            \'details\' => $details,\n        ];\n    }\n\n    /**\n     * @return array{succes: bool, message: string}\n     */\n    private function executerUneEcheance(\n        DecaissementRecurrent $charge,\n        \\DateTimeImmutable $reference\n    ): array {\n        $compte = $charge->getCompteSource();\n\n        try {\n            $mouvement = new MouvementTresorerie();\n            $mouvement\n                ->setType(MouvementTresorerie::TYPE_DECAISSEMENT)\n                ->setCategorie($charge->getCategorie())\n                ->setCompteSource($compte)\n                ->setMontant($charge->getMontant())\n                ->setLibelle(sprintf(\n                    \'%s (décaissement automatique %s)\',\n                    $charge->getLibelle(),\n                    $charge->getFrequence() === DecaissementRecurrent::FREQUENCE_ANNUELLE\n                        ? \'annuel\'\n                        : \'mensuel\'\n                ));\n\n            $this->mouvementTresorerieService->enregistrer($mouvement);\n\n            $charge->marquerExecutee($reference);\n\n            $this->notificationService->notifierRoles(\n                [\'ROLE_ADMIN\'],\n                sprintf(\n                    \'Décaissement automatique : « %s » — %d %s sur %s.\',\n                    $charge->getLibelle(),\n                    $charge->getMontant(),\n                    $mouvement->getDevise(),\n                    $compte?->getNom() ?? \'compte inconnu\'\n                ),\n                \'app_mouvement_tresorerie_show\',\n                [\'id\' => $mouvement->getId()]\n            );\n\n            $this->entityManager->flush();\n\n            return [\n                \'succes\' => true,\n                \'message\' => sprintf(\n                    \'[OK] %s : %d %s débités de "%s" (mouvement %s).\',\n                    $charge->getLibelle(),\n                    $charge->getMontant(),\n                    $mouvement->getDevise(),\n                    $compte?->getNom() ?? \'?\',\n                    $mouvement->getReference()\n                ),\n            ];\n        } catch (\\Throwable $exception) {\n            $this->notificationService->notifierRoles(\n                [\'ROLE_ADMIN\'],\n                sprintf(\n                    \'Échec du décaissement automatique « %s » (%s) : %s\',\n                    $charge->getLibelle(),\n                    $compte?->getNom() ?? \'compte inconnu\',\n                    $exception->getMessage()\n                ),\n                \'app_decaissement_recurrent_index\'\n            );\n\n            $this->entityManager->flush();\n\n            return [\n                \'succes\' => false,\n                \'message\' => sprintf(\n                    \'[ECHEC] %s : %s\',\n                    $charge->getLibelle(),\n                    $exception->getMessage()\n                ),\n            ];\n        }\n    }\n}\n'

EXECUTER_DECAISSEMENTS_COMMAND_PHP = "<?php\n\nnamespace App\\Command;\n\nuse App\\Service\\DecaissementRecurrentService;\nuse Symfony\\Component\\Console\\Attribute\\AsCommand;\nuse Symfony\\Component\\Console\\Command\\Command;\nuse Symfony\\Component\\Console\\Input\\InputInterface;\nuse Symfony\\Component\\Console\\Output\\OutputInterface;\n\n#[AsCommand(\n    name: 'app:executer-decaissements-recurrents',\n    description: 'Crée les décaissements automatiques (frais bancaires, crédits...) arrivés à échéance.'\n)]\nfinal class ExecuterDecaissementsRecurrentsCommand extends Command\n{\n    public function __construct(\n        private readonly DecaissementRecurrentService $decaissementRecurrentService\n    ) {\n        parent::__construct();\n    }\n\n    protected function execute(\n        InputInterface $input,\n        OutputInterface $output\n    ): int {\n        $resultat = $this->decaissementRecurrentService->executerDecaissementsDus();\n\n        foreach ($resultat['details'] as $ligne) {\n            $output->writeln($ligne);\n        }\n\n        $output->writeln(\n            sprintf(\n                '<info>%d décaissement(s) exécuté(s).</info>',\n                $resultat['executes']\n            )\n        );\n\n        if ($resultat['echecs'] > 0) {\n            $output->writeln(\n                sprintf(\n                    '<comment>%d échec(s) — voir la cloche de notifications (admin).</comment>',\n                    $resultat['echecs']\n                )\n            );\n        }\n\n        return Command::SUCCESS;\n    }\n}\n"

DECAISSEMENT_RECURRENT_CONTROLLER_PHP = "<?php\n\nnamespace App\\Controller;\n\nuse App\\Entity\\DecaissementRecurrent;\nuse App\\Entity\\MouvementTresorerie;\nuse App\\Entity\\User;\nuse App\\Form\\DecaissementRecurrentType;\nuse App\\Repository\\DecaissementRecurrentRepository;\nuse Doctrine\\ORM\\EntityManagerInterface;\nuse Symfony\\Bundle\\FrameworkBundle\\Controller\\AbstractController;\nuse Symfony\\Component\\HttpFoundation\\Request;\nuse Symfony\\Component\\HttpFoundation\\Response;\nuse Symfony\\Component\\Routing\\Attribute\\Route;\nuse Symfony\\Component\\Security\\Http\\Attribute\\IsGranted;\n\n/**\n * Configuration des charges fixes décaissées automatiquement (frais\n * bancaires, remboursement de crédit...). La génération réelle des\n * mouvements se fait via DecaissementRecurrentService, appelé par la\n * commande app:executer-decaissements-recurrents (tâche planifiée) —\n * cet écran ne fait que définir QUOI et QUAND.\n */\n#[Route('/decaissements-recurrents', name: 'app_decaissement_recurrent_')]\n#[IsGranted('ROLE_ADMIN')]\nfinal class DecaissementRecurrentController extends AbstractController\n{\n    #[Route('', name: 'index', methods: ['GET'])]\n    public function index(\n        DecaissementRecurrentRepository $decaissementRecurrentRepository\n    ): Response {\n        return $this->render('decaissement_recurrent/index.html.twig', [\n            'charges' => $decaissementRecurrentRepository->findToutes(),\n            'categoriesLabels' => MouvementTresorerie::CATEGORIES_LABELS,\n        ]);\n    }\n\n    #[Route('/new', name: 'new', methods: ['GET', 'POST'])]\n    public function new(\n        Request $request,\n        EntityManagerInterface $entityManager\n    ): Response {\n        $charge = new DecaissementRecurrent();\n        $charge->setDateDebut(new \\DateTimeImmutable('today'));\n\n        $form = $this->createForm(DecaissementRecurrentType::class, $charge);\n        $form->handleRequest($request);\n\n        if ($form->isSubmitted() && $form->isValid()) {\n            $charge->setCreePar($this->utilisateurConnecte());\n\n            $entityManager->persist($charge);\n            $entityManager->flush();\n\n            $this->addFlash(\n                'success',\n                sprintf(\n                    'La charge « %s » a été créée. Prochaine échéance : %s.',\n                    $charge->getLibelle(),\n                    $charge->getProchaineDateExecution()?->format('d/m/Y')\n                )\n            );\n\n            return $this->redirectToRoute(\n                'app_decaissement_recurrent_index',\n                [],\n                Response::HTTP_SEE_OTHER\n            );\n        }\n\n        return $this->render('decaissement_recurrent/new.html.twig', [\n            'form' => $form,\n        ]);\n    }\n\n    #[Route('/{id}/edit', name: 'edit', requirements: ['id' => '\\d+'], methods: ['GET', 'POST'])]\n    public function edit(\n        Request $request,\n        DecaissementRecurrent $charge,\n        EntityManagerInterface $entityManager\n    ): Response {\n        $ancienneFrequence = $charge->getFrequence();\n        $ancienJour = $charge->getJourDuMois();\n        $ancienMois = $charge->getMoisDeLAnnee();\n\n        $form = $this->createForm(DecaissementRecurrentType::class, $charge);\n        $form->handleRequest($request);\n\n        if ($form->isSubmitted() && $form->isValid()) {\n            /*\n             * Si l'échéancier (fréquence/jour/mois) a changé, la\n             * prochaine date calculée à la création n'est plus\n             * valable : on la recalcule à partir d'aujourd'hui pour\n             * ne pas déclencher un rattrapage inattendu.\n             */\n            if (\n                $charge->getFrequence() !== $ancienneFrequence\n                || $charge->getJourDuMois() !== $ancienJour\n                || $charge->getMoisDeLAnnee() !== $ancienMois\n            ) {\n                $charge->setProchaineDateExecution(\n                    $charge->calculerPremiereDateExecution(new \\DateTimeImmutable('today'))\n                );\n            }\n\n            $entityManager->flush();\n\n            $this->addFlash('success', 'La charge a été modifiée.');\n\n            return $this->redirectToRoute(\n                'app_decaissement_recurrent_index',\n                [],\n                Response::HTTP_SEE_OTHER\n            );\n        }\n\n        return $this->render('decaissement_recurrent/edit.html.twig', [\n            'charge' => $charge,\n            'form' => $form,\n        ]);\n    }\n\n    #[Route('/{id}/toggle-actif', name: 'toggle_actif', requirements: ['id' => '\\d+'], methods: ['POST'])]\n    public function toggleActif(\n        Request $request,\n        DecaissementRecurrent $charge,\n        EntityManagerInterface $entityManager\n    ): Response {\n        if ($this->isCsrfTokenValid(\n            'toggle_actif' . $charge->getId(),\n            $request->getPayload()->getString('_token')\n        )) {\n            $charge->setActif(!$charge->isActif());\n            $entityManager->flush();\n\n            $this->addFlash(\n                'success',\n                $charge->isActif()\n                    ? 'La charge a été réactivée.'\n                    : 'La charge a été suspendue.'\n            );\n        }\n\n        return $this->redirectToRoute(\n            'app_decaissement_recurrent_index',\n            [],\n            Response::HTTP_SEE_OTHER\n        );\n    }\n\n    #[Route('/{id}/delete', name: 'delete', requirements: ['id' => '\\d+'], methods: ['POST'])]\n    public function delete(\n        Request $request,\n        DecaissementRecurrent $charge,\n        EntityManagerInterface $entityManager\n    ): Response {\n        if ($this->isCsrfTokenValid(\n            'delete' . $charge->getId(),\n            $request->getPayload()->getString('_token')\n        )) {\n            $entityManager->remove($charge);\n            $entityManager->flush();\n\n            $this->addFlash('success', 'La charge récurrente a été supprimée.');\n        }\n\n        return $this->redirectToRoute(\n            'app_decaissement_recurrent_index',\n            [],\n            Response::HTTP_SEE_OTHER\n        );\n    }\n\n    private function utilisateurConnecte(): User\n    {\n        $user = $this->getUser();\n\n        if (!$user instanceof User) {\n            throw $this->createAccessDeniedException('Utilisateur non authentifié.');\n        }\n\n        return $user;\n    }\n}\n"

DECAISSEMENT_RECURRENT_TYPE_PHP = "<?php\n\nnamespace App\\Form;\n\nuse App\\Entity\\CompteTresorerie;\nuse App\\Entity\\DecaissementRecurrent;\nuse App\\Entity\\MouvementTresorerie;\nuse App\\Repository\\CompteTresorerieRepository;\nuse Doctrine\\ORM\\QueryBuilder;\nuse Symfony\\Bridge\\Doctrine\\Form\\Type\\EntityType;\nuse Symfony\\Component\\Form\\AbstractType;\nuse Symfony\\Component\\Form\\Extension\\Core\\Type\\CheckboxType;\nuse Symfony\\Component\\Form\\Extension\\Core\\Type\\ChoiceType;\nuse Symfony\\Component\\Form\\Extension\\Core\\Type\\DateType;\nuse Symfony\\Component\\Form\\Extension\\Core\\Type\\IntegerType;\nuse Symfony\\Component\\Form\\Extension\\Core\\Type\\TextareaType;\nuse Symfony\\Component\\Form\\Extension\\Core\\Type\\TextType;\nuse Symfony\\Component\\Form\\FormBuilderInterface;\nuse Symfony\\Component\\OptionsResolver\\OptionsResolver;\nuse Symfony\\Component\\Validator\\Constraints\\NotBlank;\n\nfinal class DecaissementRecurrentType extends AbstractType\n{\n    public function buildForm(\n        FormBuilderInterface $builder,\n        array $options\n    ): void {\n        $builder\n            ->add('libelle', TextType::class, [\n                'label' => 'Libellé',\n                'attr' => [\n                    'class' => 'form-control',\n                    'placeholder' => 'Ex : Frais de tenue de compte, Échéance crédit matériel...',\n                ],\n                'constraints' => [\n                    new NotBlank(message: 'Le libellé est obligatoire.'),\n                ],\n            ])\n\n            ->add('compteSource', EntityType::class, [\n                'label' => 'Compte à débiter',\n                'class' => CompteTresorerie::class,\n                'query_builder' => static function (\n                    CompteTresorerieRepository $repository\n                ): QueryBuilder {\n                    return $repository->createQueryBuilder('compte')\n                        ->andWhere('compte.actif = :actif')\n                        ->setParameter('actif', true)\n                        ->orderBy('compte.nom', 'ASC');\n                },\n                'choice_label' => static fn (CompteTresorerie $compte): string => (string) $compte,\n                'placeholder' => 'Sélectionnez un compte...',\n                'attr' => ['class' => 'form-control'],\n            ])\n\n            ->add('categorie', ChoiceType::class, [\n                'label' => 'Catégorie',\n                'choices' => array_flip(array_intersect_key(\n                    MouvementTresorerie::CATEGORIES_LABELS,\n                    array_flip(MouvementTresorerie::getCategoriesDecaissementRecurrent())\n                )),\n                'attr' => ['class' => 'form-control'],\n            ])\n\n            ->add('montant', IntegerType::class, [\n                'label' => 'Montant (FCFA)',\n                'attr' => [\n                    'class' => 'form-control',\n                    'min' => 1,\n                    'placeholder' => 'Exemple : 15000',\n                ],\n            ])\n\n            ->add('frequence', ChoiceType::class, [\n                'label' => 'Fréquence',\n                'choices' => array_flip(DecaissementRecurrent::FREQUENCES_LABELS),\n                'expanded' => true,\n                'attr' => ['class' => 'form-control'],\n            ])\n\n            ->add('jourDuMois', IntegerType::class, [\n                'label' => 'Jour du mois',\n                'help' => 'Entre 1 et 28, pour rester valable tous les mois (y compris février).',\n                'attr' => [\n                    'class' => 'form-control',\n                    'min' => 1,\n                    'max' => 28,\n                ],\n            ])\n\n            ->add('moisDeLAnnee', ChoiceType::class, [\n                'label' => 'Mois (si fréquence annuelle)',\n                'required' => false,\n                'placeholder' => '—',\n                'choices' => [\n                    'Janvier' => 1, 'Février' => 2, 'Mars' => 3, 'Avril' => 4,\n                    'Mai' => 5, 'Juin' => 6, 'Juillet' => 7, 'Août' => 8,\n                    'Septembre' => 9, 'Octobre' => 10, 'Novembre' => 11, 'Décembre' => 12,\n                ],\n                'attr' => ['class' => 'form-control'],\n            ])\n\n            ->add('dateDebut', DateType::class, [\n                'label' => 'À partir du',\n                'widget' => 'single_text',\n                'attr' => ['class' => 'form-control'],\n            ])\n\n            ->add('actif', CheckboxType::class, [\n                'label' => 'Charge active',\n                'required' => false,\n            ])\n\n            ->add('notes', TextareaType::class, [\n                'label' => 'Notes (facultatif)',\n                'required' => false,\n                'attr' => [\n                    'class' => 'form-control',\n                    'rows' => 2,\n                ],\n            ])\n        ;\n    }\n\n    public function configureOptions(OptionsResolver $resolver): void\n    {\n        $resolver->setDefaults([\n            'data_class' => DecaissementRecurrent::class,\n        ]);\n    }\n}\n"

DECAISSEMENT_RECURRENT_FORM_TWIG = '{{ form_start(form) }}\n\n<div class="card-body">\n\n\t<div class="row">\n\n\t\t<div class="col-md-12">\n\t\t\t<div class="form-group">\n\t\t\t\t{{ form_label(form.libelle) }}\n\t\t\t\t{{ form_widget(form.libelle) }}\n\t\t\t\t{{ form_errors(form.libelle) }}\n\t\t\t</div>\n\t\t</div>\n\n\t\t<div class="col-md-6">\n\t\t\t<div class="form-group">\n\t\t\t\t{{ form_label(form.compteSource) }}\n\t\t\t\t{{ form_widget(form.compteSource) }}\n\t\t\t\t{{ form_errors(form.compteSource) }}\n\t\t\t</div>\n\t\t</div>\n\n\t\t<div class="col-md-6">\n\t\t\t<div class="form-group">\n\t\t\t\t{{ form_label(form.categorie) }}\n\t\t\t\t{{ form_widget(form.categorie) }}\n\t\t\t\t{{ form_errors(form.categorie) }}\n\t\t\t</div>\n\t\t</div>\n\n\t\t<div class="col-md-6">\n\t\t\t<div class="form-group">\n\t\t\t\t{{ form_label(form.montant) }}\n\t\t\t\t{{ form_widget(form.montant) }}\n\t\t\t\t{{ form_errors(form.montant) }}\n\t\t\t</div>\n\t\t</div>\n\n\t\t<div class="col-md-6">\n\t\t\t<div class="form-group">\n\t\t\t\t{{ form_label(form.dateDebut) }}\n\t\t\t\t{{ form_widget(form.dateDebut) }}\n\t\t\t\t{{ form_errors(form.dateDebut) }}\n\t\t\t</div>\n\t\t</div>\n\n\t\t<div class="col-md-12">\n\t\t\t<div class="form-group">\n\t\t\t\t{{ form_label(form.frequence) }}\n\t\t\t\t<div>\n\t\t\t\t\t{{ form_widget(form.frequence) }}\n\t\t\t\t</div>\n\t\t\t\t{{ form_errors(form.frequence) }}\n\t\t\t</div>\n\t\t</div>\n\n\t\t<div class="col-md-6">\n\t\t\t<div class="form-group">\n\t\t\t\t{{ form_label(form.jourDuMois) }}\n\t\t\t\t{{ form_widget(form.jourDuMois) }}\n\t\t\t\t{% if form.jourDuMois.vars.help %}\n\t\t\t\t\t<small class="form-text text-muted">{{ form.jourDuMois.vars.help }}</small>\n\t\t\t\t{% endif %}\n\t\t\t\t{{ form_errors(form.jourDuMois) }}\n\t\t\t</div>\n\t\t</div>\n\n\t\t<div class="col-md-6">\n\t\t\t<div class="form-group">\n\t\t\t\t{{ form_label(form.moisDeLAnnee) }}\n\t\t\t\t{{ form_widget(form.moisDeLAnnee) }}\n\t\t\t\t{{ form_errors(form.moisDeLAnnee) }}\n\t\t\t</div>\n\t\t</div>\n\n\t\t<div class="col-md-6">\n\t\t\t<div class="form-group mt-4">\n\t\t\t\t<label class="custom-switch mb-0">\n\t\t\t\t\t{{ form_widget(form.actif, {attr: {class: \'custom-switch-input\'}}) }}\n\t\t\t\t\t<span class="custom-switch-indicator"></span>\n\t\t\t\t\t<span class="custom-switch-description">\n\t\t\t\t\t\tCharge active\n\t\t\t\t\t</span>\n\t\t\t\t</label>\n\t\t\t</div>\n\t\t</div>\n\n\t\t<div class="col-md-12">\n\t\t\t<div class="form-group">\n\t\t\t\t{{ form_label(form.notes) }}\n\t\t\t\t{{ form_widget(form.notes) }}\n\t\t\t\t{{ form_errors(form.notes) }}\n\t\t\t</div>\n\t\t</div>\n\n\t</div>\n\n\t{% if form.vars.errors|length > 0 %}\n\t\t<div class="alert alert-danger mt-3">\n\t\t\t{{ form_errors(form) }}\n\t\t</div>\n\t{% endif %}\n\n</div>\n\n<div class="card-footer text-right">\n\t<a href="{{ path(\'app_decaissement_recurrent_index\') }}" class="btn btn-secondary">\n\t\t<i class="fa fa-arrow-left mr-1"></i>\n\t\tRetour\n\t</a>\n\t<button type="submit" class="btn btn-primary-light">\n\t\t<i class="fa fa-save mr-1"></i>\n\t\tEnregistrer\n\t</button>\n</div>\n\n{{ form_end(form) }}\n'

DECAISSEMENT_RECURRENT_NEW_TWIG = '{% extends \'base.html.twig\' %}\n\n{% block title %}\n\tNouvelle charge récurrente\n{% endblock %}\n\n{% block body %}\n\n\t{% include "alert.html.twig" %}\n\n\t<div class="page-header">\n\t\t<ol class="breadcrumb">\n\t\t\t<li class="breadcrumb-item">\n\t\t\t\t<a href="{{ path(\'app_decaissement_recurrent_index\') }}">Décaissements automatiques</a>\n\t\t\t</li>\n\t\t\t<li class="breadcrumb-item active">\n\t\t\t\tNouvelle charge\n\t\t\t</li>\n\t\t</ol>\n\t</div>\n\n\t<div class="row">\n\t\t<div class="col-md-8">\n\t\t\t<div class="card">\n\t\t\t\t<div class="card-header">\n\t\t\t\t\t<h3 class="mb-0 card-title">\n\t\t\t\t\t\tAjouter une charge récurrente\n\t\t\t\t\t</h3>\n\t\t\t\t</div>\n\n\t\t\t\t{% include \'decaissement_recurrent/_form.html.twig\' %}\n\n\t\t\t</div>\n\t\t</div>\n\t</div>\n\n{% endblock %}\n'

DECAISSEMENT_RECURRENT_EDIT_TWIG = '{% extends \'base.html.twig\' %}\n\n{% block title %}\n\tModifier {{ charge.libelle }}\n{% endblock %}\n\n{% block body %}\n\n\t{% include "alert.html.twig" %}\n\n\t<div class="page-header">\n\t\t<ol class="breadcrumb">\n\t\t\t<li class="breadcrumb-item">\n\t\t\t\t<a href="{{ path(\'app_decaissement_recurrent_index\') }}">Décaissements automatiques</a>\n\t\t\t</li>\n\t\t\t<li class="breadcrumb-item active">\n\t\t\t\tModifier\n\t\t\t</li>\n\t\t</ol>\n\t</div>\n\n\t<div class="row">\n\t\t<div class="col-md-8">\n\t\t\t<div class="card">\n\t\t\t\t<div class="card-header">\n\t\t\t\t\t<h3 class="mb-0 card-title">\n\t\t\t\t\t\tModifier {{ charge.libelle }}\n\t\t\t\t\t</h3>\n\t\t\t\t</div>\n\n\t\t\t\t{% include \'decaissement_recurrent/_form.html.twig\' %}\n\n\t\t\t</div>\n\t\t</div>\n\t</div>\n\n{% endblock %}\n'

DECAISSEMENT_RECURRENT_INDEX_TWIG = '{% extends \'base.html.twig\' %}\n\n{% block title %}\n\tDécaissements automatiques\n{% endblock %}\n\n{% block body %}\n\n\t{% include "alert.html.twig" %}\n\n\t<div class="side-app">\n\n\t\t<div class="page-header">\n\n\t\t\t<div>\n\n\t\t\t\t<h1 class="page-title">\n\t\t\t\t\tDécaissements automatiques\n\t\t\t\t</h1>\n\n\t\t\t\t<ol class="breadcrumb">\n\t\t\t\t\t<li class="breadcrumb-item">\n\t\t\t\t\t\tTrésorerie\n\t\t\t\t\t</li>\n\t\t\t\t\t<li class="breadcrumb-item active">\n\t\t\t\t\t\tDécaissements automatiques\n\t\t\t\t\t</li>\n\t\t\t\t</ol>\n\n\t\t\t</div>\n\n\t\t\t<div class="ml-auto">\n\n\t\t\t\t<a href="{{ path(\'app_decaissement_recurrent_new\') }}" class="btn btn-primary-light">\n\t\t\t\t\t<i class="fa fa-plus mr-1"></i>\n\t\t\t\t\tNouvelle charge\n\t\t\t\t</a>\n\n\t\t\t</div>\n\n\t\t</div>\n\n\t\t<div class="row row-cards">\n\n\t\t\t<div class="col-lg-12">\n\n\t\t\t\t<div class="alert alert-info">\n\t\t\t\t\t<i class="fa fa-info-circle mr-1"></i>\n\t\t\t\t\tCes charges sont décaissées automatiquement dès que leur échéance est atteinte, par une tâche planifiée sur le serveur (voir <code>scripts/windows/installer_tache_decaissements_recurrents.bat</code>). Sans cette tâche installée, rien ne se déclenche tout seul.\n\t\t\t\t</div>\n\n\t\t\t\t<div class="card">\n\n\t\t\t\t\t<div class="card-header">\n\t\t\t\t\t\t<div>\n\t\t\t\t\t\t\t<h3 class="card-title mb-1">\n\t\t\t\t\t\t\t\tCharges récurrentes\n\t\t\t\t\t\t\t</h3>\n\t\t\t\t\t\t\t<small class="text-muted">\n\t\t\t\t\t\t\t\t{{ charges|length }} charge(s)\n\t\t\t\t\t\t\t</small>\n\t\t\t\t\t\t</div>\n\t\t\t\t\t</div>\n\n\t\t\t\t\t<div class="table-responsive">\n\n\t\t\t\t\t\t<table class="table table-bordered table-hover mb-0">\n\n\t\t\t\t\t\t\t<thead>\n\t\t\t\t\t\t\t\t<tr>\n\t\t\t\t\t\t\t\t\t<th>Libellé</th>\n\t\t\t\t\t\t\t\t\t<th>Compte</th>\n\t\t\t\t\t\t\t\t\t<th>Catégorie</th>\n\t\t\t\t\t\t\t\t\t<th class="text-right">Montant</th>\n\t\t\t\t\t\t\t\t\t<th>Fréquence</th>\n\t\t\t\t\t\t\t\t\t<th>Prochaine échéance</th>\n\t\t\t\t\t\t\t\t\t<th class="text-center">Statut</th>\n\t\t\t\t\t\t\t\t\t<th class="text-center">Actions</th>\n\t\t\t\t\t\t\t\t</tr>\n\t\t\t\t\t\t\t</thead>\n\n\t\t\t\t\t\t\t<tbody>\n\n\t\t\t\t\t\t\t\t{% for charge in charges %}\n\n\t\t\t\t\t\t\t\t\t<tr>\n\n\t\t\t\t\t\t\t\t\t\t<td class="align-middle">\n\t\t\t\t\t\t\t\t\t\t\t<strong>{{ charge.libelle }}</strong>\n\t\t\t\t\t\t\t\t\t\t\t{% if charge.notes %}\n\t\t\t\t\t\t\t\t\t\t\t\t<div class="small text-muted">{{ charge.notes }}</div>\n\t\t\t\t\t\t\t\t\t\t\t{% endif %}\n\t\t\t\t\t\t\t\t\t\t</td>\n\n\t\t\t\t\t\t\t\t\t\t<td class="align-middle">\n\t\t\t\t\t\t\t\t\t\t\t{{ charge.compteSource }}\n\t\t\t\t\t\t\t\t\t\t</td>\n\n\t\t\t\t\t\t\t\t\t\t<td class="align-middle">\n\t\t\t\t\t\t\t\t\t\t\t{{ categoriesLabels[charge.categorie]|default(charge.categorie) }}\n\t\t\t\t\t\t\t\t\t\t</td>\n\n\t\t\t\t\t\t\t\t\t\t<td class="align-middle text-right">\n\t\t\t\t\t\t\t\t\t\t\t{{ charge.montant|number_format(0, \',\', \' \') }} FCFA\n\t\t\t\t\t\t\t\t\t\t</td>\n\n\t\t\t\t\t\t\t\t\t\t<td class="align-middle">\n\t\t\t\t\t\t\t\t\t\t\t{{ charge.frequence == \'annuelle\' ? \'Tous les ans\' : \'Tous les mois\' }}\n\t\t\t\t\t\t\t\t\t\t\t<div class="small text-muted">\n\t\t\t\t\t\t\t\t\t\t\t\t{% if charge.frequence == \'annuelle\' %}\n\t\t\t\t\t\t\t\t\t\t\t\t\tle {{ charge.jourDuMois }}/{{ charge.moisDeLAnnee }}\n\t\t\t\t\t\t\t\t\t\t\t\t{% else %}\n\t\t\t\t\t\t\t\t\t\t\t\t\tle {{ charge.jourDuMois }} du mois\n\t\t\t\t\t\t\t\t\t\t\t\t{% endif %}\n\t\t\t\t\t\t\t\t\t\t\t</div>\n\t\t\t\t\t\t\t\t\t\t</td>\n\n\t\t\t\t\t\t\t\t\t\t<td class="align-middle">\n\t\t\t\t\t\t\t\t\t\t\t{{ charge.prochaineDateExecution ? charge.prochaineDateExecution|date(\'d/m/Y\') : \'—\' }}\n\t\t\t\t\t\t\t\t\t\t\t{% if charge.derniereDateExecution %}\n\t\t\t\t\t\t\t\t\t\t\t\t<div class="small text-muted">\n\t\t\t\t\t\t\t\t\t\t\t\t\tDernière : {{ charge.derniereDateExecution|date(\'d/m/Y\') }}\n\t\t\t\t\t\t\t\t\t\t\t\t</div>\n\t\t\t\t\t\t\t\t\t\t\t{% endif %}\n\t\t\t\t\t\t\t\t\t\t</td>\n\n\t\t\t\t\t\t\t\t\t\t<td class="align-middle text-center">\n\t\t\t\t\t\t\t\t\t\t\t{% if charge.actif %}\n\t\t\t\t\t\t\t\t\t\t\t\t<span class="badge badge-success">Active</span>\n\t\t\t\t\t\t\t\t\t\t\t{% else %}\n\t\t\t\t\t\t\t\t\t\t\t\t<span class="badge badge-light">Suspendue</span>\n\t\t\t\t\t\t\t\t\t\t\t{% endif %}\n\t\t\t\t\t\t\t\t\t\t</td>\n\n\t\t\t\t\t\t\t\t\t\t<td class="align-middle text-center nowrap">\n\t\t\t\t\t\t\t\t\t\t\t<div class="btn-group">\n\n\t\t\t\t\t\t\t\t\t\t\t\t<a href="{{ path(\'app_decaissement_recurrent_edit\', {id: charge.id}) }}" class="btn btn-sm btn-warning-light" title="Modifier">\n\t\t\t\t\t\t\t\t\t\t\t\t\t<i class="fa fa-pencil"></i>\n\t\t\t\t\t\t\t\t\t\t\t\t</a>\n\n\t\t\t\t\t\t\t\t\t\t\t\t<form method="post" action="{{ path(\'app_decaissement_recurrent_toggle_actif\', {id: charge.id}) }}" class="d-inline">\n\t\t\t\t\t\t\t\t\t\t\t\t\t<input type="hidden" name="_token" value="{{ csrf_token(\'toggle_actif\' ~ charge.id) }}">\n\t\t\t\t\t\t\t\t\t\t\t\t\t<button type="submit" class="btn btn-sm btn-secondary-light" title="{{ charge.actif ? \'Suspendre\' : \'Réactiver\' }}">\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t<i class="fa {{ charge.actif ? \'fa-pause\' : \'fa-play\' }}"></i>\n\t\t\t\t\t\t\t\t\t\t\t\t\t</button>\n\t\t\t\t\t\t\t\t\t\t\t\t</form>\n\n\t\t\t\t\t\t\t\t\t\t\t\t<form method="post" action="{{ path(\'app_decaissement_recurrent_delete\', {id: charge.id}) }}" class="d-inline js-confirm-form" data-message="Supprimer définitivement cette charge récurrente ?">\n\t\t\t\t\t\t\t\t\t\t\t\t\t<input type="hidden" name="_token" value="{{ csrf_token(\'delete\' ~ charge.id) }}">\n\t\t\t\t\t\t\t\t\t\t\t\t\t<button type="submit" class="btn btn-sm btn-danger-light" title="Supprimer">\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t<i class="fa fa-trash"></i>\n\t\t\t\t\t\t\t\t\t\t\t\t\t</button>\n\t\t\t\t\t\t\t\t\t\t\t\t</form>\n\n\t\t\t\t\t\t\t\t\t\t\t</div>\n\t\t\t\t\t\t\t\t\t\t</td>\n\n\t\t\t\t\t\t\t\t\t</tr>\n\n\t\t\t\t\t\t\t\t{% else %}\n\n\t\t\t\t\t\t\t\t\t<tr>\n\t\t\t\t\t\t\t\t\t\t<td colspan="8" class="text-center text-muted py-5">\n\t\t\t\t\t\t\t\t\t\t\tAucune charge récurrente enregistrée.\n\t\t\t\t\t\t\t\t\t\t</td>\n\t\t\t\t\t\t\t\t\t</tr>\n\n\t\t\t\t\t\t\t\t{% endfor %}\n\n\t\t\t\t\t\t\t</tbody>\n\n\t\t\t\t\t\t</table>\n\n\t\t\t\t\t</div>\n\n\t\t\t\t</div>\n\n\t\t\t</div>\n\n\t\t</div>\n\n\t</div>\n\n{% endblock %}\n'

MIGRATION_PHP = '<?php\n\ndeclare(strict_types=1);\n\nnamespace DoctrineMigrations;\n\nuse Doctrine\\DBAL\\Schema\\Schema;\nuse Doctrine\\Migrations\\AbstractMigration;\n\nfinal class Version20260825090000 extends AbstractMigration\n{\n    public function getDescription(): string\n    {\n        return "Cree la table decaissement_recurrent (frais bancaires, "\n            . "remboursement de credit... decaisses automatiquement).";\n    }\n\n    public function up(Schema $schema): void\n    {\n        $this->addSql(\n            \'CREATE TABLE decaissement_recurrent (\n                id INT AUTO_INCREMENT NOT NULL,\n                compte_source_id INT NOT NULL,\n                cree_par_id INT DEFAULT NULL,\n                libelle VARCHAR(255) NOT NULL,\n                categorie VARCHAR(30) NOT NULL,\n                montant INT NOT NULL,\n                frequence VARCHAR(20) NOT NULL,\n                jour_du_mois SMALLINT NOT NULL,\n                mois_de_lannee SMALLINT DEFAULT NULL,\n                actif TINYINT(1) NOT NULL,\n                date_debut DATE NOT NULL,\n                prochaine_date_execution DATE NOT NULL,\n                derniere_date_execution DATE DEFAULT NULL,\n                date_creation DATETIME NOT NULL,\n                notes LONGTEXT DEFAULT NULL,\n                INDEX idx_decaissement_recurrent_compte (compte_source_id),\n                INDEX idx_decaissement_recurrent_cree_par (cree_par_id),\n                INDEX idx_decaissement_recurrent_prochaine_echeance (actif, prochaine_date_execution),\n                PRIMARY KEY (id)\n            ) DEFAULT CHARACTER SET utf8mb4 COLLATE `utf8mb4_unicode_ci` ENGINE = InnoDB\'\n        );\n\n        $this->addSql(\n            \'ALTER TABLE decaissement_recurrent ADD CONSTRAINT FK_decaissement_recurrent_compte\n             FOREIGN KEY (compte_source_id) REFERENCES compte_tresorerie (id) ON DELETE RESTRICT\'\n        );\n\n        $this->addSql(\n            \'ALTER TABLE decaissement_recurrent ADD CONSTRAINT FK_decaissement_recurrent_cree_par\n             FOREIGN KEY (cree_par_id) REFERENCES `user` (id) ON DELETE SET NULL\'\n        );\n    }\n\n    public function down(Schema $schema): void\n    {\n        $this->addSql(\'DROP TABLE decaissement_recurrent\');\n    }\n}\n'

DECAISSEMENTS_BAT = '@echo off\n\n:: ============================================================\n:: EXECUTION DES DECAISSEMENTS AUTOMATIQUES\n::\n:: Lance la commande Symfony qui cree les mouvements de\n:: tresorerie des charges recurrentes arrivees a echeance\n:: (frais bancaires, remboursement de credit...).\n::\n:: Ce script est concu pour etre appele chaque jour par une\n:: tache planifiee Windows (voir\n:: installer_tache_decaissements_recurrents.bat) : il ne fait\n:: rien de visible si aucune charge n\'est due ce jour-la.\n:: ============================================================\n\nset PROJET=C:\\xamppok\\htdocs\\successImprim\nset PHP=C:\\xamppok\\php\\php.exe\nset LOG_FILE=%PROJET%\\var\\log\\decaissements_recurrents.log\n\nif not exist "%PROJET%\\var\\log" mkdir "%PROJET%\\var\\log"\n\necho [%date% %time%] Debut execution decaissements recurrents >> "%LOG_FILE%"\n\n"%PHP%" "%PROJET%\\bin\\console" app:executer-decaissements-recurrents >> "%LOG_FILE%" 2>&1\n\necho [%date% %time%] Fin execution (code %ERRORLEVEL%) >> "%LOG_FILE%"\n'

INSTALLER_TACHE_BAT = '@echo off\n\n:: ============================================================\n:: INSTALLATION DE LA TACHE PLANIFIEE\n:: "DECAISSEMENTS AUTOMATIQUES"\n::\n:: A executer UNE SEULE FOIS, avec un clic droit\n:: "Executer en tant qu\'administrateur".\n::\n:: Reexecuter ce script est sans risque : /f remplace la tache\n:: existante du meme nom au lieu d\'en creer un doublon.\n:: ============================================================\n\nset SCRIPT_DECAISSEMENTS=C:\\xamppok\\htdocs\\successImprim\\scripts\\windows\\decaissements_recurrents.bat\n\necho Installation de la tache "decaissements automatiques" (tous les jours a 06:00)...\nschtasks /create ^\n    /tn "SuccessImprim_DecaissementsRecurrents" ^\n    /tr "\\"%SCRIPT_DECAISSEMENTS%\\"" ^\n    /sc daily ^\n    /st 06:00 ^\n    /ru SYSTEM ^\n    /f\n\necho.\necho Termine. Verification :\nschtasks /query /tn "SuccessImprim_DecaissementsRecurrents"\n\necho.\necho Pour tester tout de suite, sans attendre demain 06:00 :\necho   schtasks /run /tn "SuccessImprim_DecaissementsRecurrents"\necho.\necho Le resultat de chaque execution est journalise dans :\necho   C:\\xamppok\\htdocs\\successImprim\\var\\log\\decaissements_recurrents.log\necho.\npause\n'


if __name__ == "__main__":
    main()
