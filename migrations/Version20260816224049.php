<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260816224049 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE commandes_details CHANGE remise remise NUMERIC(5, 2) DEFAULT 0 NOT NULL');
        $this->addSql('DROP INDEX IDX_journal_activite_created_at ON journal_activite');
        $this->addSql('DROP INDEX IDX_journal_activite_entite ON journal_activite');
        $this->addSql('ALTER TABLE journal_activite DROP FOREIGN KEY `FK_journal_activite_utilisateur`');
        $this->addSql('DROP INDEX idx_journal_activite_utilisateur ON journal_activite');
        $this->addSql('CREATE INDEX IDX_68C5F8ACFB88E14F ON journal_activite (utilisateur_id)');
        $this->addSql('ALTER TABLE journal_activite ADD CONSTRAINT `FK_journal_activite_utilisateur` FOREIGN KEY (utilisateur_id) REFERENCES user (id) ON DELETE SET NULL');
        $this->addSql('ALTER TABLE reclamations DROP FOREIGN KEY `FK_reclamation_agent`');
        $this->addSql('ALTER TABLE reclamations DROP FOREIGN KEY `FK_reclamation_mouvement`');
        $this->addSql('ALTER TABLE reclamations DROP FOREIGN KEY `FK_reclamation_paye_par`');
        $this->addSql('ALTER TABLE reclamations DROP FOREIGN KEY `FK_reclamation_refuse_par`');
        $this->addSql('ALTER TABLE reclamations DROP FOREIGN KEY `FK_reclamation_valide_par`');
        $this->addSql('DROP INDEX uniq_reclamation_reference ON reclamations');
        $this->addSql('CREATE UNIQUE INDEX UNIQ_1CAD6B76AEA34913 ON reclamations (reference)');
        $this->addSql('DROP INDEX idx_reclamation_agent ON reclamations');
        $this->addSql('CREATE INDEX IDX_1CAD6B763414710B ON reclamations (agent_id)');
        $this->addSql('DROP INDEX idx_reclamation_valide_par ON reclamations');
        $this->addSql('CREATE INDEX IDX_1CAD6B766AF12ED9 ON reclamations (valide_par_id)');
        $this->addSql('DROP INDEX idx_reclamation_refuse_par ON reclamations');
        $this->addSql('CREATE INDEX IDX_1CAD6B76BED2696A ON reclamations (refuse_par_id)');
        $this->addSql('DROP INDEX idx_reclamation_paye_par ON reclamations');
        $this->addSql('CREATE INDEX IDX_1CAD6B764D50E957 ON reclamations (paye_par_id)');
        $this->addSql('DROP INDEX uniq_reclamation_mouvement ON reclamations');
        $this->addSql('CREATE UNIQUE INDEX UNIQ_1CAD6B76C1DCAF54 ON reclamations (mouvement_tresorerie_id)');
        $this->addSql('ALTER TABLE reclamations ADD CONSTRAINT `FK_reclamation_agent` FOREIGN KEY (agent_id) REFERENCES user (id)');
        $this->addSql('ALTER TABLE reclamations ADD CONSTRAINT `FK_reclamation_mouvement` FOREIGN KEY (mouvement_tresorerie_id) REFERENCES mouvement_tresorerie (id) ON DELETE SET NULL');
        $this->addSql('ALTER TABLE reclamations ADD CONSTRAINT `FK_reclamation_paye_par` FOREIGN KEY (paye_par_id) REFERENCES user (id) ON DELETE SET NULL');
        $this->addSql('ALTER TABLE reclamations ADD CONSTRAINT `FK_reclamation_refuse_par` FOREIGN KEY (refuse_par_id) REFERENCES user (id) ON DELETE SET NULL');
        $this->addSql('ALTER TABLE reclamations ADD CONSTRAINT `FK_reclamation_valide_par` FOREIGN KEY (valide_par_id) REFERENCES user (id) ON DELETE SET NULL');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE commandes_details CHANGE remise remise NUMERIC(5, 2) DEFAULT \'0.00\' NOT NULL');
        $this->addSql('ALTER TABLE journal_activite DROP FOREIGN KEY FK_68C5F8ACFB88E14F');
        $this->addSql('CREATE INDEX IDX_journal_activite_created_at ON journal_activite (created_at)');
        $this->addSql('CREATE INDEX IDX_journal_activite_entite ON journal_activite (entite, entite_id)');
        $this->addSql('DROP INDEX idx_68c5f8acfb88e14f ON journal_activite');
        $this->addSql('CREATE INDEX IDX_journal_activite_utilisateur ON journal_activite (utilisateur_id)');
        $this->addSql('ALTER TABLE journal_activite ADD CONSTRAINT FK_68C5F8ACFB88E14F FOREIGN KEY (utilisateur_id) REFERENCES `user` (id) ON DELETE SET NULL');
        $this->addSql('ALTER TABLE reclamations DROP FOREIGN KEY FK_1CAD6B763414710B');
        $this->addSql('ALTER TABLE reclamations DROP FOREIGN KEY FK_1CAD6B766AF12ED9');
        $this->addSql('ALTER TABLE reclamations DROP FOREIGN KEY FK_1CAD6B76BED2696A');
        $this->addSql('ALTER TABLE reclamations DROP FOREIGN KEY FK_1CAD6B764D50E957');
        $this->addSql('ALTER TABLE reclamations DROP FOREIGN KEY FK_1CAD6B76C1DCAF54');
        $this->addSql('DROP INDEX uniq_1cad6b76aea34913 ON reclamations');
        $this->addSql('CREATE UNIQUE INDEX UNIQ_reclamation_reference ON reclamations (reference)');
        $this->addSql('DROP INDEX idx_1cad6b766af12ed9 ON reclamations');
        $this->addSql('CREATE INDEX IDX_reclamation_valide_par ON reclamations (valide_par_id)');
        $this->addSql('DROP INDEX uniq_1cad6b76c1dcaf54 ON reclamations');
        $this->addSql('CREATE UNIQUE INDEX UNIQ_reclamation_mouvement ON reclamations (mouvement_tresorerie_id)');
        $this->addSql('DROP INDEX idx_1cad6b76bed2696a ON reclamations');
        $this->addSql('CREATE INDEX IDX_reclamation_refuse_par ON reclamations (refuse_par_id)');
        $this->addSql('DROP INDEX idx_1cad6b764d50e957 ON reclamations');
        $this->addSql('CREATE INDEX IDX_reclamation_paye_par ON reclamations (paye_par_id)');
        $this->addSql('DROP INDEX idx_1cad6b763414710b ON reclamations');
        $this->addSql('CREATE INDEX IDX_reclamation_agent ON reclamations (agent_id)');
        $this->addSql('ALTER TABLE reclamations ADD CONSTRAINT FK_1CAD6B763414710B FOREIGN KEY (agent_id) REFERENCES `user` (id) ON DELETE RESTRICT');
        $this->addSql('ALTER TABLE reclamations ADD CONSTRAINT FK_1CAD6B766AF12ED9 FOREIGN KEY (valide_par_id) REFERENCES `user` (id) ON DELETE SET NULL');
        $this->addSql('ALTER TABLE reclamations ADD CONSTRAINT FK_1CAD6B76BED2696A FOREIGN KEY (refuse_par_id) REFERENCES `user` (id) ON DELETE SET NULL');
        $this->addSql('ALTER TABLE reclamations ADD CONSTRAINT FK_1CAD6B764D50E957 FOREIGN KEY (paye_par_id) REFERENCES `user` (id) ON DELETE SET NULL');
        $this->addSql('ALTER TABLE reclamations ADD CONSTRAINT FK_1CAD6B76C1DCAF54 FOREIGN KEY (mouvement_tresorerie_id) REFERENCES mouvement_tresorerie (id) ON DELETE SET NULL');
    }
}
