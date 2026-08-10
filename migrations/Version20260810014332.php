<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260810014332 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE articles ADD description LONGTEXT DEFAULT NULL, ADD actif TINYINT DEFAULT 1 NOT NULL, CHANGE reference reference VARCHAR(100) NOT NULL, CHANGE categorie categorie VARCHAR(100) DEFAULT NULL, CHANGE stock stock NUMERIC(14, 3) DEFAULT \'0.000\' NOT NULL, CHANGE stock_min stock_min NUMERIC(14, 3) DEFAULT \'0.000\' NOT NULL, CHANGE prix_achat prix_achat INT DEFAULT NULL, CHANGE prix_vente prix_vente INT DEFAULT NULL, CHANGE fournisseur fournisseur VARCHAR(100) DEFAULT NULL');
        $this->addSql('CREATE UNIQUE INDEX uniq_article_reference ON articles (reference)');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('DROP INDEX uniq_article_reference ON articles');
        $this->addSql('ALTER TABLE articles DROP description, DROP actif, CHANGE reference reference VARCHAR(255) NOT NULL, CHANGE categorie categorie VARCHAR(100) NOT NULL, CHANGE stock stock INT NOT NULL, CHANGE stock_min stock_min VARCHAR(255) NOT NULL, CHANGE prix_achat prix_achat INT NOT NULL, CHANGE prix_vente prix_vente INT NOT NULL, CHANGE fournisseur fournisseur VARCHAR(50) NOT NULL');
    }
}
