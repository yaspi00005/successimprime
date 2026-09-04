#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrige le compteur m2 des machines qui restait bloque a 0 malgre des
impressions terminees.

Cause : le compteur etait un nombre ENTIER, et chaque impression
etait arrondie individuellement avant d'etre ajoutee. Un travail de
0,0468 m2 (ex: 0,04 x 1,17 m) donne 0 une fois arrondi -- il
disparaissait donc silencieusement, comme tous les travaux de moins
de 0,5 m2. Ce n'est pas un probleme de "beaucoup" de petits travaux
qui ne s'additionnent pas : c'est que RIEN ne s'additionnait pour ce
genre de travail, car l'arrondi se faisait avant l'addition, a
chaque fois.

Ce script :
  1. ajoute une migration qui passe la colonne machines.compteur_m2
     d'entier a decimal (aucune perte : les valeurs existantes sont
     converties automatiquement) ;
  2. dans Machines.php, change compteurM2 de int a float et retire
     l'arrondi premature dans enregistrerUsage() ;
  3. dans MachinesController.php, ajoute une methode recupererDecimal()
     (comme recupererEntier(), mais accepte les virgules/points) et
     l'utilise pour compteurM2 ;
  4. dans machines/index.html.twig, affiche le compteur m2 avec 2
     decimales et permet de saisir des decimales dans les formulaires
     de creation/edition.

Usage:
    python3 corriger_arrondi_compteur_m2.py /chemin/vers/successImprim
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


MIGRATION_CONTENU = """<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\\DBAL\\Schema\\Schema;
use Doctrine\\Migrations\\AbstractMigration;

final class Version20260831160000 extends AbstractMigration
{
    public function getDescription(): string
    {
        return "Passe machines.compteur_m2 en decimal : un arrondi a "
            . "l'entier avant addition faisait disparaitre les petits "
            . "travaux (moins de 0,5 m2) du compteur d'usure.";
    }

    public function up(Schema $schema): void
    {
        $this->addSql(
            'ALTER TABLE machines MODIFY compteur_m2 DOUBLE PRECISION DEFAULT NULL'
        );
    }

    public function down(Schema $schema): void
    {
        $this->addSql(
            'ALTER TABLE machines MODIFY compteur_m2 INT DEFAULT NULL'
        );
    }
}
"""


def creer_migration(racine):
    chemin_relatif = "migrations/Version20260831160000.php"
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


def appliquer_paires(racine, chemin_relatif, marqueur, paires, diagnostic):
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

    for index, (ancien, nouveau) in enumerate(paires):
        if nouveau in contenu:
            print("  [SKIP bloc " + str(index) + "] deja present.")
            continue

        if ancien not in contenu:
            print("  [ECHEC bloc " + str(index) + "] reference introuvable.")
            tout_ok = False
            continue

        if contenu.count(ancien) > 1:
            print("  [ECHEC bloc " + str(index) + "] reference trouvee plusieurs fois -> ignore par prudence.")
            tout_ok = False
            continue

        contenu = contenu.replace(ancien, nouveau, 1)
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
        "    #[ORM\\Column(type: Types::INTEGER)]\n    private ?int $compteurM2 = null;",
        "    /*\n     * En m\u00b2 decimaux (Types::FLOAT) et non plus en entier : un\n     * arrondi a chaque impression individuelle ferait disparaitre\n     * tous les petits travaux (moins de 0,5 m\u00b2) avant meme qu'ils\n     * ne s'additionnent. Voir enregistrerUsage().\n     */\n    #[ORM\\Column(type: Types::FLOAT, nullable: true)]\n    private ?float $compteurM2 = null;",
    ),
    (
        "    public function getCompteurM2(): ?int\n    {\n        return $this->compteurM2;\n    }\n\n    public function setCompteurM2(int $compteurM2): static\n    {\n        $this->compteurM2 = $compteurM2;\n\n        return $this;\n    }",
        "    public function getCompteurM2(): ?float\n    {\n        return $this->compteurM2;\n    }\n\n    public function setCompteurM2(float $compteurM2): static\n    {\n        $this->compteurM2 = $compteurM2;\n\n        return $this;\n    }",
    ),
    (
        "        if ($this->utiliseSurface()) {\n            $this->compteurM2 = ($this->compteurM2 ?? 0) + (int) round($surfaceM2Totale);\n\n            return;",
        "        if ($this->utiliseSurface()) {\n            $this->compteurM2 = round(($this->compteurM2 ?? 0) + $surfaceM2Totale, 2);\n\n            return;",
    ),
]

MACHINESCONTROLLER_PHP_PAIRES = [
    (
        "        $compteurM2 = $this->recupererEntier(\n            $request,\n            'compteurM2',\n            0\n        );",
        "        $compteurM2 = $this->recupererDecimal(\n            $request,\n            'compteurM2',\n            0.0\n        );",
    ),
    (
        "        if (!ctype_digit($valeur)) {\n            throw new \\InvalidArgumentException(\n                sprintf(\n                    'Le champ %s doit contenir un nombre entier.',\n                    $champ\n                )\n            );\n        }\n\n        return (int) $valeur;\n    }",
        "        if (!ctype_digit($valeur)) {\n            throw new \\InvalidArgumentException(\n                sprintf(\n                    'Le champ %s doit contenir un nombre entier.',\n                    $champ\n                )\n            );\n        }\n\n        return (int) $valeur;\n    }\n\n    /*\n     * Comme recupererEntier(), mais accepte les decimales -- utilise\n     * pour compteurM2, alimente automatiquement avec des surfaces\n     * fractionnaires (voir Machines::enregistrerUsage()).\n     */\n    private function recupererDecimal(\n        Request $request,\n        string $champ,\n        float $valeurParDefaut = 0.0\n    ): float {\n        $valeur = trim(\n            (string) $request->request->get($champ)\n        );\n\n        if ($valeur === '') {\n            return $valeurParDefaut;\n        }\n\n        $valeur = str_replace(',', '.', $valeur);\n\n        if (!is_numeric($valeur)) {\n            throw new \\InvalidArgumentException(\n                sprintf(\n                    'Le champ %s doit contenir un nombre.',\n                    $champ\n                )\n            );\n        }\n\n        return max(0.0, (float) $valeur);\n    }",
    ),
]

MACHINES_TWIG_PAIRES = [
    (
        '<strong>\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t{{ machine.compteurM2\n                                                        is not null\n                                                        ? machine.compteurM2\n                                                        : 0\n                                                    }}\n\t\t\t\t\t\t\t\t\t\t\t\t\t</strong>',
        "<strong>\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t{{ machine.compteurM2\n                                                        is not null\n                                                        ? machine.compteurM2|number_format(2, ',', ' ')\n                                                        : 0\n                                                    }}\n\t\t\t\t\t\t\t\t\t\t\t\t\t</strong>",
    ),
    (
        '<input type="number" id="machineCreateCompteurM2" class="form-control" min="0" step="1" value="0">',
        '<input type="number" id="machineCreateCompteurM2" class="form-control" min="0" step="0.01" value="0">',
    ),
    (
        '<input type="number" id="machineEditCompteurM2" class="form-control" min="0" step="1">',
        '<input type="number" id="machineEditCompteurM2" class="form-control" min="0" step="0.01">',
    ),
]

MARQUEUR_MACHINES_PHP = "En m\u00b2 decimaux (Types::FLOAT)"
MARQUEUR_MACHINESCONTROLLER_PHP = "function recupererDecimal"
MARQUEUR_MACHINES_TWIG = 'step="0.01" value="0">'


def main():
    racine = sys.argv[1] if len(sys.argv) >= 2 else "."
    verifier_racine(racine)

    resultats = []

    print("-" * 70)
    print("migrations/Version20260831160000.php (nouveau fichier)")
    print("-" * 70)
    resultats.append(creer_migration(racine))
    print()

    print("-" * 70)
    print("src/Entity/Machines.php")
    print("-" * 70)
    resultats.append(appliquer_paires(
        racine, "src/Entity/Machines.php", MARQUEUR_MACHINES_PHP,
        MACHINES_PHP_PAIRES,
        "grep -n -B2 -A6 \"compteurM2\" src/Entity/Machines.php"
    ))
    print()

    print("-" * 70)
    print("src/Controller/MachinesController.php")
    print("-" * 70)
    resultats.append(appliquer_paires(
        racine, "src/Controller/MachinesController.php", MARQUEUR_MACHINESCONTROLLER_PHP,
        MACHINESCONTROLLER_PHP_PAIRES,
        "grep -n -B2 -A10 \"function recupererEntier\" src/Controller/MachinesController.php"
    ))
    print()

    print("-" * 70)
    print("templates/machines/index.html.twig")
    print("-" * 70)
    resultats.append(appliquer_paires(
        racine, "templates/machines/index.html.twig", MARQUEUR_MACHINES_TWIG,
        MACHINES_TWIG_PAIRES,
        "grep -n \"machineCreateCompteurM2\\|machineEditCompteurM2\" templates/machines/index.html.twig"
    ))
    print()

    try:
        r1 = subprocess.run(["php", "-l", os.path.join(racine, "src/Entity/Machines.php")], capture_output=True, text=True, timeout=30)
        print("php -l Machines.php : " + r1.stdout.strip() + r1.stderr.strip())

        r2 = subprocess.run(["php", "-l", os.path.join(racine, "src/Controller/MachinesController.php")], capture_output=True, text=True, timeout=30)
        print("php -l MachinesController.php : " + r2.stdout.strip() + r2.stderr.strip())
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
        print("Les petits travaux (moins de 0,5 m2) vont maintenant")
        print("s'additionner correctement au compteur m2, au lieu de")
        print("disparaitre a chaque fois.")
    else:
        print("Un ou plusieurs fichiers n'ont pas pu etre modifies (voir [ECHEC] ci-dessus).")
        print("Recopiez-moi TOUT ce resume, je corrige avant de vous renvoyer le script.")


if __name__ == "__main__":
    main()
