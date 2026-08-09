<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260807201401 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE machines ADD numero_machine VARCHAR(50) DEFAULT NULL, ADD adresse_ip VARCHAR(45) DEFAULT NULL');
        $this->addSql('CREATE UNIQUE INDEX UNIQ_F1CE8DEDD351C125 ON machines (numero_machine)');
        $this->addSql('CREATE UNIQUE INDEX UNIQ_F1CE8DED573D0821 ON machines (adresse_ip)');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('DROP INDEX UNIQ_F1CE8DEDD351C125 ON machines');
        $this->addSql('DROP INDEX UNIQ_F1CE8DED573D0821 ON machines');
        $this->addSql('ALTER TABLE machines DROP numero_machine, DROP adresse_ip');
    }
}
