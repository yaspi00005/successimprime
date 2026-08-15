<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

final class Version20260815120000 extends AbstractMigration
{
    public function getDescription(): string
    {
        return 'Ajoute le module Achats (fournisseurs, achats, achat_detail) et transforme articles.fournisseur en relation.';
    }

    public function up(Schema $schema): void
    {
        /*
         * ========================================================
         * FOURNISSEURS
         * ========================================================
         *
         * La table n'existait pas encore : l'entité Fournisseurs
         * était présente dans le code mais jamais migrée.
         */
        $this->addSql(
            'CREATE TABLE fournisseurs (
                id INT AUTO_INCREMENT NOT NULL,
                nom VARCHAR(255) NOT NULL,
                telephone INT DEFAULT NULL,
                email VARCHAR(255) DEFAULT NULL,
                adresse LONGTEXT DEFAULT NULL,
                actif TINYINT(1) DEFAULT 1 NOT NULL,
                PRIMARY KEY (id)
            ) DEFAULT CHARACTER SET utf8mb4'
        );

        /*
         * ========================================================
         * ACHATS (en-tête)
         * ========================================================
         */
        $this->addSql(
            'CREATE TABLE achats (
                id INT AUTO_INCREMENT NOT NULL,
                fournisseur_id INT NOT NULL,
                numero VARCHAR(50) DEFAULT NULL,
                statut VARCHAR(20) NOT NULL,
                date_demande DATETIME NOT NULL,
                date_reception DATETIME DEFAULT NULL,
                observation LONGTEXT DEFAULT NULL,
                total_ht INT DEFAULT 0 NOT NULL,
                tva INT DEFAULT 0 NOT NULL,
                total_ttc INT DEFAULT 0 NOT NULL,
                UNIQUE INDEX uniq_achat_numero (numero),
                INDEX idx_achats_fournisseur (fournisseur_id),
                PRIMARY KEY (id)
            ) DEFAULT CHARACTER SET utf8mb4'
        );

        $this->addSql(
            'ALTER TABLE achats
             ADD CONSTRAINT fk_achats_fournisseur
             FOREIGN KEY (fournisseur_id) REFERENCES fournisseurs (id)'
        );

        /*
         * ========================================================
         * ACHAT_DETAIL (lignes)
         * ========================================================
         */
        $this->addSql(
            'CREATE TABLE achat_detail (
                id INT AUTO_INCREMENT NOT NULL,
                achat_id INT NOT NULL,
                article_id INT NOT NULL,
                quantite INT NOT NULL,
                prix_unitaire INT NOT NULL,
                total_ht INT DEFAULT 0 NOT NULL,
                INDEX idx_achat_detail_achat (achat_id),
                INDEX idx_achat_detail_article (article_id),
                PRIMARY KEY (id)
            ) DEFAULT CHARACTER SET utf8mb4'
        );

        $this->addSql(
            'ALTER TABLE achat_detail
             ADD CONSTRAINT fk_achat_detail_achat
             FOREIGN KEY (achat_id) REFERENCES achats (id) ON DELETE CASCADE'
        );

        $this->addSql(
            'ALTER TABLE achat_detail
             ADD CONSTRAINT fk_achat_detail_article
             FOREIGN KEY (article_id) REFERENCES articles (id)'
        );

        /*
         * ========================================================
         * ARTICLES.FOURNISSEUR : TEXTE LIBRE -> RELATION
         * ========================================================
         */
        $this->addSql(
            'ALTER TABLE articles ADD fournisseur_id INT DEFAULT NULL'
        );

        /*
         * Crée une fiche Fournisseurs pour chaque nom déjà saisi
         * en texte libre sur un article, sans doublon.
         */
        $this->addSql(
            "INSERT INTO fournisseurs (nom, actif)
             SELECT DISTINCT TRIM(a.fournisseur), 1
             FROM articles a
             WHERE a.fournisseur IS NOT NULL
               AND TRIM(a.fournisseur) <> ''
               AND NOT EXISTS (
                   SELECT 1 FROM fournisseurs f
                   WHERE f.nom = TRIM(a.fournisseur)
               )"
        );

        $this->addSql(
            "UPDATE articles a
             JOIN fournisseurs f ON f.nom = TRIM(a.fournisseur)
             SET a.fournisseur_id = f.id
             WHERE a.fournisseur IS NOT NULL
               AND TRIM(a.fournisseur) <> ''"
        );

        $this->addSql(
            'ALTER TABLE articles
             ADD CONSTRAINT fk_articles_fournisseur
             FOREIGN KEY (fournisseur_id) REFERENCES fournisseurs (id)
             ON DELETE SET NULL'
        );

        $this->addSql(
            'CREATE INDEX idx_articles_fournisseur ON articles (fournisseur_id)'
        );

        $this->addSql(
            'ALTER TABLE articles DROP COLUMN fournisseur'
        );
    }

    public function down(Schema $schema): void
    {
        $this->addSql(
            'ALTER TABLE articles ADD fournisseur VARCHAR(100) DEFAULT NULL'
        );

        $this->addSql(
            'UPDATE articles a
             JOIN fournisseurs f ON f.id = a.fournisseur_id
             SET a.fournisseur = f.nom'
        );

        $this->addSql(
            'ALTER TABLE articles DROP FOREIGN KEY fk_articles_fournisseur'
        );

        $this->addSql(
            'DROP INDEX idx_articles_fournisseur ON articles'
        );

        $this->addSql(
            'ALTER TABLE articles DROP COLUMN fournisseur_id'
        );

        $this->addSql(
            'ALTER TABLE achat_detail DROP FOREIGN KEY fk_achat_detail_achat'
        );

        $this->addSql(
            'ALTER TABLE achat_detail DROP FOREIGN KEY fk_achat_detail_article'
        );

        $this->addSql('DROP TABLE achat_detail');

        $this->addSql(
            'ALTER TABLE achats DROP FOREIGN KEY fk_achats_fournisseur'
        );

        $this->addSql('DROP TABLE achats');

        $this->addSql('DROP TABLE fournisseurs');
    }
}
