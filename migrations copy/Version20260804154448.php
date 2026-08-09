<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260804154448 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE commandes_details ADD type_ligne VARCHAR(30) DEFAULT \'produit\' NOT NULL, ADD mode_saisie VARCHAR(30) DEFAULT \'automatique\' NOT NULL');
        $this->addSql('DROP INDEX uniq_devis_numero ON devis');
        $this->addSql('CREATE UNIQUE INDEX UNIQ_8B27C52BF55AE19E ON devis (numero)');
        $this->addSql('ALTER TABLE devis_details ADD type_ligne VARCHAR(30) DEFAULT \'produit\' NOT NULL, ADD mode_saisie VARCHAR(30) DEFAULT \'automatique\' NOT NULL');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE commandes_details DROP type_ligne, DROP mode_saisie');
        $this->addSql('DROP INDEX uniq_8b27c52bf55ae19e ON devis');
        $this->addSql('CREATE UNIQUE INDEX uniq_devis_numero ON devis (numero)');
        $this->addSql('ALTER TABLE devis_details DROP type_ligne, DROP mode_saisie');
    }
}
