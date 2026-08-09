<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260807180650 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE ordre_production ADD numero_etiquette VARCHAR(50) DEFAULT NULL, ADD etiquette_affectee_le DATETIME DEFAULT NULL, ADD etiquette_affectee_par_id INT DEFAULT NULL');
        $this->addSql('ALTER TABLE ordre_production ADD CONSTRAINT FK_D1C3E8442A05A43E FOREIGN KEY (etiquette_affectee_par_id) REFERENCES `user` (id) ON DELETE SET NULL');
        $this->addSql('CREATE UNIQUE INDEX UNIQ_D1C3E844531D6FC5 ON ordre_production (numero_etiquette)');
        $this->addSql('CREATE INDEX IDX_D1C3E8442A05A43E ON ordre_production (etiquette_affectee_par_id)');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE ordre_production DROP FOREIGN KEY FK_D1C3E8442A05A43E');
        $this->addSql('DROP INDEX UNIQ_D1C3E844531D6FC5 ON ordre_production');
        $this->addSql('DROP INDEX IDX_D1C3E8442A05A43E ON ordre_production');
        $this->addSql('ALTER TABLE ordre_production DROP numero_etiquette, DROP etiquette_affectee_le, DROP etiquette_affectee_par_id');
    }
}
