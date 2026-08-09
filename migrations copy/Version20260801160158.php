<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260801160158 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE commande_detail_finition DROP FOREIGN KEY `FK_B07D7138A0C197D7`');
        $this->addSql('DROP INDEX uniq_commande_detail_configuration_finition ON commande_detail_finition');
        $this->addSql('ALTER TABLE commande_detail_finition ADD nom_finition VARCHAR(255) NOT NULL, ADD obligatoire TINYINT DEFAULT 0 NOT NULL, ADD finition_id INT NOT NULL, CHANGE configuration_finition_id configuration_finition_id INT DEFAULT NULL');
        $this->addSql('ALTER TABLE commande_detail_finition ADD CONSTRAINT FK_B07D7138A0C197D7 FOREIGN KEY (configuration_finition_id) REFERENCES produit_configuration_finition (id) ON DELETE SET NULL');
        $this->addSql('ALTER TABLE commande_detail_finition ADD CONSTRAINT FK_B07D7138CB56F5AF FOREIGN KEY (finition_id) REFERENCES finition (id) ON DELETE RESTRICT');
        $this->addSql('CREATE INDEX IDX_B07D7138CB56F5AF ON commande_detail_finition (finition_id)');
        $this->addSql('CREATE UNIQUE INDEX uniq_commande_detail_finition ON commande_detail_finition (commande_detail_id, finition_id)');
        $this->addSql('ALTER TABLE produits ADD mode_calcul VARCHAR(30) DEFAULT \'unite\' NOT NULL');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE commande_detail_finition DROP FOREIGN KEY FK_B07D7138A0C197D7');
        $this->addSql('ALTER TABLE commande_detail_finition DROP FOREIGN KEY FK_B07D7138CB56F5AF');
        $this->addSql('DROP INDEX IDX_B07D7138CB56F5AF ON commande_detail_finition');
        $this->addSql('DROP INDEX uniq_commande_detail_finition ON commande_detail_finition');
        $this->addSql('ALTER TABLE commande_detail_finition DROP nom_finition, DROP obligatoire, DROP finition_id, CHANGE configuration_finition_id configuration_finition_id INT NOT NULL');
        $this->addSql('ALTER TABLE commande_detail_finition ADD CONSTRAINT `FK_B07D7138A0C197D7` FOREIGN KEY (configuration_finition_id) REFERENCES produit_configuration_finition (id)');
        $this->addSql('CREATE UNIQUE INDEX uniq_commande_detail_configuration_finition ON commande_detail_finition (commande_detail_id, configuration_finition_id)');
        $this->addSql('ALTER TABLE produits DROP mode_calcul');
    }
}
