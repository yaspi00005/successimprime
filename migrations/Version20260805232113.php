<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260805232113 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('CREATE TABLE controle_pre_presse (id INT AUTO_INCREMENT NOT NULL, statut VARCHAR(30) NOT NULL, format_conforme TINYINT DEFAULT 0 NOT NULL, dimensions_conformes TINYINT DEFAULT 0 NOT NULL, resolution_conforme TINYINT DEFAULT 0 NOT NULL, profil_couleurs_conforme TINYINT DEFAULT 0 NOT NULL, fonds_perdus_conformes TINYINT DEFAULT 0 NOT NULL, marges_securite_conformes TINYINT DEFAULT 0 NOT NULL, polices_conformes TINYINT DEFAULT 0 NOT NULL, orthographe_verifiee TINYINT DEFAULT 0 NOT NULL, orientation_conforme TINYINT DEFAULT 0 NOT NULL, nombre_pages_conforme TINYINT DEFAULT 0 NOT NULL, recto_verso_conforme TINYINT DEFAULT 0 NOT NULL, support_conforme TINYINT DEFAULT 0 NOT NULL, quantite_conforme TINYINT DEFAULT 0 NOT NULL, fichier_deja_traite TINYINT DEFAULT 0 NOT NULL, correction_necessaire TINYINT DEFAULT 0 NOT NULL, bat_necessaire TINYINT DEFAULT 0 NOT NULL, bat_valide TINYINT DEFAULT 0 NOT NULL, anomalies LONGTEXT DEFAULT NULL, corrections_effectuees LONGTEXT DEFAULT NULL, observation LONGTEXT DEFAULT NULL, cree_le DATETIME NOT NULL, controle_le DATETIME DEFAULT NULL, traite_le DATETIME DEFAULT NULL, valide_le DATETIME DEFAULT NULL, envoye_production_le DATETIME DEFAULT NULL, commande_detail_id INT NOT NULL, controle_par_id INT DEFAULT NULL, traite_par_id INT DEFAULT NULL, valide_par_id INT DEFAULT NULL, envoye_production_par_id INT DEFAULT NULL, INDEX IDX_FA26187C8DC59F9 (commande_detail_id), INDEX IDX_FA26187BA5AD30 (controle_par_id), INDEX IDX_FA26187167FABE8 (traite_par_id), INDEX IDX_FA261876AF12ED9 (valide_par_id), INDEX IDX_FA261878FBD9DB1 (envoye_production_par_id), PRIMARY KEY (id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('CREATE TABLE controle_pre_presse_fichier (controle_pre_presse_id INT NOT NULL, fichier_id INT NOT NULL, INDEX IDX_4D8558C4C6055018 (controle_pre_presse_id), INDEX IDX_4D8558C4F915CFE (fichier_id), PRIMARY KEY (controle_pre_presse_id, fichier_id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('ALTER TABLE controle_pre_presse ADD CONSTRAINT FK_FA26187C8DC59F9 FOREIGN KEY (commande_detail_id) REFERENCES commandes_details (id) ON DELETE CASCADE');
        $this->addSql('ALTER TABLE controle_pre_presse ADD CONSTRAINT FK_FA26187BA5AD30 FOREIGN KEY (controle_par_id) REFERENCES `user` (id) ON DELETE SET NULL');
        $this->addSql('ALTER TABLE controle_pre_presse ADD CONSTRAINT FK_FA26187167FABE8 FOREIGN KEY (traite_par_id) REFERENCES `user` (id) ON DELETE SET NULL');
        $this->addSql('ALTER TABLE controle_pre_presse ADD CONSTRAINT FK_FA261876AF12ED9 FOREIGN KEY (valide_par_id) REFERENCES `user` (id) ON DELETE SET NULL');
        $this->addSql('ALTER TABLE controle_pre_presse ADD CONSTRAINT FK_FA261878FBD9DB1 FOREIGN KEY (envoye_production_par_id) REFERENCES `user` (id) ON DELETE SET NULL');
        $this->addSql('ALTER TABLE controle_pre_presse_fichier ADD CONSTRAINT FK_4D8558C4C6055018 FOREIGN KEY (controle_pre_presse_id) REFERENCES controle_pre_presse (id) ON DELETE CASCADE');
        $this->addSql('ALTER TABLE controle_pre_presse_fichier ADD CONSTRAINT FK_4D8558C4F915CFE FOREIGN KEY (fichier_id) REFERENCES commande_detail_fichier (id) ON DELETE CASCADE');
        $this->addSql('ALTER TABLE user CHANGE actif actif TINYINT DEFAULT 1 NOT NULL');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE controle_pre_presse DROP FOREIGN KEY FK_FA26187C8DC59F9');
        $this->addSql('ALTER TABLE controle_pre_presse DROP FOREIGN KEY FK_FA26187BA5AD30');
        $this->addSql('ALTER TABLE controle_pre_presse DROP FOREIGN KEY FK_FA26187167FABE8');
        $this->addSql('ALTER TABLE controle_pre_presse DROP FOREIGN KEY FK_FA261876AF12ED9');
        $this->addSql('ALTER TABLE controle_pre_presse DROP FOREIGN KEY FK_FA261878FBD9DB1');
        $this->addSql('ALTER TABLE controle_pre_presse_fichier DROP FOREIGN KEY FK_4D8558C4C6055018');
        $this->addSql('ALTER TABLE controle_pre_presse_fichier DROP FOREIGN KEY FK_4D8558C4F915CFE');
        $this->addSql('DROP TABLE controle_pre_presse');
        $this->addSql('DROP TABLE controle_pre_presse_fichier');
        $this->addSql('ALTER TABLE `user` CHANGE actif actif TINYINT NOT NULL');
    }
}
