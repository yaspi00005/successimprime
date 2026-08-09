<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260727225358 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('CREATE TABLE commande_detail_fichier (id INT AUTO_INCREMENT NOT NULL, nom_original VARCHAR(255) NOT NULL, nom_stockage VARCHAR(255) NOT NULL, type_mime VARCHAR(100) NOT NULL, taille INT NOT NULL, statut VARCHAR(30) NOT NULL, cree_le DATETIME NOT NULL, commande_detail_id INT NOT NULL, INDEX IDX_39E2DA10C8DC59F9 (commande_detail_id), PRIMARY KEY (id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('ALTER TABLE commande_detail_fichier ADD CONSTRAINT FK_39E2DA10C8DC59F9 FOREIGN KEY (commande_detail_id) REFERENCES commandes_details (id) ON DELETE CASCADE');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE commande_detail_fichier DROP FOREIGN KEY FK_39E2DA10C8DC59F9');
        $this->addSql('DROP TABLE commande_detail_fichier');
    }
}
