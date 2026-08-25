<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

final class Version20260822090000 extends AbstractMigration
{
    public function getDescription(): string
    {
        return "Ajoute la colonne devis.deleted (suppression douce, comme pour les "
            . "commandes) : le champ existait deja sur l'entite Devis et le "
            . "controleur/repository l'utilisaient deja, mais aucune migration ne "
            . "l'avait jamais creee en base.";
    }

    public function up(Schema $schema): void
    {
        $this->addSql(
            'ALTER TABLE devis ADD deleted TINYINT(1) NOT NULL DEFAULT 0'
        );
    }

    public function down(Schema $schema): void
    {
        $this->addSql('ALTER TABLE devis DROP deleted');
    }
}
