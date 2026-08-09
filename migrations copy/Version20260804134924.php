<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260804134924 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE devis ADD commande_id INT DEFAULT NULL, DROP statut_paiement');
        $this->addSql('ALTER TABLE devis ADD CONSTRAINT FK_8B27C52B82EA2E54 FOREIGN KEY (commande_id) REFERENCES commandes (id) ON DELETE SET NULL');
        $this->addSql('CREATE UNIQUE INDEX UNIQ_8B27C52B82EA2E54 ON devis (commande_id)');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE devis DROP FOREIGN KEY FK_8B27C52B82EA2E54');
        $this->addSql('DROP INDEX UNIQ_8B27C52B82EA2E54 ON devis');
        $this->addSql('ALTER TABLE devis ADD statut_paiement VARCHAR(20) DEFAULT \'impayee\' NOT NULL, DROP commande_id');
    }
}
