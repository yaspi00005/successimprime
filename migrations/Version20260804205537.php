<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260804205537 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE mouvement_tresorerie DROP FOREIGN KEY `FK_516E74682A4C4478`');
        $this->addSql('ALTER TABLE mouvement_tresorerie DROP FOREIGN KEY `FK_516E7468A11E8C5A`');
        $this->addSql('DROP INDEX IDX_516E7468A11E8C5A ON mouvement_tresorerie');
        $this->addSql('DROP INDEX idx_mouvement_compte_date ON mouvement_tresorerie');
        $this->addSql('ALTER TABLE mouvement_tresorerie ADD devise VARCHAR(10) DEFAULT \'XOF\' NOT NULL, ADD description LONGTEXT DEFAULT NULL, ADD date_operation DATETIME NOT NULL, ADD compte_source_id INT DEFAULT NULL, ADD compte_destination_id INT DEFAULT NULL, DROP sens, DROP solde_avant, DROP solde_apres, DROP observation, DROP motif_rejet, DROP compte_tresorerie_id, CHANGE statut statut VARCHAR(30) NOT NULL, CHANGE libelle libelle VARCHAR(255) NOT NULL, CHANGE origine type VARCHAR(30) NOT NULL, CHANGE groupe_operation mode_paiement VARCHAR(50) DEFAULT NULL');
        $this->addSql('ALTER TABLE mouvement_tresorerie ADD CONSTRAINT FK_516E74682A4C4478 FOREIGN KEY (paiement_id) REFERENCES paiements (id) ON DELETE SET NULL');
        $this->addSql('ALTER TABLE mouvement_tresorerie ADD CONSTRAINT FK_516E746856B22253 FOREIGN KEY (compte_source_id) REFERENCES compte_tresorerie (id) ON DELETE RESTRICT');
        $this->addSql('ALTER TABLE mouvement_tresorerie ADD CONSTRAINT FK_516E74684105B733 FOREIGN KEY (compte_destination_id) REFERENCES compte_tresorerie (id) ON DELETE RESTRICT');
        $this->addSql('CREATE INDEX IDX_516E746856B22253 ON mouvement_tresorerie (compte_source_id)');
        $this->addSql('CREATE INDEX IDX_516E74684105B733 ON mouvement_tresorerie (compte_destination_id)');
        $this->addSql('CREATE INDEX idx_mouvement_type ON mouvement_tresorerie (type)');
        $this->addSql('CREATE INDEX idx_mouvement_date ON mouvement_tresorerie (date_operation)');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE mouvement_tresorerie DROP FOREIGN KEY FK_516E74682A4C4478');
        $this->addSql('ALTER TABLE mouvement_tresorerie DROP FOREIGN KEY FK_516E746856B22253');
        $this->addSql('ALTER TABLE mouvement_tresorerie DROP FOREIGN KEY FK_516E74684105B733');
        $this->addSql('DROP INDEX IDX_516E746856B22253 ON mouvement_tresorerie');
        $this->addSql('DROP INDEX IDX_516E74684105B733 ON mouvement_tresorerie');
        $this->addSql('DROP INDEX idx_mouvement_type ON mouvement_tresorerie');
        $this->addSql('DROP INDEX idx_mouvement_date ON mouvement_tresorerie');
        $this->addSql('ALTER TABLE mouvement_tresorerie ADD sens VARCHAR(10) NOT NULL, ADD solde_avant INT DEFAULT NULL, ADD solde_apres INT DEFAULT NULL, ADD motif_rejet LONGTEXT DEFAULT NULL, ADD compte_tresorerie_id INT NOT NULL, DROP devise, DROP date_operation, DROP compte_source_id, DROP compte_destination_id, CHANGE libelle libelle VARCHAR(150) DEFAULT NULL, CHANGE statut statut VARCHAR(20) NOT NULL, CHANGE type origine VARCHAR(30) NOT NULL, CHANGE description observation LONGTEXT DEFAULT NULL, CHANGE mode_paiement groupe_operation VARCHAR(50) DEFAULT NULL');
        $this->addSql('ALTER TABLE mouvement_tresorerie ADD CONSTRAINT `FK_516E74682A4C4478` FOREIGN KEY (paiement_id) REFERENCES paiements (id)');
        $this->addSql('ALTER TABLE mouvement_tresorerie ADD CONSTRAINT `FK_516E7468A11E8C5A` FOREIGN KEY (compte_tresorerie_id) REFERENCES compte_tresorerie (id)');
        $this->addSql('CREATE INDEX IDX_516E7468A11E8C5A ON mouvement_tresorerie (compte_tresorerie_id)');
        $this->addSql('CREATE INDEX idx_mouvement_compte_date ON mouvement_tresorerie (compte_tresorerie_id, date_creation)');
    }
}
