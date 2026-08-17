<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

final class Version20260816130000 extends AbstractMigration
{
    public function getDescription(): string
    {
        return "Ajoute la colonne emetteur sur devis (memes valeurs que factures : drepa, mdg_success, mdg), pour que le PDF du devis reprenne les 3 en-tetes du PDF de facture.";
    }

    public function up(Schema $schema): void
    {
        $this->addSql("ALTER TABLE devis ADD emetteur VARCHAR(30) NOT NULL DEFAULT 'mdg_success'");
    }

    public function down(Schema $schema): void
    {
        $this->addSql('ALTER TABLE devis DROP emetteur');
    }
}
