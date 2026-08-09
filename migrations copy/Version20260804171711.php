<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260804171711 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE devis_details DROP FOREIGN KEY `FK_E0C890D6F6B75B26`');
        $this->addSql('DROP INDEX IDX_E0C890D6F6B75B26 ON devis_details');
        $this->addSql('ALTER TABLE devis_details DROP machine_id');
        $this->addSql('ALTER TABLE mouvement_tresorerie ADD paiement_id INT DEFAULT NULL');
        $this->addSql('ALTER TABLE mouvement_tresorerie ADD CONSTRAINT FK_516E74682A4C4478 FOREIGN KEY (paiement_id) REFERENCES paiements (id) ON DELETE RESTRICT');
        $this->addSql('CREATE UNIQUE INDEX UNIQ_516E74682A4C4478 ON mouvement_tresorerie (paiement_id)');
        $this->addSql('ALTER TABLE paiements ADD CONSTRAINT FK_E1B02E12A11E8C5A FOREIGN KEY (compte_tresorerie_id) REFERENCES compte_tresorerie (id) ON DELETE RESTRICT');
        $this->addSql('ALTER TABLE paiements ADD CONSTRAINT FK_E1B02E126AF12ED9 FOREIGN KEY (valide_par_id) REFERENCES `user` (id) ON DELETE SET NULL');
        $this->addSql('ALTER TABLE paiements ADD CONSTRAINT FK_E1B02E12F376B95 FOREIGN KEY (annule_par_id) REFERENCES `user` (id) ON DELETE SET NULL');
        $this->addSql('CREATE INDEX IDX_E1B02E12A11E8C5A ON paiements (compte_tresorerie_id)');
        $this->addSql('CREATE INDEX IDX_E1B02E126AF12ED9 ON paiements (valide_par_id)');
        $this->addSql('CREATE INDEX IDX_E1B02E12F376B95 ON paiements (annule_par_id)');
        $this->addSql('CREATE INDEX idx_paiement_compte_statut ON paiements (compte_tresorerie_id, statut)');
        $this->addSql('DROP INDEX idx_e1b02e1282ea2e54 ON paiements');
        $this->addSql('CREATE INDEX idx_paiement_commande ON paiements (commande_id)');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE devis_details ADD machine_id INT DEFAULT NULL');
        $this->addSql('ALTER TABLE devis_details ADD CONSTRAINT `FK_E0C890D6F6B75B26` FOREIGN KEY (machine_id) REFERENCES machines (id) ON DELETE SET NULL');
        $this->addSql('CREATE INDEX IDX_E0C890D6F6B75B26 ON devis_details (machine_id)');
        $this->addSql('ALTER TABLE mouvement_tresorerie DROP FOREIGN KEY FK_516E74682A4C4478');
        $this->addSql('DROP INDEX UNIQ_516E74682A4C4478 ON mouvement_tresorerie');
        $this->addSql('ALTER TABLE mouvement_tresorerie DROP paiement_id');
        $this->addSql('ALTER TABLE paiements DROP FOREIGN KEY FK_E1B02E12A11E8C5A');
        $this->addSql('ALTER TABLE paiements DROP FOREIGN KEY FK_E1B02E126AF12ED9');
        $this->addSql('ALTER TABLE paiements DROP FOREIGN KEY FK_E1B02E12F376B95');
        $this->addSql('DROP INDEX IDX_E1B02E12A11E8C5A ON paiements');
        $this->addSql('DROP INDEX IDX_E1B02E126AF12ED9 ON paiements');
        $this->addSql('DROP INDEX IDX_E1B02E12F376B95 ON paiements');
        $this->addSql('DROP INDEX idx_paiement_compte_statut ON paiements');
        $this->addSql('DROP INDEX idx_paiement_commande ON paiements');
        $this->addSql('CREATE INDEX IDX_E1B02E1282EA2E54 ON paiements (commande_id)');
    }
}
