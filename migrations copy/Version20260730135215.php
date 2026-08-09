<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260730135215 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE commandes_details DROP FOREIGN KEY `FK_B48B83DAF347EFB`');
        $this->addSql('ALTER TABLE commandes_details DROP prix, CHANGE quantite quantite INT DEFAULT 1 NOT NULL, CHANGE prix_unitaire prix_unitaire INT DEFAULT 0 NOT NULL, CHANGE cout_revient cout_revient INT DEFAULT 0 NOT NULL, CHANGE remise remise INT DEFAULT 0 NOT NULL, CHANGE tva tva INT DEFAULT 0 NOT NULL, CHANGE total_ht total_ht INT DEFAULT 0 NOT NULL, CHANGE total_ttc total_ttc INT DEFAULT 0 NOT NULL, CHANGE recto_verso recto_verso TINYINT DEFAULT 0 NOT NULL, CHANGE nombre_faces nombre_faces INT DEFAULT 1 NOT NULL, CHANGE oeillets oeillets TINYINT DEFAULT 0 NOT NULL, CHANGE decoupe decoupe TINYINT DEFAULT 0 NOT NULL, CHANGE emballage emballage TINYINT DEFAULT 0 NOT NULL, CHANGE bat_valide bat_valide TINYINT DEFAULT 0 NOT NULL, CHANGE etat etat TINYINT DEFAULT 1 NOT NULL, CHANGE priorite priorite VARCHAR(30) DEFAULT \'normale\' NOT NULL, CHANGE produit_id produit_id INT NOT NULL, CHANGE mode_configuration mode_configuration VARCHAR(20) DEFAULT \'automatique\' NOT NULL');
        $this->addSql('ALTER TABLE commandes_details ADD CONSTRAINT FK_B48B83DAF347EFB FOREIGN KEY (produit_id) REFERENCES produits (id) ON DELETE RESTRICT');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE commandes_details DROP FOREIGN KEY FK_B48B83DAF347EFB');
        $this->addSql('ALTER TABLE commandes_details ADD prix DOUBLE PRECISION DEFAULT NULL, CHANGE mode_configuration mode_configuration VARCHAR(20) DEFAULT \'manuel\' NOT NULL, CHANGE quantite quantite INT NOT NULL, CHANGE prix_unitaire prix_unitaire INT NOT NULL, CHANGE cout_revient cout_revient INT NOT NULL, CHANGE remise remise INT NOT NULL, CHANGE tva tva INT NOT NULL, CHANGE total_ht total_ht INT NOT NULL, CHANGE total_ttc total_ttc INT NOT NULL, CHANGE recto_verso recto_verso TINYINT NOT NULL, CHANGE nombre_faces nombre_faces INT NOT NULL, CHANGE oeillets oeillets TINYINT NOT NULL, CHANGE decoupe decoupe TINYINT NOT NULL, CHANGE emballage emballage TINYINT NOT NULL, CHANGE bat_valide bat_valide TINYINT NOT NULL, CHANGE etat etat TINYINT NOT NULL, CHANGE priorite priorite VARCHAR(30) NOT NULL, CHANGE produit_id produit_id INT DEFAULT NULL');
        $this->addSql('ALTER TABLE commandes_details ADD CONSTRAINT `FK_B48B83DAF347EFB` FOREIGN KEY (produit_id) REFERENCES produits (id) ON DELETE SET NULL');
    }
}
