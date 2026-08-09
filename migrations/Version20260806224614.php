<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260806224614 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE etiquette ADD commande_id INT DEFAULT NULL, ADD commande_detail_id INT DEFAULT NULL');
        $this->addSql('ALTER TABLE etiquette ADD CONSTRAINT FK_1E0E195A82EA2E54 FOREIGN KEY (commande_id) REFERENCES commandes (id) ON DELETE SET NULL');
        $this->addSql('ALTER TABLE etiquette ADD CONSTRAINT FK_1E0E195AC8DC59F9 FOREIGN KEY (commande_detail_id) REFERENCES commandes_details (id) ON DELETE SET NULL');
        $this->addSql('CREATE INDEX idx_etiquette_commande ON etiquette (commande_id)');
        $this->addSql('CREATE INDEX idx_etiquette_commande_detail ON etiquette (commande_detail_id)');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE etiquette DROP FOREIGN KEY FK_1E0E195A82EA2E54');
        $this->addSql('ALTER TABLE etiquette DROP FOREIGN KEY FK_1E0E195AC8DC59F9');
        $this->addSql('DROP INDEX idx_etiquette_commande ON etiquette');
        $this->addSql('DROP INDEX idx_etiquette_commande_detail ON etiquette');
        $this->addSql('ALTER TABLE etiquette DROP commande_id, DROP commande_detail_id');
    }
}
