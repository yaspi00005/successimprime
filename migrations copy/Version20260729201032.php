<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260729201032 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE clients CHANGE type_client type_client VARCHAR(10) DEFAULT \'B2C\' NOT NULL');
        $this->addSql('ALTER TABLE commandes_details ADD mode_configuration VARCHAR(20) DEFAULT \'manuel\' NOT NULL, CHANGE quantites quantite INT NOT NULL');
        $this->addSql('ALTER TABLE produit_configuration ADD prix_b2_b INT DEFAULT NULL');
        $this->addSql('ALTER TABLE produits ADD prix_b2_b DOUBLE PRECISION DEFAULT NULL');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE clients CHANGE type_client type_client VARCHAR(50) NOT NULL');
        $this->addSql('ALTER TABLE commandes_details DROP mode_configuration, CHANGE quantite quantites INT NOT NULL');
        $this->addSql('ALTER TABLE produits DROP prix_b2_b');
        $this->addSql('ALTER TABLE produit_configuration DROP prix_b2_b');
    }
}
