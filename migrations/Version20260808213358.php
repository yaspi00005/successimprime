<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260808213358 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('CREATE TABLE bon_livraison (id INT AUTO_INCREMENT NOT NULL, numero VARCHAR(50) NOT NULL, cree_le DATETIME NOT NULL, valide_le DATETIME DEFAULT NULL, livre_le DATETIME DEFAULT NULL, statut VARCHAR(30) NOT NULL, nom_receptionnaire VARCHAR(255) DEFAULT NULL, telephone_receptionnaire VARCHAR(50) DEFAULT NULL, adresse_livraison VARCHAR(255) DEFAULT NULL, observation LONGTEXT DEFAULT NULL, commande_id INT NOT NULL, cree_par_id INT DEFAULT NULL, valide_par_id INT DEFAULT NULL, livre_par_id INT DEFAULT NULL, UNIQUE INDEX UNIQ_31A531A4F55AE19E (numero), INDEX IDX_31A531A482EA2E54 (commande_id), INDEX IDX_31A531A4FC29C013 (cree_par_id), INDEX IDX_31A531A46AF12ED9 (valide_par_id), INDEX IDX_31A531A4E2C6415F (livre_par_id), PRIMARY KEY (id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('CREATE TABLE bon_livraison_ligne (id INT AUTO_INCREMENT NOT NULL, designation VARCHAR(255) NOT NULL, quantite_commandee INT NOT NULL, quantite_livree INT NOT NULL, unite VARCHAR(50) DEFAULT NULL, observation VARCHAR(255) DEFAULT NULL, bon_livraison_id INT NOT NULL, commande_detail_id INT NOT NULL, INDEX IDX_9C189341D8D16068 (bon_livraison_id), INDEX IDX_9C189341C8DC59F9 (commande_detail_id), PRIMARY KEY (id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('ALTER TABLE bon_livraison ADD CONSTRAINT FK_31A531A482EA2E54 FOREIGN KEY (commande_id) REFERENCES commandes (id) ON DELETE CASCADE');
        $this->addSql('ALTER TABLE bon_livraison ADD CONSTRAINT FK_31A531A4FC29C013 FOREIGN KEY (cree_par_id) REFERENCES `user` (id) ON DELETE SET NULL');
        $this->addSql('ALTER TABLE bon_livraison ADD CONSTRAINT FK_31A531A46AF12ED9 FOREIGN KEY (valide_par_id) REFERENCES `user` (id) ON DELETE SET NULL');
        $this->addSql('ALTER TABLE bon_livraison ADD CONSTRAINT FK_31A531A4E2C6415F FOREIGN KEY (livre_par_id) REFERENCES `user` (id) ON DELETE SET NULL');
        $this->addSql('ALTER TABLE bon_livraison_ligne ADD CONSTRAINT FK_9C189341D8D16068 FOREIGN KEY (bon_livraison_id) REFERENCES bon_livraison (id) ON DELETE CASCADE');
        $this->addSql('ALTER TABLE bon_livraison_ligne ADD CONSTRAINT FK_9C189341C8DC59F9 FOREIGN KEY (commande_detail_id) REFERENCES commandes_details (id) ON DELETE RESTRICT');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE bon_livraison DROP FOREIGN KEY FK_31A531A482EA2E54');
        $this->addSql('ALTER TABLE bon_livraison DROP FOREIGN KEY FK_31A531A4FC29C013');
        $this->addSql('ALTER TABLE bon_livraison DROP FOREIGN KEY FK_31A531A46AF12ED9');
        $this->addSql('ALTER TABLE bon_livraison DROP FOREIGN KEY FK_31A531A4E2C6415F');
        $this->addSql('ALTER TABLE bon_livraison_ligne DROP FOREIGN KEY FK_9C189341D8D16068');
        $this->addSql('ALTER TABLE bon_livraison_ligne DROP FOREIGN KEY FK_9C189341C8DC59F9');
        $this->addSql('DROP TABLE bon_livraison');
        $this->addSql('DROP TABLE bon_livraison_ligne');
    }
}
