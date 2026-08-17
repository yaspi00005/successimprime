<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

final class Version20260817150000 extends AbstractMigration
{
    public function getDescription(): string
    {
        return "Ajoute la verification admin (verifie, verifie_par_id, date_verification) sur mouvement_tresorerie, sans impact sur les calculs de solde.";
    }

    public function up(Schema $schema): void
    {
        $this->addSql("ALTER TABLE mouvement_tresorerie ADD verifie TINYINT(1) NOT NULL DEFAULT 0, ADD verifie_par_id INT DEFAULT NULL, ADD date_verification DATETIME DEFAULT NULL");
        $this->addSql('ALTER TABLE mouvement_tresorerie ADD CONSTRAINT FK_mouvement_tresorerie_verifie_par FOREIGN KEY (verifie_par_id) REFERENCES `user` (id) ON DELETE SET NULL');
        $this->addSql('CREATE INDEX IDX_mouvement_tresorerie_verifie_par ON mouvement_tresorerie (verifie_par_id)');
    }

    public function down(Schema $schema): void
    {
        $this->addSql('ALTER TABLE mouvement_tresorerie DROP FOREIGN KEY FK_mouvement_tresorerie_verifie_par');
        $this->addSql('DROP INDEX IDX_mouvement_tresorerie_verifie_par ON mouvement_tresorerie');
        $this->addSql('ALTER TABLE mouvement_tresorerie DROP verifie, DROP verifie_par_id, DROP date_verification');
    }
}
