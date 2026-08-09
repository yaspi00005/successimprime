<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260806212245 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('CREATE TABLE etiquette (id INT AUTO_INCREMENT NOT NULL, numero VARCHAR(50) NOT NULL, token VARCHAR(128) NOT NULL, fichier_qr VARCHAR(255) NOT NULL, statut VARCHAR(30) NOT NULL, cree_le DATETIME NOT NULL, imprime_le DATETIME DEFAULT NULL, associe_le DATETIME DEFAULT NULL, lot_id INT NOT NULL, associe_par_id INT DEFAULT NULL, UNIQUE INDEX UNIQ_1E0E195AF55AE19E (numero), UNIQUE INDEX UNIQ_1E0E195A5F37A13B (token), INDEX IDX_1E0E195AA8CBA5F7 (lot_id), INDEX IDX_1E0E195A276FAE2C (associe_par_id), INDEX idx_etiquette_statut (statut), PRIMARY KEY (id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('CREATE TABLE lot_etiquette (id INT AUTO_INCREMENT NOT NULL, numero VARCHAR(30) NOT NULL, quantite INT NOT NULL, prefixe VARCHAR(20) NOT NULL, dossier VARCHAR(255) NOT NULL, fichier_zip VARCHAR(255) DEFAULT NULL, statut VARCHAR(30) NOT NULL, cree_le DATETIME NOT NULL, termine_le DATETIME DEFAULT NULL, genere_par_id INT NOT NULL, UNIQUE INDEX UNIQ_3F18271EF55AE19E (numero), UNIQUE INDEX UNIQ_3F18271E3D48E037 (dossier), INDEX IDX_3F18271E9DEC084D (genere_par_id), PRIMARY KEY (id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('ALTER TABLE etiquette ADD CONSTRAINT FK_1E0E195AA8CBA5F7 FOREIGN KEY (lot_id) REFERENCES lot_etiquette (id) ON DELETE CASCADE');
        $this->addSql('ALTER TABLE etiquette ADD CONSTRAINT FK_1E0E195A276FAE2C FOREIGN KEY (associe_par_id) REFERENCES `user` (id) ON DELETE SET NULL');
        $this->addSql('ALTER TABLE lot_etiquette ADD CONSTRAINT FK_3F18271E9DEC084D FOREIGN KEY (genere_par_id) REFERENCES `user` (id) ON DELETE RESTRICT');
        $this->addSql('ALTER TABLE commandes ADD public_id BINARY(16) NOT NULL');
        $this->addSql('CREATE UNIQUE INDEX UNIQ_35D4282CB5B48B91 ON commandes (public_id)');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE etiquette DROP FOREIGN KEY FK_1E0E195AA8CBA5F7');
        $this->addSql('ALTER TABLE etiquette DROP FOREIGN KEY FK_1E0E195A276FAE2C');
        $this->addSql('ALTER TABLE lot_etiquette DROP FOREIGN KEY FK_3F18271E9DEC084D');
        $this->addSql('DROP TABLE etiquette');
        $this->addSql('DROP TABLE lot_etiquette');
        $this->addSql('DROP INDEX UNIQ_35D4282CB5B48B91 ON commandes');
        $this->addSql('ALTER TABLE commandes DROP public_id');
    }
}
