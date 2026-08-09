<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260801211741 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('CREATE TABLE devis (id INT AUTO_INCREMENT NOT NULL, numero VARCHAR(50) NOT NULL, date_creation DATETIME NOT NULL, date_validite DATETIME NOT NULL, statut VARCHAR(30) NOT NULL, remise_pourcentage INT DEFAULT 0 NOT NULL, montant_remise INT DEFAULT 0 NOT NULL, taux_tva INT DEFAULT 0 NOT NULL, total_ht INT DEFAULT 0 NOT NULL, total_apres_remise INT DEFAULT 0 NOT NULL, montant_tva INT DEFAULT 0 NOT NULL, total_ttc INT DEFAULT 0 NOT NULL, notes LONGTEXT DEFAULT NULL, conditions_commerciales LONGTEXT DEFAULT NULL, client_id INT NOT NULL, commande_id INT DEFAULT NULL, INDEX IDX_8B27C52B19EB6921 (client_id), UNIQUE INDEX UNIQ_8B27C52B82EA2E54 (commande_id), UNIQUE INDEX uniq_devis_numero (numero), PRIMARY KEY (id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('CREATE TABLE devis_detail_finition (id INT AUTO_INCREMENT NOT NULL, nom_finition VARCHAR(255) NOT NULL, obligatoire TINYINT DEFAULT 0 NOT NULL, prix_applique INT DEFAULT 0 NOT NULL, mode_calcul VARCHAR(30) DEFAULT \'forfait\' NOT NULL, quantite INT DEFAULT 1 NOT NULL, montant INT DEFAULT 0 NOT NULL, devis_detail_id INT NOT NULL, configuration_finition_id INT DEFAULT NULL, finition_id INT NOT NULL, INDEX IDX_BE70DB30A903C9C1 (devis_detail_id), INDEX IDX_BE70DB30A0C197D7 (configuration_finition_id), INDEX IDX_BE70DB30CB56F5AF (finition_id), UNIQUE INDEX uniq_devis_detail_finition (devis_detail_id, finition_id), PRIMARY KEY (id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('CREATE TABLE devis_details (id INT AUTO_INCREMENT NOT NULL, mode_configuration VARCHAR(20) DEFAULT \'automatique\' NOT NULL, designation VARCHAR(255) NOT NULL, largeur NUMERIC(10, 2) DEFAULT NULL, longueur NUMERIC(10, 2) DEFAULT NULL, surface NUMERIC(12, 4) DEFAULT NULL, quantite INT DEFAULT 1 NOT NULL, prix_unitaire INT DEFAULT 0 NOT NULL, cout_revient INT DEFAULT 0 NOT NULL, remise INT DEFAULT 0 NOT NULL, tva INT DEFAULT 0 NOT NULL, total_ht INT DEFAULT 0 NOT NULL, total_ttc INT DEFAULT 0 NOT NULL, profil_couleurs VARCHAR(20) DEFAULT NULL, resolution VARCHAR(50) DEFAULT NULL, grammage VARCHAR(100) DEFAULT NULL, epaisseur VARCHAR(50) DEFAULT NULL, recto_verso TINYINT DEFAULT 0 NOT NULL, nombre_faces INT DEFAULT 1 NOT NULL, laminage VARCHAR(255) DEFAULT NULL, oeillets TINYINT DEFAULT 0 NOT NULL, decoupe TINYINT DEFAULT 0 NOT NULL, pliage VARCHAR(100) DEFAULT NULL, emballage TINYINT DEFAULT 0 NOT NULL, ordre INT DEFAULT 10 NOT NULL, etat TINYINT DEFAULT 1 NOT NULL, priorite VARCHAR(30) DEFAULT \'normale\' NOT NULL, temps_estime INT DEFAULT NULL, observation LONGTEXT DEFAULT NULL, mode_calcul VARCHAR(30) DEFAULT \'unite\' NOT NULL, devis_id INT NOT NULL, produit_id INT DEFAULT NULL, produit_configuration_id INT DEFAULT NULL, type_impression_id INT DEFAULT NULL, support_id INT DEFAULT NULL, format_id INT DEFAULT NULL, INDEX IDX_E0C890D641DEFADA (devis_id), INDEX IDX_E0C890D6F347EFB (produit_id), INDEX IDX_E0C890D6806A5250 (produit_configuration_id), INDEX IDX_E0C890D6D357F183 (type_impression_id), INDEX IDX_E0C890D6315B405 (support_id), INDEX IDX_E0C890D6D629F605 (format_id), PRIMARY KEY (id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('ALTER TABLE devis ADD CONSTRAINT FK_8B27C52B19EB6921 FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE RESTRICT');
        $this->addSql('ALTER TABLE devis ADD CONSTRAINT FK_8B27C52B82EA2E54 FOREIGN KEY (commande_id) REFERENCES commandes (id) ON DELETE SET NULL');
        $this->addSql('ALTER TABLE devis_detail_finition ADD CONSTRAINT FK_BE70DB30A903C9C1 FOREIGN KEY (devis_detail_id) REFERENCES devis_details (id) ON DELETE CASCADE');
        $this->addSql('ALTER TABLE devis_detail_finition ADD CONSTRAINT FK_BE70DB30A0C197D7 FOREIGN KEY (configuration_finition_id) REFERENCES produit_configuration_finition (id) ON DELETE SET NULL');
        $this->addSql('ALTER TABLE devis_detail_finition ADD CONSTRAINT FK_BE70DB30CB56F5AF FOREIGN KEY (finition_id) REFERENCES finition (id) ON DELETE RESTRICT');
        $this->addSql('ALTER TABLE devis_details ADD CONSTRAINT FK_E0C890D641DEFADA FOREIGN KEY (devis_id) REFERENCES devis (id) ON DELETE CASCADE');
        $this->addSql('ALTER TABLE devis_details ADD CONSTRAINT FK_E0C890D6F347EFB FOREIGN KEY (produit_id) REFERENCES produits (id) ON DELETE SET NULL');
        $this->addSql('ALTER TABLE devis_details ADD CONSTRAINT FK_E0C890D6806A5250 FOREIGN KEY (produit_configuration_id) REFERENCES produit_configuration (id) ON DELETE SET NULL');
        $this->addSql('ALTER TABLE devis_details ADD CONSTRAINT FK_E0C890D6D357F183 FOREIGN KEY (type_impression_id) REFERENCES types_impression (id) ON DELETE SET NULL');
        $this->addSql('ALTER TABLE devis_details ADD CONSTRAINT FK_E0C890D6315B405 FOREIGN KEY (support_id) REFERENCES supports (id) ON DELETE SET NULL');
        $this->addSql('ALTER TABLE devis_details ADD CONSTRAINT FK_E0C890D6D629F605 FOREIGN KEY (format_id) REFERENCES format (id) ON DELETE SET NULL');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE devis DROP FOREIGN KEY FK_8B27C52B19EB6921');
        $this->addSql('ALTER TABLE devis DROP FOREIGN KEY FK_8B27C52B82EA2E54');
        $this->addSql('ALTER TABLE devis_detail_finition DROP FOREIGN KEY FK_BE70DB30A903C9C1');
        $this->addSql('ALTER TABLE devis_detail_finition DROP FOREIGN KEY FK_BE70DB30A0C197D7');
        $this->addSql('ALTER TABLE devis_detail_finition DROP FOREIGN KEY FK_BE70DB30CB56F5AF');
        $this->addSql('ALTER TABLE devis_details DROP FOREIGN KEY FK_E0C890D641DEFADA');
        $this->addSql('ALTER TABLE devis_details DROP FOREIGN KEY FK_E0C890D6F347EFB');
        $this->addSql('ALTER TABLE devis_details DROP FOREIGN KEY FK_E0C890D6806A5250');
        $this->addSql('ALTER TABLE devis_details DROP FOREIGN KEY FK_E0C890D6D357F183');
        $this->addSql('ALTER TABLE devis_details DROP FOREIGN KEY FK_E0C890D6315B405');
        $this->addSql('ALTER TABLE devis_details DROP FOREIGN KEY FK_E0C890D6D629F605');
        $this->addSql('DROP TABLE devis');
        $this->addSql('DROP TABLE devis_detail_finition');
        $this->addSql('DROP TABLE devis_details');
    }
}
