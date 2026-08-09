<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260726165053 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE categorie_produit ADD code VARCHAR(50) NOT NULL, ADD prix_base DOUBLE PRECISION DEFAULT NULL, ADD personnalisable TINYINT NOT NULL, ADD actif TINYINT NOT NULL');
        $this->addSql('CREATE UNIQUE INDEX UNIQ_7626428577153098 ON categorie_produit (code)');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('DROP INDEX UNIQ_7626428577153098 ON categorie_produit');
        $this->addSql('ALTER TABLE categorie_produit DROP code, DROP prix_base, DROP personnalisable, DROP actif');
    }
}
