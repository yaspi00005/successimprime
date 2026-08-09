<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260730211252 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE produit_configuration DROP FOREIGN KEY `FK_8BBC0309D629F605`');
        $this->addSql('ALTER TABLE produit_configuration CHANGE format_id format_id INT DEFAULT NULL');
        $this->addSql('ALTER TABLE produit_configuration ADD CONSTRAINT FK_8BBC0309D629F605 FOREIGN KEY (format_id) REFERENCES format (id) ON DELETE SET NULL');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE produit_configuration DROP FOREIGN KEY FK_8BBC0309D629F605');
        $this->addSql('ALTER TABLE produit_configuration CHANGE format_id format_id INT NOT NULL');
        $this->addSql('ALTER TABLE produit_configuration ADD CONSTRAINT `FK_8BBC0309D629F605` FOREIGN KEY (format_id) REFERENCES format (id) ON DELETE CASCADE');
    }
}
