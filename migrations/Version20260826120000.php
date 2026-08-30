<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

final class Version20260826120000 extends AbstractMigration
{
    public function getDescription(): string
    {
        return "Ajoute machines.compteur_feuilles (compteur d'usure en "
            . "feuilles A4-equivalent, pour les machines facturees a la feuille).";
    }

    public function up(Schema $schema): void
    {
        $this->addSql(
            'ALTER TABLE machines ADD compteur_feuilles INT DEFAULT 0 NOT NULL'
        );
    }

    public function down(Schema $schema): void
    {
        $this->addSql('ALTER TABLE machines DROP compteur_feuilles');
    }
}
