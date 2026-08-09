<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260806230029 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE commandes_details ADD statut_production VARCHAR(30) DEFAULT \'a_produire\' NOT NULL, ADD production_debute_le DATETIME DEFAULT NULL, ADD production_terminee_le DATETIME DEFAULT NULL, ADD quantite_produite INT DEFAULT 0 NOT NULL, ADD quantite_rebut INT DEFAULT 0 NOT NULL, ADD observation_production LONGTEXT DEFAULT NULL, ADD production_debutee_par_id INT DEFAULT NULL, ADD production_terminee_par_id INT DEFAULT NULL');
        $this->addSql('ALTER TABLE commandes_details ADD CONSTRAINT FK_B48B83DAE87137C3 FOREIGN KEY (production_debutee_par_id) REFERENCES `user` (id) ON DELETE SET NULL');
        $this->addSql('ALTER TABLE commandes_details ADD CONSTRAINT FK_B48B83DAF889D27D FOREIGN KEY (production_terminee_par_id) REFERENCES `user` (id) ON DELETE SET NULL');
        $this->addSql('CREATE INDEX IDX_B48B83DAE87137C3 ON commandes_details (production_debutee_par_id)');
        $this->addSql('CREATE INDEX IDX_B48B83DAF889D27D ON commandes_details (production_terminee_par_id)');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE commandes_details DROP FOREIGN KEY FK_B48B83DAE87137C3');
        $this->addSql('ALTER TABLE commandes_details DROP FOREIGN KEY FK_B48B83DAF889D27D');
        $this->addSql('DROP INDEX IDX_B48B83DAE87137C3 ON commandes_details');
        $this->addSql('DROP INDEX IDX_B48B83DAF889D27D ON commandes_details');
        $this->addSql('ALTER TABLE commandes_details DROP statut_production, DROP production_debute_le, DROP production_terminee_le, DROP quantite_produite, DROP quantite_rebut, DROP observation_production, DROP production_debutee_par_id, DROP production_terminee_par_id');
    }
}
