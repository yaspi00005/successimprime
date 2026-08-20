#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrige la liste d'articles vide au moment de choisir une ligne de
type "Article" dans une commande (ou un devis).

Cause : le champ Articles::$vendable ("Cet article peut etre vendu
directement", une case a cocher du formulaire article) a pour valeur
par defaut false, et rien ne la coche automatiquement -- la liste de
selection d'une commande/devis ne montre QUE les articles avec
vendable = true. Du coup, tout article cree normalement (sans penser
a cocher cette case precise) reste invisible dans cette liste, meme
avec actif = true.

Corrige :
1) Le defaut de Articles::$vendable passe a true : desormais tout
   nouvel article est vendable directement, sauf si on decoche la
   case expres pour un article reserve a la production interne.
2) Migration de base de donnees pour mettre a jour les articles deja
   crees (dont les 3 dans ta base), afin qu'ils apparaissent
   immediatement dans la liste.

Executer depuis la racine du projet :
    python3 fix_articles_vendable_liste_vide.py

Puis lancer la migration :
    php bin/console doctrine:migrations:migrate
"""

import os
import sys


def appliquer(chemin, ancien, nouveau, label):
    try:
        with open(chemin, "r", encoding="utf-8") as f:
            contenu = f.read()
    except FileNotFoundError:
        print(f"[ERREUR] Fichier introuvable : {chemin}")
        return False

    if nouveau in contenu:
        print(f"[SKIP] {label} : deja applique.")
        return True

    occurrences = contenu.count(ancien)

    if occurrences != 1:
        print(
            f"[ERREUR] {label} : {occurrences} occurrence(s) trouvee(s) "
            f"dans {chemin} (1 attendue)"
        )
        return False

    contenu = contenu.replace(ancien, nouveau)

    with open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)

    print(f"[OK] {label}")
    return True


def creer_fichier(chemin, contenu, label):
    if os.path.isfile(chemin):
        with open(chemin, "r", encoding="utf-8") as f:
            existant = f.read()
        if existant == contenu:
            print(f"[SKIP] {label} : deja applique.")
            return True
        print(
            f"[ERREUR] {label} : {chemin} existe deja avec un contenu "
            f"different. Rien n'a ete ecrase."
        )
        return False

    dossier = os.path.dirname(chemin)
    if dossier and not os.path.isdir(dossier):
        os.makedirs(dossier, exist_ok=True)

    with open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)

    print(f"[OK] {label}")
    return True


resultats = []

resultats.append(appliquer(
    "src/Entity/Articles.php",
"    #[ORM\\Column(\n    options: [\n        'default' => false,\n    ]\n)]\nprivate bool $vendable = false;",
"    #[ORM\\Column(\n    options: [\n        'default' => true,\n    ]\n)]\nprivate bool $vendable = true;",
    "1) Articles : vendable = true par defaut",
))

resultats.append(creer_fichier(
    "migrations/Version20260819160000.php",
'<?php\n\ndeclare(strict_types=1);\n\nnamespace DoctrineMigrations;\n\nuse Doctrine\\DBAL\\Schema\\Schema;\nuse Doctrine\\Migrations\\AbstractMigration;\n\nfinal class Version20260819160000 extends AbstractMigration\n{\n    public function getDescription(): string\n    {\n        return "Corrige le defaut de articles.vendable (etait false, jamais coche par le formulaire de creation d\'un article) : passe a true, et met a jour les articles existants pour qu\'ils apparaissent dans la liste de selection d\'une commande/d\'un devis.";\n    }\n\n    public function up(Schema $schema): void\n    {\n        $this->addSql(\'ALTER TABLE articles ALTER vendable SET DEFAULT 1\');\n        $this->addSql(\'UPDATE articles SET vendable = 1 WHERE vendable = 0\');\n    }\n\n    public function down(Schema $schema): void\n    {\n        $this->addSql(\'ALTER TABLE articles ALTER vendable SET DEFAULT 0\');\n    }\n}\n',
    "2) Cree la migration (corrige les articles existants)",
))


echecs = resultats.count(False)

print()
if echecs:
    print(f"Termine avec {echecs} erreur(s). Voir les [ERREUR] ci-dessus.")
    sys.exit(1)
else:
    print("Termine sans erreur. Lance maintenant : php bin/console doctrine:migrations:migrate")
