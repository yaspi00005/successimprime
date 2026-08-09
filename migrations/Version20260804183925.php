<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260804183925 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE paiements DROP FOREIGN KEY `FK_E1B02E1282EA2E54`');
        $this->addSql('ALTER TABLE paiements ADD CONSTRAINT FK_E1B02E12A11E8C5A FOREIGN KEY (compte_tresorerie_id) REFERENCES compte_tresorerie (id) ON DELETE RESTRICT');
        $this->addSql('ALTER TABLE paiements ADD CONSTRAINT FK_E1B02E126AF12ED9 FOREIGN KEY (valide_par_id) REFERENCES `user` (id) ON DELETE SET NULL');
        $this->addSql('ALTER TABLE paiements ADD CONSTRAINT FK_E1B02E12F376B95 FOREIGN KEY (annule_par_id) REFERENCES `user` (id) ON DELETE SET NULL');
        $this->addSql('DROP INDEX idx_e1b02e1282ea2e54 ON paiements');
        $this->addSql('CREATE INDEX idx_paiement_commande ON paiements (commande_id)');
        $this->addSql('ALTER TABLE paiements ADD CONSTRAINT `FK_E1B02E1282EA2E54` FOREIGN KEY (commande_id) REFERENCES commandes (id) ON DELETE CASCADE');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE paiements DROP FOREIGN KEY FK_E1B02E12A11E8C5A');
        $this->addSql('ALTER TABLE paiements DROP FOREIGN KEY FK_E1B02E126AF12ED9');
        $this->addSql('ALTER TABLE paiements DROP FOREIGN KEY FK_E1B02E12F376B95');
        $this->addSql('ALTER TABLE paiements DROP FOREIGN KEY FK_E1B02E1282EA2E54');
        $this->addSql('DROP INDEX idx_paiement_commande ON paiements');
        $this->addSql('CREATE INDEX IDX_E1B02E1282EA2E54 ON paiements (commande_id)');
        $this->addSql('ALTER TABLE paiements ADD CONSTRAINT FK_E1B02E1282EA2E54 FOREIGN KEY (commande_id) REFERENCES commandes (id) ON DELETE CASCADE');
    }
}
