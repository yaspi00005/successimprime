<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260726194736 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('CREATE TABLE produit_configuration (id INT AUTO_INCREMENT NOT NULL, active TINYINT NOT NULL, ordre INT NOT NULL, description LONGTEXT DEFAULT NULL, prix_base INT DEFAULT NULL, mode_calcul VARCHAR(30) NOT NULL, quantite_minimale INT NOT NULL, quantite_maximale INT DEFAULT NULL, produit_id INT NOT NULL, type_impression_id INT NOT NULL, support_id INT NOT NULL, format_id INT NOT NULL, INDEX IDX_8BBC0309F347EFB (produit_id), INDEX IDX_8BBC0309D357F183 (type_impression_id), INDEX IDX_8BBC0309315B405 (support_id), INDEX IDX_8BBC0309D629F605 (format_id), UNIQUE INDEX uniq_produit_configuration (produit_id, type_impression_id, support_id, format_id), PRIMARY KEY (id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('CREATE TABLE produit_configuration_finition (id INT AUTO_INCREMENT NOT NULL, obligatoire TINYINT NOT NULL, selectionnee_par_defaut TINYINT NOT NULL, payante TINYINT NOT NULL, prix INT NOT NULL, mode_calcul VARCHAR(30) NOT NULL, quantite_minimale INT NOT NULL, quantite_maximale INT DEFAULT NULL, active TINYINT NOT NULL, ordre INT NOT NULL, description VARCHAR(500) DEFAULT NULL, produit_configuration_id INT NOT NULL, finition_id INT NOT NULL, INDEX IDX_BF2ECD31806A5250 (produit_configuration_id), INDEX IDX_BF2ECD31CB56F5AF (finition_id), UNIQUE INDEX uniq_configuration_finition (produit_configuration_id, finition_id), PRIMARY KEY (id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('ALTER TABLE produit_configuration ADD CONSTRAINT FK_8BBC0309F347EFB FOREIGN KEY (produit_id) REFERENCES produits (id) ON DELETE CASCADE');
        $this->addSql('ALTER TABLE produit_configuration ADD CONSTRAINT FK_8BBC0309D357F183 FOREIGN KEY (type_impression_id) REFERENCES types_impression (id) ON DELETE CASCADE');
        $this->addSql('ALTER TABLE produit_configuration ADD CONSTRAINT FK_8BBC0309315B405 FOREIGN KEY (support_id) REFERENCES supports (id) ON DELETE CASCADE');
        $this->addSql('ALTER TABLE produit_configuration ADD CONSTRAINT FK_8BBC0309D629F605 FOREIGN KEY (format_id) REFERENCES format (id) ON DELETE CASCADE');
        $this->addSql('ALTER TABLE produit_configuration_finition ADD CONSTRAINT FK_BF2ECD31806A5250 FOREIGN KEY (produit_configuration_id) REFERENCES produit_configuration (id) ON DELETE CASCADE');
        $this->addSql('ALTER TABLE produit_configuration_finition ADD CONSTRAINT FK_BF2ECD31CB56F5AF FOREIGN KEY (finition_id) REFERENCES finition (id) ON DELETE CASCADE');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE produit_configuration DROP FOREIGN KEY FK_8BBC0309F347EFB');
        $this->addSql('ALTER TABLE produit_configuration DROP FOREIGN KEY FK_8BBC0309D357F183');
        $this->addSql('ALTER TABLE produit_configuration DROP FOREIGN KEY FK_8BBC0309315B405');
        $this->addSql('ALTER TABLE produit_configuration DROP FOREIGN KEY FK_8BBC0309D629F605');
        $this->addSql('ALTER TABLE produit_configuration_finition DROP FOREIGN KEY FK_BF2ECD31806A5250');
        $this->addSql('ALTER TABLE produit_configuration_finition DROP FOREIGN KEY FK_BF2ECD31CB56F5AF');
        $this->addSql('DROP TABLE produit_configuration');
        $this->addSql('DROP TABLE produit_configuration_finition');
    }
}
