<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260804160638 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('CREATE TABLE compte_tresorerie (id INT AUTO_INCREMENT NOT NULL, code VARCHAR(50) NOT NULL, nom VARCHAR(150) NOT NULL, type VARCHAR(30) NOT NULL, nom_banque VARCHAR(150) DEFAULT NULL, numero_compte VARCHAR(100) DEFAULT NULL, titulaire_compte VARCHAR(150) DEFAULT NULL, solde_initial INT DEFAULT 0 NOT NULL, solde_actuel INT DEFAULT 0 NOT NULL, devise VARCHAR(10) DEFAULT \'XOF\' NOT NULL, autoriser_decouvert TINYINT DEFAULT 0 NOT NULL, actif TINYINT DEFAULT 1 NOT NULL, description LONGTEXT DEFAULT NULL, date_creation DATETIME NOT NULL, date_modification DATETIME DEFAULT NULL, UNIQUE INDEX UNIQ_E738ED0677153098 (code), PRIMARY KEY (id)) DEFAULT CHARACTER SET utf8mb4');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('DROP TABLE compte_tresorerie');
    }
}
