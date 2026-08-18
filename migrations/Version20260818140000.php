<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

final class Version20260818140000 extends AbstractMigration
{
    public function getDescription(): string
    {
        return "Ajoute le suivi de la derniere modification d'une commande (modifie_le, modifie_par_id), notamment pour les modifications faites par un administrateur sur une commande verrouillee.";
    }

    public function up(Schema $schema): void
    {
        $this->addSql('ALTER TABLE commandes ADD modifie_le DATETIME DEFAULT NULL, ADD modifie_par_id INT DEFAULT NULL');
        $this->addSql('ALTER TABLE commandes ADD CONSTRAINT FK_commandes_modifie_par FOREIGN KEY (modifie_par_id) REFERENCES `user` (id) ON DELETE SET NULL');
        $this->addSql('CREATE INDEX IDX_commandes_modifie_par ON commandes (modifie_par_id)');
    }

    public function down(Schema $schema): void
    {
        $this->addSql('ALTER TABLE commandes DROP FOREIGN KEY FK_commandes_modifie_par');
        $this->addSql('DROP INDEX IDX_commandes_modifie_par ON commandes');
        $this->addSql('ALTER TABLE commandes DROP modifie_le, DROP modifie_par_id');
    }
}
