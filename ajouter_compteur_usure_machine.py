#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ajoute le suivi automatique de l'usure des machines : chaque
impression terminée ajuste desormais le compteur de la machine
utilisee (compteur_m2 pour les machines facturees au metre carre,
nouveau compteur_feuilles en A4-equivalent pour les machines
facturees a la feuille). L'amortissement reste calcule sur le temps
ecoule (inchange) -- ce compteur sert uniquement a anticiper la
maintenance.

5 endroits modifies :
  1) src/Entity/Machines.php : nouveau champ compteur_feuilles +
     methode enregistrerUsage().
  2) src/Controller/ProductionController.php : au moment de terminer
     une production, calcule la surface imprimee (largeur x longueur
     x quantite traitee) et l'ajoute au compteur de la machine.
  3) src/Controller/MachinesController.php : le compteur feuilles est
     lisible/modifiable manuellement comme les deux autres compteurs.
  4) templates/machines/index.html.twig : affichage + champs de
     creation/modification pour le nouveau compteur.
  5) migrations/Version20260826120000.php (nouveau fichier) : ajoute
     la colonne compteur_feuilles.

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


def php_lint(chemin_absolu):
    try:
        resultat = subprocess.run(
            ["php", "-l", chemin_absolu],
            capture_output=True, text=True, timeout=30
        )
        print("  php -l : " + resultat.stdout.strip() + resultat.stderr.strip())
    except Exception:
        pass


def remplacer_unique(chemin_relatif, contenu, ancien, nouveau, description):
    if ancien not in contenu:
        print("[ECHEC] " + chemin_relatif + " : '" + description + "' introuvable -> abandon (rien ecrit).")
        return None
    return contenu.replace(ancien, nouveau, 1)


# ============================================================
# 1) src/Entity/Machines.php
# ============================================================

ANCIEN_CHAMP = """    #[ORM\\Column(type: Types::INTEGER)]
    private ?int $compteurHeures = null;"""

NOUVEAU_CHAMP = """    #[ORM\\Column(type: Types::INTEGER)]
    private ?int $compteurHeures = null;

    /*
     * Compteur en feuilles A4-équivalent (une A3 compte pour 2 A4),
     * pour les machines facturées à la feuille. Distinct de
     * compteurM2, réservé aux machines grand format.
     */
    #[ORM\\Column(type: Types::INTEGER, options: ['default' => 0])]
    private int $compteurFeuilles = 0;"""

ANCIEN_GETTER = """    public function getCompteurHeures(): ?int
    {
        return $this->compteurHeures;
    }

    public function setCompteurHeures(int $compteurHeures): static
    {
        $this->compteurHeures = $compteurHeures;

        return $this;
    }"""

NOUVEAU_GETTER = """    public function getCompteurHeures(): ?int
    {
        return $this->compteurHeures;
    }

    public function setCompteurHeures(int $compteurHeures): static
    {
        $this->compteurHeures = $compteurHeures;

        return $this;
    }

    public function getCompteurFeuilles(): int
    {
        return $this->compteurFeuilles;
    }

    public function setCompteurFeuilles(int $compteurFeuilles): static
    {
        $this->compteurFeuilles = $compteurFeuilles;

        return $this;
    }"""

ANCIEN_UTILISE_FEUILLE = """    public function utiliseFeuille(): bool
    {
        return $this->modeFacturation === self::MODE_FACTURATION_FEUILLE;
    }"""

NOUVEAU_UTILISE_FEUILLE = """    public function utiliseFeuille(): bool
    {
        return $this->modeFacturation === self::MODE_FACTURATION_FEUILLE;
    }

    /*
     * Surface d'une feuille A4, en m² (0,21 x 0,297) — sert de
     * référence pour convertir une surface imprimée en nombre de
     * feuilles A4-équivalent (une A3 compte pour 2 A4).
     */
    private const SURFACE_A4_M2 = 0.21 * 0.297;

    /**
     * Ajoute l'usage d'une impression au compteur d'usure de la
     * machine, uniquement pour suivre la maintenance — n'affecte pas
     * le calcul de l'amortissement (basé sur le temps écoulé, voir
     * getChargeAmortissementMensuelle()). Le compteur alimenté dépend
     * du mode de facturation de la machine.
     */
    public function enregistrerUsage(float $surfaceM2Totale): void
    {
        if ($surfaceM2Totale <= 0) {
            return;
        }

        if ($this->utiliseSurface()) {
            $this->compteurM2 = ($this->compteurM2 ?? 0) + (int) round($surfaceM2Totale);

            return;
        }

        if ($this->utiliseFeuille()) {
            $this->compteurFeuilles += (int) round(
                $surfaceM2Totale / self::SURFACE_A4_M2
            );
        }
    }"""

MARQUEUR_MACHINES = "enregistrerUsage"


def corriger_machines(racine):
    chemin_relatif = "src/Entity/Machines.php"
    chemin_absolu = os.path.join(racine, chemin_relatif)

    print("-" * 70)
    print(chemin_relatif)
    print("-" * 70)

    if not os.path.isfile(chemin_absolu):
        print("[ABSENT] " + chemin_relatif + " n'existe pas du tout sur le disque.")
        return False

    with open(chemin_absolu, "r", encoding="utf-8") as f:
        contenu = f.read()

    if MARQUEUR_MACHINES in contenu:
        print("[SKIP] " + chemin_relatif + " contient deja '" + MARQUEUR_MACHINES + "' (deja applique).")
        return True

    contenu2 = remplacer_unique(chemin_relatif, contenu, ANCIEN_CHAMP, NOUVEAU_CHAMP, "champ compteurHeures")
    if contenu2 is None:
        print("  Copiez-moi le resultat de :")
        print("    grep -n -B2 -A2 \"compteurHeures = null\" " + chemin_relatif)
        return False

    contenu3 = remplacer_unique(chemin_relatif, contenu2, ANCIEN_GETTER, NOUVEAU_GETTER, "getter/setter compteurHeures")
    if contenu3 is None:
        print("  Copiez-moi le resultat de :")
        print("    grep -n -A10 \"function getCompteurHeures\" " + chemin_relatif)
        return False

    contenu4 = remplacer_unique(chemin_relatif, contenu3, ANCIEN_UTILISE_FEUILLE, NOUVEAU_UTILISE_FEUILLE, "methode utiliseFeuille")
    if contenu4 is None:
        print("  Copiez-moi le resultat de :")
        print("    grep -n -A5 \"function utiliseFeuille\" " + chemin_relatif)
        return False

    with open(chemin_absolu, "w", encoding="utf-8", newline="") as f:
        f.write(contenu4)
        f.flush()
        os.fsync(f.fileno())

    with open(chemin_absolu, "r", encoding="utf-8", newline="") as f:
        relu = f.read()

    if relu != contenu4:
        print("[ECHEC VERIFICATION] " + chemin_relatif + " : le contenu relu ne correspond pas.")
        return False

    print("[OK VERIFIE] " + chemin_relatif)
    print("  Chemin reel : " + os.path.realpath(chemin_absolu))
    php_lint(chemin_absolu)
    return True


# ============================================================
# 2) src/Controller/ProductionController.php
# ============================================================

ANCIEN_TERMINER = """        $ordre->terminer(
            $utilisateur,
            $quantiteProduite,
            $quantiteRebut,
            $observation
        );

        /*
         * ========================================================
         * NOTIFICATION
         * ========================================================"""

NOUVEAU_TERMINER = """        $ordre->terminer(
            $utilisateur,
            $quantiteProduite,
            $quantiteRebut,
            $observation
        );

        /*
         * ========================================================
         * COMPTEUR D'USURE MACHINE
         * ========================================================
         *
         * Suivi de l'usage uniquement (maintenance) : n'affecte pas
         * l'amortissement, calculé sur le temps écoulé. Alimente
         * compteurM2 ou compteurFeuilles selon le mode de facturation
         * de la machine ; ignoré si la ligne n'a pas de dimensions
         * (article en stock, saisie libre).
         */
        $machineUtilisee = $ordre->getMachine();

        if ($machineUtilisee instanceof Machines) {
            $largeurDetail = (float) ($detail->getLargeur() ?? 0);
            $longueurDetail = (float) ($detail->getLongueur() ?? 0);

            if ($largeurDetail > 0 && $longueurDetail > 0) {
                $machineUtilisee->enregistrerUsage(
                    $largeurDetail * $longueurDetail * $quantiteTraitee
                );
            }
        }

        /*
         * ========================================================
         * NOTIFICATION
         * ========================================================"""

MARQUEUR_PRODUCTION = "COMPTEUR D'USURE MACHINE"


def corriger_production(racine):
    chemin_relatif = "src/Controller/ProductionController.php"
    chemin_absolu = os.path.join(racine, chemin_relatif)

    print()
    print("-" * 70)
    print(chemin_relatif)
    print("-" * 70)

    if not os.path.isfile(chemin_absolu):
        print("[ABSENT] " + chemin_relatif + " n'existe pas du tout sur le disque.")
        return False

    with open(chemin_absolu, "r", encoding="utf-8") as f:
        contenu = f.read()

    if MARQUEUR_PRODUCTION in contenu:
        print("[SKIP] " + chemin_relatif + " contient deja la logique du compteur d'usure (deja applique).")
        return True

    if "use App\\Entity\\Machines;" not in contenu:
        print("[ECHEC] " + chemin_relatif + " : import de Machines introuvable -> abandon (rien ecrit).")
        print("  Copiez-moi le resultat de :")
        print("    grep -n \"^use App\\\\\\\\Entity\" " + chemin_relatif)
        return False

    contenu_corrige = remplacer_unique(chemin_relatif, contenu, ANCIEN_TERMINER, NOUVEAU_TERMINER, "fin de la methode terminer()")

    if contenu_corrige is None:
        print("  Copiez-moi le resultat de :")
        print("    grep -n -B3 -A10 \"NOTIFICATION\" " + chemin_relatif + " | head -30")
        return False

    with open(chemin_absolu, "w", encoding="utf-8", newline="") as f:
        f.write(contenu_corrige)
        f.flush()
        os.fsync(f.fileno())

    with open(chemin_absolu, "r", encoding="utf-8", newline="") as f:
        relu = f.read()

    if relu != contenu_corrige:
        print("[ECHEC VERIFICATION] " + chemin_relatif + " : le contenu relu ne correspond pas.")
        return False

    print("[OK VERIFIE] " + chemin_relatif)
    print("  Chemin reel : " + os.path.realpath(chemin_absolu))
    php_lint(chemin_absolu)
    return True


# ============================================================
# 3) src/Controller/MachinesController.php
# ============================================================

ANCIEN_LECTURE = """        $compteurHeures = $this->recupererEntier(
            $request,
            'compteurHeures',
            0
        );"""

NOUVELLE_LECTURE = """        $compteurHeures = $this->recupererEntier(
            $request,
            'compteurHeures',
            0
        );

        $compteurFeuilles = $this->recupererEntier(
            $request,
            'compteurFeuilles',
            0
        );"""

ANCIENNE_AFFECTATION = """            ->setCompteurM2($compteurM2)
            ->setCompteurHeures($compteurHeures)
            ->setEtat($etat)"""

NOUVELLE_AFFECTATION = """            ->setCompteurM2($compteurM2)
            ->setCompteurHeures($compteurHeures)
            ->setCompteurFeuilles($compteurFeuilles)
            ->setEtat($etat)"""

ANCIEN_TABLEAU = """            'compteurHeures' =>
                $machine->getCompteurHeures(),

            'etat' => $machine->getEtat(),"""

NOUVEAU_TABLEAU = """            'compteurHeures' =>
                $machine->getCompteurHeures(),

            'compteurFeuilles' =>
                $machine->getCompteurFeuilles(),

            'etat' => $machine->getEtat(),"""

MARQUEUR_MACHINES_CONTROLLER = "compteurFeuilles"


def corriger_machines_controller(racine):
    chemin_relatif = "src/Controller/MachinesController.php"
    chemin_absolu = os.path.join(racine, chemin_relatif)

    print()
    print("-" * 70)
    print(chemin_relatif)
    print("-" * 70)

    if not os.path.isfile(chemin_absolu):
        print("[ABSENT] " + chemin_relatif + " n'existe pas du tout sur le disque.")
        return False

    with open(chemin_absolu, "r", encoding="utf-8") as f:
        contenu = f.read()

    if MARQUEUR_MACHINES_CONTROLLER in contenu:
        print("[SKIP] " + chemin_relatif + " contient deja 'compteurFeuilles' (deja applique).")
        return True

    contenu2 = remplacer_unique(chemin_relatif, contenu, ANCIEN_LECTURE, NOUVELLE_LECTURE, "lecture compteurHeures")
    if contenu2 is None:
        print("  Copiez-moi le resultat de :")
        print("    grep -n -A6 \"compteurHeures = .this->recupererEntier\" " + chemin_relatif)
        return False

    contenu3 = remplacer_unique(chemin_relatif, contenu2, ANCIENNE_AFFECTATION, NOUVELLE_AFFECTATION, "affectation setCompteurHeures")
    if contenu3 is None:
        print("  Copiez-moi le resultat de :")
        print("    grep -n -B2 -A2 \"setCompteurHeures\" " + chemin_relatif)
        return False

    contenu4 = remplacer_unique(chemin_relatif, contenu3, ANCIEN_TABLEAU, NOUVEAU_TABLEAU, "tableau compteurHeures")
    if contenu4 is None:
        print("  Copiez-moi le resultat de :")
        print("    grep -n -B2 -A4 \"'compteurHeures' =>\" " + chemin_relatif)
        return False

    with open(chemin_absolu, "w", encoding="utf-8", newline="") as f:
        f.write(contenu4)
        f.flush()
        os.fsync(f.fileno())

    with open(chemin_absolu, "r", encoding="utf-8", newline="") as f:
        relu = f.read()

    if relu != contenu4:
        print("[ECHEC VERIFICATION] " + chemin_relatif + " : le contenu relu ne correspond pas.")
        return False

    print("[OK VERIFIE] " + chemin_relatif)
    print("  Chemin reel : " + os.path.realpath(chemin_absolu))
    php_lint(chemin_absolu)
    return True


# ============================================================
# 4) templates/machines/index.html.twig
# ============================================================

ANCIEN_AFFICHAGE = """<div>
													<small class="text-muted">
														Heures :
													</small>

													<strong>
														{{ machine.compteurHeures
                                                        is not null
                                                        ? machine.compteurHeures
                                                        : 0
                                                    }}
													</strong>
												</div>

											</td>"""

NOUVEL_AFFICHAGE = """<div>
													<small class="text-muted">
														Heures :
													</small>

													<strong>
														{{ machine.compteurHeures
                                                        is not null
                                                        ? machine.compteurHeures
                                                        : 0
                                                    }}
													</strong>
												</div>

												<div>
													<small class="text-muted">
														Feuilles :
													</small>

													<strong>
														{{ machine.compteurFeuilles|default(0) }}
													</strong>
												</div>

											</td>"""

ANCIEN_CHAMP_CREATE = """						{# COMPTEUR HEURES #}
						<div class="col-md-6">

							<div class="form-group">

								<label class="form-label" for="machineCreateCompteurHeures">
									Compteur heures
								</label>

								<input type="number" id="machineCreateCompteurHeures" class="form-control" min="0" step="1" value="0">

							</div>

						</div>


						<div class="col-12">
							<hr>
							<h6 class="text-muted">Rentabilité / amortissement</h6>
						</div>"""

NOUVEAU_CHAMP_CREATE = """						{# COMPTEUR HEURES #}
						<div class="col-md-6">

							<div class="form-group">

								<label class="form-label" for="machineCreateCompteurHeures">
									Compteur heures
								</label>

								<input type="number" id="machineCreateCompteurHeures" class="form-control" min="0" step="1" value="0">

							</div>

						</div>


						{# COMPTEUR FEUILLES #}
						<div class="col-md-6">

							<div class="form-group">

								<label class="form-label" for="machineCreateCompteurFeuilles">
									Compteur feuilles (A4-équivalent)
								</label>

								<input type="number" id="machineCreateCompteurFeuilles" class="form-control" min="0" step="1" value="0">

							</div>

						</div>


						<div class="col-12">
							<hr>
							<h6 class="text-muted">Rentabilité / amortissement</h6>
						</div>"""

ANCIEN_CHAMP_EDIT = """								<label class="form-label" for="machineEditCompteurHeures">
									Compteur heures
								</label>

								<input type="number" id="machineEditCompteurHeures" class="form-control" min="0" step="1">

							</div>

						</div>


						<div class="col-12">
							<hr>
							<h6 class="text-muted">Rentabilité / amortissement</h6>
						</div>


						<div class="col-md-4">

							<div class="form-group">"""

NOUVEAU_CHAMP_EDIT = """								<label class="form-label" for="machineEditCompteurHeures">
									Compteur heures
								</label>

								<input type="number" id="machineEditCompteurHeures" class="form-control" min="0" step="1">

							</div>

						</div>


						<div class="col-md-6">

							<div class="form-group">

								<label class="form-label" for="machineEditCompteurFeuilles">
									Compteur feuilles (A4-équivalent)
								</label>

								<input type="number" id="machineEditCompteurFeuilles" class="form-control" min="0" step="1">

							</div>

						</div>


						<div class="col-12">
							<hr>
							<h6 class="text-muted">Rentabilité / amortissement</h6>
						</div>


						<div class="col-md-4">

							<div class="form-group">"""

ANCIEN_JS_CREATE_VAR = """const compteurM2 = valeur('machineCreateCompteurM2');

const compteurHeures = valeur('machineCreateCompteurHeures');

const etat = valeur('machineCreateEtat');"""

NOUVEAU_JS_CREATE_VAR = """const compteurM2 = valeur('machineCreateCompteurM2');

const compteurHeures = valeur('machineCreateCompteurHeures');

const compteurFeuilles = valeur('machineCreateCompteurFeuilles');

const etat = valeur('machineCreateEtat');"""

ANCIEN_JS_EDIT_DEFINIR = """definirValeur('machineEditCompteurM2', machine.compteurM2 ?? 0);

definirValeur('machineEditCompteurHeures', machine.compteurHeures ?? 0);"""

NOUVEAU_JS_EDIT_DEFINIR = """definirValeur('machineEditCompteurM2', machine.compteurM2 ?? 0);

definirValeur('machineEditCompteurHeures', machine.compteurHeures ?? 0);

definirValeur('machineEditCompteurFeuilles', machine.compteurFeuilles ?? 0);"""

ANCIEN_JS_EDIT_VAR = """const compteurM2 = valeur('machineEditCompteurM2');

const compteurHeures = valeur('machineEditCompteurHeures');"""

NOUVEAU_JS_EDIT_VAR = """const compteurM2 = valeur('machineEditCompteurM2');

const compteurHeures = valeur('machineEditCompteurHeures');

const compteurFeuilles = valeur('machineEditCompteurFeuilles');"""

ANCIEN_FORMDATA = "formData.append('compteurHeures', compteurHeures || '0');"
NOUVEAU_FORMDATA = (
    "formData.append('compteurHeures', compteurHeures || '0');\n\n"
    "formData.append('compteurFeuilles', compteurFeuilles || '0');"
)

MARQUEUR_TWIG = "compteurFeuilles"


def corriger_twig(racine):
    chemin_relatif = "templates/machines/index.html.twig"
    chemin_absolu = os.path.join(racine, chemin_relatif)

    print()
    print("-" * 70)
    print(chemin_relatif)
    print("-" * 70)

    if not os.path.isfile(chemin_absolu):
        print("[ABSENT] " + chemin_relatif + " n'existe pas du tout sur le disque.")
        return False

    with open(chemin_absolu, "r", encoding="utf-8") as f:
        contenu = f.read()

    if MARQUEUR_TWIG in contenu:
        print("[SKIP] " + chemin_relatif + " contient deja 'compteurFeuilles' (deja applique).")
        return True

    etapes = [
        (ANCIEN_AFFICHAGE, NOUVEL_AFFICHAGE, "affichage du compteur dans le tableau"),
        (ANCIEN_CHAMP_CREATE, NOUVEAU_CHAMP_CREATE, "champ 'compteur feuilles' (creation)"),
        (ANCIEN_CHAMP_EDIT, NOUVEAU_CHAMP_EDIT, "champ 'compteur feuilles' (modification)"),
        (ANCIEN_JS_CREATE_VAR, NOUVEAU_JS_CREATE_VAR, "variable JS (creation)"),
        (ANCIEN_JS_EDIT_DEFINIR, NOUVEAU_JS_EDIT_DEFINIR, "pre-remplissage JS (modification)"),
        (ANCIEN_JS_EDIT_VAR, NOUVEAU_JS_EDIT_VAR, "variable JS (modification)"),
    ]

    for ancien, nouveau, description in etapes:
        resultat = remplacer_unique(chemin_relatif, contenu, ancien, nouveau, description)
        if resultat is None:
            print("  Copiez-moi le resultat de :")
            print("    grep -n \"machineCreateCompteurHeures\\|machineEditCompteurHeures\" " + chemin_relatif)
            return False
        contenu = resultat

    # Les 2 occurrences de "formData.append('compteurHeures', ...)"
    # (creation et modification) sont identiques : on ajoute la ligne
    # compteurFeuilles apres CHACUNE d'elles.
    nombre_formdata = contenu.count(ANCIEN_FORMDATA)

    if nombre_formdata != 2:
        print("[ECHEC] " + chemin_relatif + " : attendu 2 occurrences de \"formData.append('compteurHeures'...)\", trouve " + str(nombre_formdata) + " -> abandon (rien ecrit).")
        print("  Copiez-moi le resultat de :")
        print("    grep -n \"formData.append('compteurHeures'\" " + chemin_relatif)
        return False

    contenu = contenu.replace(ANCIEN_FORMDATA, NOUVEAU_FORMDATA)

    with open(chemin_absolu, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
        f.flush()
        os.fsync(f.fileno())

    with open(chemin_absolu, "r", encoding="utf-8", newline="") as f:
        relu = f.read()

    if relu != contenu:
        print("[ECHEC VERIFICATION] " + chemin_relatif + " : le contenu relu ne correspond pas.")
        return False

    print("[OK VERIFIE] " + chemin_relatif)
    print("  Chemin reel : " + os.path.realpath(chemin_absolu))
    return True


# ============================================================
# 5) migrations/Version20260826120000.php (nouveau fichier)
# ============================================================

CONTENU_MIGRATION = '''<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\\DBAL\\Schema\\Schema;
use Doctrine\\Migrations\\AbstractMigration;

final class Version20260826120000 extends AbstractMigration
{
    public function getDescription(): string
    {
        return "Ajoute machines.compteur_feuilles (compteur d'usure en "
            . "feuilles A4-equivalent, pour les machines facturees a la feuille).";
    }

    public function up(Schema $schema): void
    {
        $this->addSql(
            'ALTER TABLE machines ADD compteur_feuilles INT DEFAULT 0 NOT NULL'
        );
    }

    public function down(Schema $schema): void
    {
        $this->addSql('ALTER TABLE machines DROP compteur_feuilles');
    }
}
'''


def creer_migration(racine):
    chemin_relatif = "migrations/Version20260826120000.php"
    chemin_absolu = os.path.join(racine, chemin_relatif)

    print()
    print("-" * 70)
    print(chemin_relatif)
    print("-" * 70)

    if os.path.isfile(chemin_absolu):
        print("[SKIP] " + chemin_relatif + " existe deja (deja applique).")
        return True

    dossier = os.path.dirname(chemin_absolu)
    os.makedirs(dossier, exist_ok=True)

    with open(chemin_absolu, "w", encoding="utf-8", newline="") as f:
        f.write(CONTENU_MIGRATION)
        f.flush()
        os.fsync(f.fileno())

    with open(chemin_absolu, "r", encoding="utf-8", newline="") as f:
        relu = f.read()

    if relu != CONTENU_MIGRATION:
        print("[ECHEC VERIFICATION] " + chemin_relatif + " : le contenu relu ne correspond pas.")
        return False

    print("[OK VERIFIE] " + chemin_relatif + " (nouveau fichier cree)")
    php_lint(chemin_absolu)
    return True


def main():
    racine = sys.argv[1] if len(sys.argv) >= 2 else "."
    verifier_racine(racine)

    resultats = [
        corriger_machines(racine),
        corriger_production(racine),
        corriger_machines_controller(racine),
        corriger_twig(racine),
        creer_migration(racine),
    ]

    print()
    print("=" * 70)
    print("RESUME")
    print("=" * 70)

    if all(resultats):
        print("Tout est en place. Lancez maintenant :")
        print("  php bin/console doctrine:migrations:migrate")
        print("  php bin/console cache:clear")
        print()
        print("A chaque production terminee, le compteur de la machine")
        print("utilisee s'ajuste automatiquement :")
        print("  - compteur m2 pour les machines facturees au metre carre ;")
        print("  - nouveau compteur feuilles (A4-equivalent) pour les")
        print("    machines facturees a la feuille.")
        print()
        print("Vous pouvez aussi corriger ces compteurs manuellement sur la")
        print("fiche d'une machine, comme avant.")
        print()
        print("L'amortissement (Rentabilite) continue d'etre calcule sur le")
        print("temps ecoule, sans changement.")
    else:
        print("Au moins un fichier n'a pas pu etre modifie (voir [ECHEC] ci-dessus).")
        print("Recopiez-moi TOUT ce resume, je corrige avant de vous renvoyer le script.")


if __name__ == "__main__":
    main()
