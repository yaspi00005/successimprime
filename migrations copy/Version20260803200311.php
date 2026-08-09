<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260803200311 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE devis_detail_finition DROP FOREIGN KEY `FK_BE70DB30A0C197D7`');
        $this->addSql('ALTER TABLE devis_detail_finition DROP FOREIGN KEY `FK_BE70DB30CB56F5AF`');
        $this->addSql('DROP INDEX uniq_devis_detail_finition ON devis_detail_finition');
        $this->addSql('DROP INDEX IDX_BE70DB30CB56F5AF ON devis_detail_finition');
        $this->addSql('ALTER TABLE devis_detail_finition DROP nom_finition, DROP obligatoire, DROP finition_id, CHANGE prix_applique prix_applique INT NOT NULL, CHANGE mode_calcul mode_calcul VARCHAR(30) NOT NULL, CHANGE quantite quantite INT NOT NULL, CHANGE montant montant INT NOT NULL, CHANGE configuration_finition_id configuration_finition_id INT NOT NULL');
        $this->addSql('ALTER TABLE devis_detail_finition ADD CONSTRAINT FK_BE70DB30A0C197D7 FOREIGN KEY (configuration_finition_id) REFERENCES produit_configuration_finition (id) ON DELETE RESTRICT');
        $this->addSql('CREATE UNIQUE INDEX uniq_devis_detail_configuration_finition ON devis_detail_finition (devis_detail_id, configuration_finition_id)');
        $this->addSql('ALTER TABLE devis_details ADD bat_valide TINYINT DEFAULT 0 NOT NULL, ADD temps_reel INT DEFAULT NULL, ADD fichier VARCHAR(255) DEFAULT NULL, ADD machine_id INT DEFAULT NULL, DROP ordre');
        $this->addSql('ALTER TABLE devis_details ADD CONSTRAINT FK_E0C890D6F6B75B26 FOREIGN KEY (machine_id) REFERENCES machines (id) ON DELETE SET NULL');
        $this->addSql('CREATE INDEX IDX_E0C890D6F6B75B26 ON devis_details (machine_id)');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE devis_details DROP FOREIGN KEY FK_E0C890D6F6B75B26');
        $this->addSql('DROP INDEX IDX_E0C890D6F6B75B26 ON devis_details');
        $this->addSql('ALTER TABLE devis_details ADD ordre INT DEFAULT 10 NOT NULL, DROP bat_valide, DROP temps_reel, DROP fichier, DROP machine_id');
        $this->addSql('ALTER TABLE devis_detail_finition DROP FOREIGN KEY FK_BE70DB30A0C197D7');
        $this->addSql('DROP INDEX uniq_devis_detail_configuration_finition ON devis_detail_finition');
        $this->addSql('ALTER TABLE devis_detail_finition ADD nom_finition VARCHAR(255) NOT NULL, ADD obligatoire TINYINT DEFAULT 0 NOT NULL, ADD finition_id INT NOT NULL, CHANGE prix_applique prix_applique INT DEFAULT 0 NOT NULL, CHANGE mode_calcul mode_calcul VARCHAR(30) DEFAULT \'forfait\' NOT NULL, CHANGE quantite quantite INT DEFAULT 1 NOT NULL, CHANGE montant montant INT DEFAULT 0 NOT NULL, CHANGE configuration_finition_id configuration_finition_id INT DEFAULT NULL');
        $this->addSql('ALTER TABLE devis_detail_finition ADD CONSTRAINT `FK_BE70DB30A0C197D7` FOREIGN KEY (configuration_finition_id) REFERENCES produit_configuration_finition (id) ON DELETE SET NULL');
        $this->addSql('ALTER TABLE devis_detail_finition ADD CONSTRAINT `FK_BE70DB30CB56F5AF` FOREIGN KEY (finition_id) REFERENCES finition (id)');
        $this->addSql('CREATE UNIQUE INDEX uniq_devis_detail_finition ON devis_detail_finition (devis_detail_id, finition_id)');
        $this->addSql('CREATE INDEX IDX_BE70DB30CB56F5AF ON devis_detail_finition (finition_id)');
    }
}
