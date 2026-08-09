<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260806232906 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE ordre_production ADD transmis_le DATETIME DEFAULT NULL, ADD debut_prevu_le DATETIME DEFAULT NULL, ADD fin_prevue_le DATETIME DEFAULT NULL, ADD duree_estimee_minutes INT DEFAULT NULL, ADD duree_pause_minutes INT DEFAULT 0 NOT NULL, ADD pause_debute_le DATETIME DEFAULT NULL');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE ordre_production DROP transmis_le, DROP debut_prevu_le, DROP fin_prevue_le, DROP duree_estimee_minutes, DROP duree_pause_minutes, DROP pause_debute_le');
    }
}
