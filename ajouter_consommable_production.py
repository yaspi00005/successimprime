#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ajoute un deuxieme interrupteur independant sur les articles :
"Consommable en production", separe de "Vendable". Un article
(ex. bache vinyle) peut desormais etre a la fois vendable au
client ET consommable manuellement en production (ecran
Consommables), alors qu'un article uniquement vendable (ex.
kakemono) reste absent de cet ecran, comme avant.

Les articles deja non vendables restent visibles dans Consommables
sans rien faire (la migration les marque consommable_production
automatiquement = NOT vendable).

Fichiers concernes :
  - src/Entity/Articles.php (nouveau champ + accesseurs)
  - src/Repository/ArticlesRepository.php (findConsommables())
  - src/Form/ArticlesType.php (nouvelle case a cocher)
  - templates/articles/form.html.twig (affichage)
  - migrations/Version20260901180000.php (nouveau)

Usage:
    python3 ajouter_consommable_production.py /chemin/vers/successImprim
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


def lire(chemin):
    with open(chemin, "r", encoding="utf-8") as f:
        return f.read()


def ecrire(chemin, contenu):
    with open(chemin, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
        f.flush()
        os.fsync(f.fileno())

    with open(chemin, "r", encoding="utf-8", newline="") as f:
        relu = f.read()

    return relu == contenu


def appliquer_paires(racine, chemin_relatif, paires):
    chemin_absolu = os.path.join(racine, chemin_relatif)

    if not os.path.isfile(chemin_absolu):
        print("[ABSENT] " + chemin_relatif + " n'existe pas du tout sur le disque.")
        return False

    contenu = lire(chemin_absolu)
    contenu_original = contenu
    tout_ok = True

    for ancien, nouveau, description in paires:
        if nouveau in contenu:
            print("  [SKIP] " + description + " (deja applique)")
            continue

        if ancien not in contenu:
            print("  [ECHEC] " + description + " : bloc de reference introuvable.")
            tout_ok = False
            continue

        if contenu.count(ancien) > 1:
            print("  [ECHEC] " + description + " : bloc de reference trouve plusieurs fois, abandon.")
            tout_ok = False
            continue

        contenu = contenu.replace(ancien, nouveau, 1)
        print("  [OK] " + description)

    if contenu == contenu_original:
        return tout_ok

    if not ecrire(chemin_absolu, contenu):
        print("[ECHEC VERIFICATION] " + chemin_relatif + " : le contenu relu ne correspond pas.")
        return False

    print("[OK VERIFIE] " + chemin_relatif)
    print("  Chemin reel : " + os.path.realpath(chemin_absolu))
    return tout_ok


def creer_migration(racine):
    chemin_relatif = "migrations/Version20260901180000.php"
    chemin_absolu = os.path.join(racine, chemin_relatif)

    if os.path.isfile(chemin_absolu):
        if lire(chemin_absolu) == MIGRATION:
            print("[SKIP] " + chemin_relatif + " (deja applique)")
            return True
        print("[ATTENTION] " + chemin_relatif + " existe deja avec un contenu different -> non ecrase.")
        return False

    if not ecrire(chemin_absolu, MIGRATION):
        print("[ECHEC VERIFICATION] " + chemin_relatif + " : le contenu relu ne correspond pas.")
        return False

    print("[OK VERIFIE] " + chemin_relatif + " (nouveau fichier)")
    return True


ENTITY_PAIRES = [
    (
        "    #[ORM\\Column(\n    options: [\n        'default' => true,\n    ]\n)]\nprivate bool $vendable = true;",
        '    #[ORM\\Column(\n    options: [\n        \'default\' => true,\n    ]\n)]\nprivate bool $vendable = true;\n\n/*\n * Indépendant de "vendable" : un article peut être vendu\n * directement au client ET servir de matière première\n * consommée manuellement en production (ex. bâche vinyle),\n * alors qu\'un article uniquement vendable (ex. kakémono) ne\n * doit pas apparaître dans l\'écran Consommables.\n */\n#[ORM\\Column(\n    options: [\n        \'default\' => false,\n    ]\n)]\nprivate bool $consommableProduction = false;',
        "champ consommableProduction"
    ),
    (
        'public function setVendable(\n    bool $vendable\n): static {\n    $this->vendable = $vendable;\n\n    return $this;\n}\n    public function __toString(): string',
        'public function setVendable(\n    bool $vendable\n): static {\n    $this->vendable = $vendable;\n\n    return $this;\n}\n\npublic function isConsommableProduction(): bool\n{\n    return $this->consommableProduction;\n}\n\npublic function setConsommableProduction(\n    bool $consommableProduction\n): static {\n    $this->consommableProduction = $consommableProduction;\n\n    return $this;\n}\n    public function __toString(): string',
        "accesseurs isConsommableProduction/setConsommableProduction"
    ),
]

REPO_PAIRES = [
    (
        '    /**\n     * Articles utilisables comme consommables de production\n     * (colle, encre, film...) : jamais vendus directement au\n     * client, donc exclus de "Article en stock" côté commande\n     * (vendable = false).\n     *\n     * @return Articles[]\n     */\n    public function findConsommables(): array\n    {\n        return $this->createQueryBuilder(\'a\')\n            ->andWhere(\'a.vendable = :vendable\')\n            ->andWhere(\'a.actif = :actif\')\n            ->setParameter(\'vendable\', false)\n            ->setParameter(\'actif\', true)\n            ->orderBy(\'a.designation\', \'ASC\')\n            ->getQuery()\n            ->getResult();\n    }',
        '/**\n     * Articles utilisables comme consommables de production\n     * (colle, encre, film...) : soit jamais vendus directement\n     * au client (vendable = false), soit explicitement marqués\n     * "consommable en production" bien qu\'aussi vendables\n     * (ex. bâche vinyle, à la fois vendue et utilisée comme\n     * matière première).\n     *\n     * @return Articles[]\n     */\n    public function findConsommables(): array\n    {\n        return $this->createQueryBuilder(\'a\')\n            ->andWhere(\n                \'a.vendable = :nonVendable OR a.consommableProduction = :consommableProduction\'\n            )\n            ->andWhere(\'a.actif = :actif\')\n            ->setParameter(\'nonVendable\', false)\n            ->setParameter(\'consommableProduction\', true)\n            ->setParameter(\'actif\', true)\n            ->orderBy(\'a.designation\', \'ASC\')\n            ->getQuery()\n            ->getResult();\n    }',
        "findConsommables() inclut aussi les articles vendables marques consommables"
    ),
]

FORM_PAIRES = [
    (
        "->add(\n    'vendable',\n    CheckboxType::class,\n    [\n        'label' =>\n            'Cet article peut être vendu directement',\n\n        'required' =>\n            false,\n    ]\n)",
        "->add(\n    'vendable',\n    CheckboxType::class,\n    [\n        'label' =>\n            'Cet article peut être vendu directement',\n\n        'required' =>\n            false,\n    ]\n)\n->add(\n    'consommableProduction',\n    CheckboxType::class,\n    [\n        'label' =>\n            'Cet article peut aussi être retiré manuellement du stock en production (écran Consommables)',\n\n        'required' =>\n            false,\n    ]\n)",
        "case a cocher Consommable en production"
    ),
]

TMPL_PAIRES = [
    (
        '<div class="col-12">\n\t\t\t\t\t\t{{ form_row(form.vendable) }}\n\t\t\t\t\t</div>',
        '<div class="col-12">\n\t\t\t\t\t\t{{ form_row(form.vendable) }}\n\t\t\t\t\t</div>\n\n\t\t\t\t\t<div class="col-12">\n\t\t\t\t\t\t{{ form_row(form.consommableProduction) }}\n\t\t\t\t\t</div>',
        "affichage de la case a cocher"
    ),
]

MIGRATION = '<?php\n\ndeclare(strict_types=1);\n\nnamespace DoctrineMigrations;\n\nuse Doctrine\\DBAL\\Schema\\Schema;\nuse Doctrine\\Migrations\\AbstractMigration;\n\nfinal class Version20260901180000 extends AbstractMigration\n{\n    public function getDescription(): string\n    {\n        return "Ajoute articles.consommable_production : un article peut "\n            . "desormais etre a la fois vendable ET consommable en "\n            . "production (ex. bache vinyle), independamment l\'un de "\n            . "l\'autre. Les articles deja non vendables gardent leur "\n            . "visibilite dans l\'ecran Consommables (backfill = NOT vendable).";\n    }\n\n    public function up(Schema $schema): void\n    {\n        $this->addSql(\n            \'ALTER TABLE articles ADD consommable_production TINYINT(1) DEFAULT 0 NOT NULL\'\n        );\n\n        $this->addSql(\n            \'UPDATE articles SET consommable_production = (vendable = 0)\'\n        );\n    }\n\n    public function down(Schema $schema): void\n    {\n        $this->addSql(\n            \'ALTER TABLE articles DROP consommable_production\'\n        );\n    }\n}\n'


def main():
    racine = sys.argv[1] if len(sys.argv) >= 2 else "."
    verifier_racine(racine)

    resultats = []

    print("-" * 70)
    print("src/Entity/Articles.php")
    print("-" * 70)
    resultats.append(appliquer_paires(racine, "src/Entity/Articles.php", ENTITY_PAIRES))
    print()

    print("-" * 70)
    print("src/Repository/ArticlesRepository.php")
    print("-" * 70)
    resultats.append(appliquer_paires(racine, "src/Repository/ArticlesRepository.php", REPO_PAIRES))
    print()

    print("-" * 70)
    print("src/Form/ArticlesType.php")
    print("-" * 70)
    resultats.append(appliquer_paires(racine, "src/Form/ArticlesType.php", FORM_PAIRES))
    print()

    print("-" * 70)
    print("templates/articles/form.html.twig")
    print("-" * 70)
    resultats.append(appliquer_paires(racine, "templates/articles/form.html.twig", TMPL_PAIRES))
    print()

    print("-" * 70)
    print("migrations/Version20260901180000.php (nouveau)")
    print("-" * 70)
    resultats.append(creer_migration(racine))
    print()

    for chemin_relatif in [
        "src/Entity/Articles.php",
        "src/Repository/ArticlesRepository.php",
        "src/Form/ArticlesType.php",
        "migrations/Version20260901180000.php",
    ]:
        chemin_absolu = os.path.join(racine, chemin_relatif)
        try:
            resultat = subprocess.run(
                ["php", "-l", chemin_absolu],
                capture_output=True, text=True, timeout=30
            )
            print("php -l " + chemin_relatif + " : " + resultat.stdout.strip() + resultat.stderr.strip())
        except Exception:
            pass

    print()
    print("=" * 70)
    print("RESUME")
    print("=" * 70)

    if all(resultats):
        print("Tout est en place.")
        print()
        print("Derniere etape (obligatoire, modifie la base de donnees) :")
        print("  php bin/console doctrine:migrations:migrate")
        print()
        print("Ensuite, pour un article comme la bache vinyle : ouvrez sa")
        print("fiche (Parametres > Produits > Articles), cochez a la fois")
        print("'Vendable' et 'Consommable en production', enregistrez. Il")
        print("apparaitra alors dans les deux ecrans.")
    else:
        print("Un ou plusieurs blocs n'ont pas pu etre modifies (voir [ECHEC] ci-dessus).")
        print("Recopiez-moi TOUT ce resume, je corrige avant de vous renvoyer le script.")


if __name__ == "__main__":
    main()