<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260806191839 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('CREATE TABLE ordre_production (id INT AUTO_INCREMENT NOT NULL, numero VARCHAR(30) NOT NULL, statut VARCHAR(30) NOT NULL, priorite VARCHAR(20) NOT NULL, quantite INT DEFAULT NULL, instructions LONGTEXT DEFAULT NULL, cree_le DATETIME NOT NULL, date_limite DATETIME DEFAULT NULL, demarre_le DATETIME DEFAULT NULL, termine_le DATETIME DEFAULT NULL, commande_detail_id INT NOT NULL, controle_pre_presse_id INT NOT NULL, cree_par_id INT DEFAULT NULL, operateur_id INT DEFAULT NULL, UNIQUE INDEX UNIQ_D1C3E844F55AE19E (numero), INDEX IDX_D1C3E844C8DC59F9 (commande_detail_id), INDEX IDX_D1C3E844FC29C013 (cree_par_id), INDEX IDX_D1C3E8443F192FC (operateur_id), UNIQUE INDEX uniq_ordre_controle (controle_pre_presse_id), PRIMARY KEY (id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('CREATE TABLE ordre_production_fichier (ordre_production_id INT NOT NULL, commande_detail_fichier_id INT NOT NULL, INDEX IDX_514FAAF685180A13 (ordre_production_id), INDEX IDX_514FAAF64FB4C8B8 (commande_detail_fichier_id), PRIMARY KEY (ordre_production_id, commande_detail_fichier_id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('ALTER TABLE ordre_production ADD CONSTRAINT FK_D1C3E844C8DC59F9 FOREIGN KEY (commande_detail_id) REFERENCES commandes_details (id) ON DELETE CASCADE');
        $this->addSql('ALTER TABLE ordre_production ADD CONSTRAINT FK_D1C3E844C6055018 FOREIGN KEY (controle_pre_presse_id) REFERENCES controle_pre_presse (id) ON DELETE CASCADE');
        $this->addSql('ALTER TABLE ordre_production ADD CONSTRAINT FK_D1C3E844FC29C013 FOREIGN KEY (cree_par_id) REFERENCES `user` (id) ON DELETE SET NULL');
        $this->addSql('ALTER TABLE ordre_production ADD CONSTRAINT FK_D1C3E8443F192FC FOREIGN KEY (operateur_id) REFERENCES `user` (id) ON DELETE SET NULL');
        $this->addSql('ALTER TABLE ordre_production_fichier ADD CONSTRAINT FK_514FAAF685180A13 FOREIGN KEY (ordre_production_id) REFERENCES ordre_production (id) ON DELETE CASCADE');
        $this->addSql('ALTER TABLE ordre_production_fichier ADD CONSTRAINT FK_514FAAF64FB4C8B8 FOREIGN KEY (commande_detail_fichier_id) REFERENCES commande_detail_fichier (id) ON DELETE CASCADE');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE ordre_production DROP FOREIGN KEY FK_D1C3E844C8DC59F9');
        $this->addSql('ALTER TABLE ordre_production DROP FOREIGN KEY FK_D1C3E844C6055018');
        $this->addSql('ALTER TABLE ordre_production DROP FOREIGN KEY FK_D1C3E844FC29C013');
        $this->addSql('ALTER TABLE ordre_production DROP FOREIGN KEY FK_D1C3E8443F192FC');
        $this->addSql('ALTER TABLE ordre_production_fichier DROP FOREIGN KEY FK_514FAAF685180A13');
        $this->addSql('ALTER TABLE ordre_production_fichier DROP FOREIGN KEY FK_514FAAF64FB4C8B8');
        $this->addSql('DROP TABLE ordre_production');
        $this->addSql('DROP TABLE ordre_production_fichier');
    }
}
