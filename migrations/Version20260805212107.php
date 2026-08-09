<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260805212107 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('CREATE TABLE ligne_rapprochement_bancaire (id INT AUTO_INCREMENT NOT NULL, date_releve DATE DEFAULT NULL, reference_bancaire VARCHAR(100) DEFAULT NULL, montant_releve INT NOT NULL, pointee TINYINT DEFAULT 0 NOT NULL, observation LONGTEXT DEFAULT NULL, date_creation DATETIME NOT NULL, rapprochement_bancaire_id INT NOT NULL, mouvement_tresorerie_id INT NOT NULL, INDEX IDX_83FBB11264AED8C9 (rapprochement_bancaire_id), INDEX IDX_83FBB112C1DCAF54 (mouvement_tresorerie_id), UNIQUE INDEX uniq_ligne_rapprochement_mouvement (rapprochement_bancaire_id, mouvement_tresorerie_id), PRIMARY KEY (id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('CREATE TABLE rapprochement_bancaire (id INT AUTO_INCREMENT NOT NULL, reference VARCHAR(50) NOT NULL, date_debut DATE NOT NULL, date_fin DATE NOT NULL, solde_ouverture_releve INT NOT NULL, solde_cloture_releve INT NOT NULL, solde_comptable INT NOT NULL, ecart INT NOT NULL, statut VARCHAR(20) DEFAULT \'brouillon\' NOT NULL, observation LONGTEXT DEFAULT NULL, date_creation DATETIME NOT NULL, date_validation DATETIME DEFAULT NULL, date_cloture DATETIME DEFAULT NULL, compte_tresorerie_id INT NOT NULL, cree_par_id INT DEFAULT NULL, valide_par_id INT DEFAULT NULL, INDEX IDX_D4D082D0A11E8C5A (compte_tresorerie_id), INDEX IDX_D4D082D0FC29C013 (cree_par_id), INDEX IDX_D4D082D06AF12ED9 (valide_par_id), UNIQUE INDEX uniq_rapprochement_reference (reference), PRIMARY KEY (id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('ALTER TABLE ligne_rapprochement_bancaire ADD CONSTRAINT FK_83FBB11264AED8C9 FOREIGN KEY (rapprochement_bancaire_id) REFERENCES rapprochement_bancaire (id) ON DELETE CASCADE');
        $this->addSql('ALTER TABLE ligne_rapprochement_bancaire ADD CONSTRAINT FK_83FBB112C1DCAF54 FOREIGN KEY (mouvement_tresorerie_id) REFERENCES mouvement_tresorerie (id) ON DELETE RESTRICT');
        $this->addSql('ALTER TABLE rapprochement_bancaire ADD CONSTRAINT FK_D4D082D0A11E8C5A FOREIGN KEY (compte_tresorerie_id) REFERENCES compte_tresorerie (id) ON DELETE RESTRICT');
        $this->addSql('ALTER TABLE rapprochement_bancaire ADD CONSTRAINT FK_D4D082D0FC29C013 FOREIGN KEY (cree_par_id) REFERENCES `user` (id) ON DELETE SET NULL');
        $this->addSql('ALTER TABLE rapprochement_bancaire ADD CONSTRAINT FK_D4D082D06AF12ED9 FOREIGN KEY (valide_par_id) REFERENCES `user` (id) ON DELETE SET NULL');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE ligne_rapprochement_bancaire DROP FOREIGN KEY FK_83FBB11264AED8C9');
        $this->addSql('ALTER TABLE ligne_rapprochement_bancaire DROP FOREIGN KEY FK_83FBB112C1DCAF54');
        $this->addSql('ALTER TABLE rapprochement_bancaire DROP FOREIGN KEY FK_D4D082D0A11E8C5A');
        $this->addSql('ALTER TABLE rapprochement_bancaire DROP FOREIGN KEY FK_D4D082D0FC29C013');
        $this->addSql('ALTER TABLE rapprochement_bancaire DROP FOREIGN KEY FK_D4D082D06AF12ED9');
        $this->addSql('DROP TABLE ligne_rapprochement_bancaire');
        $this->addSql('DROP TABLE rapprochement_bancaire');
    }
}
