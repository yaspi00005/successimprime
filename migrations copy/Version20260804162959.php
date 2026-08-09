<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260804162959 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('CREATE TABLE mouvement_tresorerie (id INT AUTO_INCREMENT NOT NULL, reference VARCHAR(50) NOT NULL, sens VARCHAR(10) NOT NULL, origine VARCHAR(30) NOT NULL, montant INT NOT NULL, solde_avant INT DEFAULT NULL, solde_apres INT DEFAULT NULL, statut VARCHAR(20) NOT NULL, reference_externe VARCHAR(100) DEFAULT NULL, libelle VARCHAR(150) DEFAULT NULL, observation LONGTEXT DEFAULT NULL, groupe_operation VARCHAR(50) DEFAULT NULL, date_creation DATETIME NOT NULL, date_validation DATETIME DEFAULT NULL, date_annulation DATETIME DEFAULT NULL, motif_rejet LONGTEXT DEFAULT NULL, motif_annulation LONGTEXT DEFAULT NULL, compte_tresorerie_id INT NOT NULL, UNIQUE INDEX UNIQ_516E7468AEA34913 (reference), INDEX IDX_516E7468A11E8C5A (compte_tresorerie_id), INDEX idx_mouvement_compte_date (compte_tresorerie_id, date_creation), INDEX idx_mouvement_statut (statut), PRIMARY KEY (id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('ALTER TABLE mouvement_tresorerie ADD CONSTRAINT FK_516E7468A11E8C5A FOREIGN KEY (compte_tresorerie_id) REFERENCES compte_tresorerie (id) ON DELETE RESTRICT');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE mouvement_tresorerie DROP FOREIGN KEY FK_516E7468A11E8C5A');
        $this->addSql('DROP TABLE mouvement_tresorerie');
    }
}
