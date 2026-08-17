<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

final class Version20260816140000 extends AbstractMigration
{
    public function getDescription(): string
    {
        return "Ajoute la table reclamations (demandes de remboursement des agents : soumission, validation/refus admin, paiement caisse relie a un MouvementTresorerie).";
    }

    public function up(Schema $schema): void
    {
        $this->addSql('CREATE TABLE reclamations (id INT AUTO_INCREMENT NOT NULL, reference VARCHAR(50) NOT NULL, motif LONGTEXT NOT NULL, montant INT NOT NULL, justificatif VARCHAR(255) DEFAULT NULL, statut VARCHAR(30) NOT NULL, date_creation DATETIME NOT NULL, date_validation DATETIME DEFAULT NULL, motif_refus LONGTEXT DEFAULT NULL, date_refus DATETIME DEFAULT NULL, date_paiement DATETIME DEFAULT NULL, agent_id INT NOT NULL, valide_par_id INT DEFAULT NULL, refuse_par_id INT DEFAULT NULL, paye_par_id INT DEFAULT NULL, mouvement_tresorerie_id INT DEFAULT NULL, UNIQUE INDEX UNIQ_reclamation_reference (reference), UNIQUE INDEX UNIQ_reclamation_mouvement (mouvement_tresorerie_id), INDEX idx_reclamation_statut (statut), INDEX IDX_reclamation_agent (agent_id), INDEX IDX_reclamation_valide_par (valide_par_id), INDEX IDX_reclamation_refuse_par (refuse_par_id), INDEX IDX_reclamation_paye_par (paye_par_id), PRIMARY KEY (id)) DEFAULT CHARACTER SET utf8mb4');

        $this->addSql('ALTER TABLE reclamations ADD CONSTRAINT FK_reclamation_agent FOREIGN KEY (agent_id) REFERENCES `user` (id)');
        $this->addSql('ALTER TABLE reclamations ADD CONSTRAINT FK_reclamation_valide_par FOREIGN KEY (valide_par_id) REFERENCES `user` (id) ON DELETE SET NULL');
        $this->addSql('ALTER TABLE reclamations ADD CONSTRAINT FK_reclamation_refuse_par FOREIGN KEY (refuse_par_id) REFERENCES `user` (id) ON DELETE SET NULL');
        $this->addSql('ALTER TABLE reclamations ADD CONSTRAINT FK_reclamation_paye_par FOREIGN KEY (paye_par_id) REFERENCES `user` (id) ON DELETE SET NULL');
        $this->addSql('ALTER TABLE reclamations ADD CONSTRAINT FK_reclamation_mouvement FOREIGN KEY (mouvement_tresorerie_id) REFERENCES mouvement_tresorerie (id) ON DELETE SET NULL');
    }

    public function down(Schema $schema): void
    {
        $this->addSql('ALTER TABLE reclamations DROP FOREIGN KEY FK_reclamation_agent');
        $this->addSql('ALTER TABLE reclamations DROP FOREIGN KEY FK_reclamation_valide_par');
        $this->addSql('ALTER TABLE reclamations DROP FOREIGN KEY FK_reclamation_refuse_par');
        $this->addSql('ALTER TABLE reclamations DROP FOREIGN KEY FK_reclamation_paye_par');
        $this->addSql('ALTER TABLE reclamations DROP FOREIGN KEY FK_reclamation_mouvement');
        $this->addSql('DROP TABLE reclamations');
    }
}
