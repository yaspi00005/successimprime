<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260806231532 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE ordre_production ADD quantite_produite INT DEFAULT 0 NOT NULL, ADD quantite_rebut INT DEFAULT 0 NOT NULL, ADD observation_fin LONGTEXT DEFAULT NULL, ADD machine_id INT DEFAULT NULL, ADD termine_par_id INT DEFAULT NULL');
        $this->addSql('ALTER TABLE ordre_production ADD CONSTRAINT FK_D1C3E844F6B75B26 FOREIGN KEY (machine_id) REFERENCES machines (id) ON DELETE SET NULL');
        $this->addSql('ALTER TABLE ordre_production ADD CONSTRAINT FK_D1C3E84461168D84 FOREIGN KEY (termine_par_id) REFERENCES `user` (id) ON DELETE SET NULL');
        $this->addSql('CREATE INDEX IDX_D1C3E844F6B75B26 ON ordre_production (machine_id)');
        $this->addSql('CREATE INDEX IDX_D1C3E84461168D84 ON ordre_production (termine_par_id)');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE ordre_production DROP FOREIGN KEY FK_D1C3E844F6B75B26');
        $this->addSql('ALTER TABLE ordre_production DROP FOREIGN KEY FK_D1C3E84461168D84');
        $this->addSql('DROP INDEX IDX_D1C3E844F6B75B26 ON ordre_production');
        $this->addSql('DROP INDEX IDX_D1C3E84461168D84 ON ordre_production');
        $this->addSql('ALTER TABLE ordre_production DROP quantite_produite, DROP quantite_rebut, DROP observation_fin, DROP machine_id, DROP termine_par_id');
    }
}
