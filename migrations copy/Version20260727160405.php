<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260727160405 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE commandes_details ADD produit_configuration_id INT DEFAULT NULL');
        $this->addSql('ALTER TABLE commandes_details ADD CONSTRAINT FK_B48B83DA806A5250 FOREIGN KEY (produit_configuration_id) REFERENCES produit_configuration (id) ON DELETE SET NULL');
        $this->addSql('CREATE INDEX IDX_B48B83DA806A5250 ON commandes_details (produit_configuration_id)');
        $this->addSql('ALTER TABLE produits CHANGE publie publie TINYINT DEFAULT 1 NOT NULL, CHANGE ordre ordre INT DEFAULT 10 NOT NULL, CHANGE personnalisable personnalisable TINYINT DEFAULT 1 NOT NULL, CHANGE actif actif TINYINT DEFAULT 1 NOT NULL');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE commandes_details DROP FOREIGN KEY FK_B48B83DA806A5250');
        $this->addSql('DROP INDEX IDX_B48B83DA806A5250 ON commandes_details');
        $this->addSql('ALTER TABLE commandes_details DROP produit_configuration_id');
        $this->addSql('ALTER TABLE produits CHANGE publie publie TINYINT NOT NULL, CHANGE ordre ordre INT NOT NULL, CHANGE personnalisable personnalisable TINYINT NOT NULL, CHANGE actif actif TINYINT NOT NULL');
    }
}
