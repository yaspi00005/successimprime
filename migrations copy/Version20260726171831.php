<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260726171831 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE commandes_details DROP FOREIGN KEY `FK_B48B83DA315B405`');
        $this->addSql('ALTER TABLE commandes_details DROP FOREIGN KEY `FK_B48B83DA82EA2E54`');
        $this->addSql('ALTER TABLE commandes_details DROP FOREIGN KEY `FK_B48B83DAD357F183`');
        $this->addSql('ALTER TABLE commandes_details DROP FOREIGN KEY `FK_B48B83DAD629F605`');
        $this->addSql('ALTER TABLE commandes_details DROP FOREIGN KEY `FK_B48B83DAF347EFB`');
        $this->addSql('ALTER TABLE commandes_details DROP FOREIGN KEY `FK_B48B83DAF6B75B26`');
        $this->addSql('ALTER TABLE commandes_details DROP FOREIGN KEY `FK_B48B83DA97185C1E`');
        $this->addSql('DROP INDEX IDX_B48B83DA97185C1E ON commandes_details');
        $this->addSql('ALTER TABLE commandes_details DROP types_impressions, DROP longueurs, DROP prix, DROP remises, DROP quantites, DROP supports_id, CHANGE largeur largeur NUMERIC(10, 2) DEFAULT NULL, CHANGE longueur longueur NUMERIC(10, 2) DEFAULT NULL, CHANGE surface surface NUMERIC(12, 4) DEFAULT NULL, CHANGE profil_couleurs profil_couleurs VARCHAR(20) DEFAULT NULL, CHANGE resolution resolution VARCHAR(50) DEFAULT NULL, CHANGE grammage grammage VARCHAR(100) DEFAULT NULL, CHANGE epaisseur epaisseur VARCHAR(50) DEFAULT NULL, CHANGE laminage laminage VARCHAR(255) DEFAULT NULL, CHANGE pliage pliage VARCHAR(100) DEFAULT NULL, CHANGE emballage emballage TINYINT NOT NULL, CHANGE bat_valide bat_valide TINYINT NOT NULL, CHANGE temps_estime temps_estime INT DEFAULT NULL, CHANGE temps_reel temps_reel INT DEFAULT NULL, CHANGE fichier fichier VARCHAR(255) DEFAULT NULL, CHANGE observation observation LONGTEXT DEFAULT NULL, CHANGE commande_id commande_id INT NOT NULL');
        $this->addSql('ALTER TABLE commandes_details ADD CONSTRAINT FK_B48B83DA315B405 FOREIGN KEY (support_id) REFERENCES supports (id) ON DELETE SET NULL');
        $this->addSql('ALTER TABLE commandes_details ADD CONSTRAINT FK_B48B83DA82EA2E54 FOREIGN KEY (commande_id) REFERENCES commandes (id) ON DELETE CASCADE');
        $this->addSql('ALTER TABLE commandes_details ADD CONSTRAINT FK_B48B83DAD357F183 FOREIGN KEY (type_impression_id) REFERENCES types_impression (id) ON DELETE SET NULL');
        $this->addSql('ALTER TABLE commandes_details ADD CONSTRAINT FK_B48B83DAD629F605 FOREIGN KEY (format_id) REFERENCES format (id) ON DELETE SET NULL');
        $this->addSql('ALTER TABLE commandes_details ADD CONSTRAINT FK_B48B83DAF347EFB FOREIGN KEY (produit_id) REFERENCES produits (id) ON DELETE SET NULL');
        $this->addSql('ALTER TABLE commandes_details ADD CONSTRAINT FK_B48B83DAF6B75B26 FOREIGN KEY (machine_id) REFERENCES machines (id) ON DELETE SET NULL');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE commandes_details DROP FOREIGN KEY FK_B48B83DA82EA2E54');
        $this->addSql('ALTER TABLE commandes_details DROP FOREIGN KEY FK_B48B83DAF347EFB');
        $this->addSql('ALTER TABLE commandes_details DROP FOREIGN KEY FK_B48B83DAD357F183');
        $this->addSql('ALTER TABLE commandes_details DROP FOREIGN KEY FK_B48B83DA315B405');
        $this->addSql('ALTER TABLE commandes_details DROP FOREIGN KEY FK_B48B83DAF6B75B26');
        $this->addSql('ALTER TABLE commandes_details DROP FOREIGN KEY FK_B48B83DAD629F605');
        $this->addSql('ALTER TABLE commandes_details ADD types_impressions VARCHAR(50) NOT NULL, ADD longueurs INT NOT NULL, ADD prix INT NOT NULL, ADD remises INT NOT NULL, ADD quantites INT NOT NULL, ADD supports_id INT DEFAULT NULL, CHANGE largeur largeur INT NOT NULL, CHANGE longueur longueur INT NOT NULL, CHANGE surface surface VARCHAR(100) DEFAULT NULL, CHANGE profil_couleurs profil_couleurs VARCHAR(5) NOT NULL, CHANGE resolution resolution LONGTEXT NOT NULL, CHANGE grammage grammage VARCHAR(100) NOT NULL, CHANGE epaisseur epaisseur VARCHAR(50) NOT NULL, CHANGE laminage laminage VARCHAR(255) NOT NULL, CHANGE pliage pliage BIGINT DEFAULT NULL, CHANGE emballage emballage TINYINT DEFAULT NULL, CHANGE bat_valide bat_valide BIGINT NOT NULL, CHANGE temps_estime temps_estime INT NOT NULL, CHANGE temps_reel temps_reel INT NOT NULL, CHANGE fichier fichier VARCHAR(255) NOT NULL, CHANGE observation observation LONGTEXT NOT NULL, CHANGE commande_id commande_id INT DEFAULT NULL');
        $this->addSql('ALTER TABLE commandes_details ADD CONSTRAINT `FK_B48B83DA82EA2E54` FOREIGN KEY (commande_id) REFERENCES commandes (id)');
        $this->addSql('ALTER TABLE commandes_details ADD CONSTRAINT `FK_B48B83DAF347EFB` FOREIGN KEY (produit_id) REFERENCES produits (id)');
        $this->addSql('ALTER TABLE commandes_details ADD CONSTRAINT `FK_B48B83DAD357F183` FOREIGN KEY (type_impression_id) REFERENCES types_impression (id)');
        $this->addSql('ALTER TABLE commandes_details ADD CONSTRAINT `FK_B48B83DA315B405` FOREIGN KEY (support_id) REFERENCES supports (id)');
        $this->addSql('ALTER TABLE commandes_details ADD CONSTRAINT `FK_B48B83DAF6B75B26` FOREIGN KEY (machine_id) REFERENCES machines (id)');
        $this->addSql('ALTER TABLE commandes_details ADD CONSTRAINT `FK_B48B83DAD629F605` FOREIGN KEY (format_id) REFERENCES format (id)');
        $this->addSql('ALTER TABLE commandes_details ADD CONSTRAINT `FK_B48B83DA97185C1E` FOREIGN KEY (supports_id) REFERENCES supports (id)');
        $this->addSql('CREATE INDEX IDX_B48B83DA97185C1E ON commandes_details (supports_id)');
    }
}
