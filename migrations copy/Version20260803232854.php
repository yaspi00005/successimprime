<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260803232854 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE devis DROP FOREIGN KEY `FK_8B27C52B19EB6921`');
        $this->addSql('ALTER TABLE devis DROP FOREIGN KEY `FK_8B27C52B82EA2E54`');
        $this->addSql('DROP INDEX IDX_8B27C52B19EB6921 ON devis');
        $this->addSql('DROP INDEX UNIQ_8B27C52B82EA2E54 ON devis');
        $this->addSql('ALTER TABLE devis ADD date_devis DATETIME NOT NULL, ADD remise INT DEFAULT 0 NOT NULL, ADD tva INT DEFAULT 0 NOT NULL, ADD montant_apayer INT DEFAULT 0 NOT NULL, ADD deleted TINYINT DEFAULT 0 NOT NULL, ADD statut_paiement VARCHAR(20) DEFAULT \'impayee\' NOT NULL, ADD agents_id INT NOT NULL, DROP date_creation, DROP date_validite, DROP remise_pourcentage, DROP montant_remise, DROP taux_tva, DROP total_apres_remise, DROP montant_tva, DROP notes, DROP conditions_commerciales, DROP commande_id, CHANGE numero numero VARCHAR(50) DEFAULT NULL, CHANGE statut statut TINYINT DEFAULT 1 NOT NULL, CHANGE etat etat TINYINT DEFAULT 1 NOT NULL, CHANGE observation observation LONGTEXT DEFAULT NULL, CHANGE client_id clients_id INT NOT NULL');
        $this->addSql('ALTER TABLE devis ADD CONSTRAINT FK_8B27C52BAB014612 FOREIGN KEY (clients_id) REFERENCES clients (id)');
        $this->addSql('ALTER TABLE devis ADD CONSTRAINT FK_8B27C52B709770DC FOREIGN KEY (agents_id) REFERENCES `user` (id)');
        $this->addSql('CREATE INDEX IDX_8B27C52BAB014612 ON devis (clients_id)');
        $this->addSql('CREATE INDEX IDX_8B27C52B709770DC ON devis (agents_id)');
        $this->addSql('ALTER TABLE devis_detail_finition DROP FOREIGN KEY `FK_BE70DB30A0C197D7`');
        $this->addSql('ALTER TABLE devis_detail_finition ADD nom_finition VARCHAR(255) NOT NULL, ADD obligatoire TINYINT DEFAULT 0 NOT NULL, ADD finition_id INT NOT NULL, CHANGE configuration_finition_id configuration_finition_id INT DEFAULT NULL');
        $this->addSql('ALTER TABLE devis_detail_finition ADD CONSTRAINT FK_BE70DB30A0C197D7 FOREIGN KEY (configuration_finition_id) REFERENCES produit_configuration_finition (id) ON DELETE SET NULL');
        $this->addSql('ALTER TABLE devis_detail_finition ADD CONSTRAINT FK_BE70DB30CB56F5AF FOREIGN KEY (finition_id) REFERENCES finition (id) ON DELETE RESTRICT');
        $this->addSql('CREATE INDEX IDX_BE70DB30CB56F5AF ON devis_detail_finition (finition_id)');
        $this->addSql('ALTER TABLE devis_details DROP ordre');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE devis DROP FOREIGN KEY FK_8B27C52BAB014612');
        $this->addSql('ALTER TABLE devis DROP FOREIGN KEY FK_8B27C52B709770DC');
        $this->addSql('DROP INDEX IDX_8B27C52BAB014612 ON devis');
        $this->addSql('DROP INDEX IDX_8B27C52B709770DC ON devis');
        $this->addSql('ALTER TABLE devis ADD date_validite DATETIME NOT NULL, ADD remise_pourcentage INT DEFAULT 0 NOT NULL, ADD montant_remise INT DEFAULT 0 NOT NULL, ADD taux_tva INT DEFAULT 0 NOT NULL, ADD total_apres_remise INT DEFAULT 0 NOT NULL, ADD montant_tva INT DEFAULT 0 NOT NULL, ADD notes LONGTEXT DEFAULT NULL, ADD conditions_commerciales LONGTEXT DEFAULT NULL, ADD client_id INT NOT NULL, ADD commande_id INT DEFAULT NULL, DROP remise, DROP tva, DROP montant_apayer, DROP deleted, DROP statut_paiement, DROP clients_id, DROP agents_id, CHANGE numero numero VARCHAR(50) NOT NULL, CHANGE observation observation LONGTEXT NOT NULL, CHANGE statut statut VARCHAR(30) NOT NULL, CHANGE etat etat TINYINT NOT NULL, CHANGE date_devis date_creation DATETIME NOT NULL');
        $this->addSql('ALTER TABLE devis ADD CONSTRAINT `FK_8B27C52B19EB6921` FOREIGN KEY (client_id) REFERENCES clients (id)');
        $this->addSql('ALTER TABLE devis ADD CONSTRAINT `FK_8B27C52B82EA2E54` FOREIGN KEY (commande_id) REFERENCES commandes (id) ON DELETE SET NULL');
        $this->addSql('CREATE INDEX IDX_8B27C52B19EB6921 ON devis (client_id)');
        $this->addSql('CREATE UNIQUE INDEX UNIQ_8B27C52B82EA2E54 ON devis (commande_id)');
        $this->addSql('ALTER TABLE devis_details ADD ordre INT DEFAULT 0 NOT NULL');
        $this->addSql('ALTER TABLE devis_detail_finition DROP FOREIGN KEY FK_BE70DB30A0C197D7');
        $this->addSql('ALTER TABLE devis_detail_finition DROP FOREIGN KEY FK_BE70DB30CB56F5AF');
        $this->addSql('DROP INDEX IDX_BE70DB30CB56F5AF ON devis_detail_finition');
        $this->addSql('ALTER TABLE devis_detail_finition DROP nom_finition, DROP obligatoire, DROP finition_id, CHANGE configuration_finition_id configuration_finition_id INT NOT NULL');
        $this->addSql('ALTER TABLE devis_detail_finition ADD CONSTRAINT `FK_BE70DB30A0C197D7` FOREIGN KEY (configuration_finition_id) REFERENCES produit_configuration_finition (id)');
    }
}
