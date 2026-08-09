<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260729203219 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE clients CHANGE raison_sociale raison_sociale VARCHAR(100) DEFAULT NULL, CHANGE telephone telephone VARCHAR(30) NOT NULL, CHANGE email email VARCHAR(255) DEFAULT NULL, CHANGE adresse adresse VARCHAR(255) DEFAULT NULL, CHANGE ville ville VARCHAR(100) DEFAULT NULL, CHANGE nif nif VARCHAR(30) DEFAULT NULL, CHANGE rccm rccm VARCHAR(50) DEFAULT NULL, CHANGE plafond_credit plafond_credit INT DEFAULT NULL, CHANGE observation observation LONGTEXT DEFAULT NULL');
        $this->addSql('CREATE UNIQUE INDEX UNIQ_C82E7477153098 ON clients (code)');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('DROP INDEX UNIQ_C82E7477153098 ON clients');
        $this->addSql('ALTER TABLE clients CHANGE raison_sociale raison_sociale VARCHAR(100) NOT NULL, CHANGE telephone telephone VARCHAR(30) DEFAULT NULL, CHANGE email email VARCHAR(255) NOT NULL, CHANGE adresse adresse VARCHAR(255) NOT NULL, CHANGE ville ville VARCHAR(100) NOT NULL, CHANGE nif nif VARCHAR(30) NOT NULL, CHANGE rccm rccm VARCHAR(50) NOT NULL, CHANGE plafond_credit plafond_credit VARCHAR(30) DEFAULT NULL, CHANGE observation observation LONGTEXT NOT NULL');
    }
}
