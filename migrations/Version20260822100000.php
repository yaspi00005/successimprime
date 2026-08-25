<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

final class Version20260822100000 extends AbstractMigration
{
    public function getDescription(): string
    {
        return "Ajoute commandes.recupere_par_client, pour distinguer les "
            . "commandes retirées par le client lui-même des commandes "
            . "livrées par un livreur.";
    }

    public function up(Schema $schema): void
    {
        $this->addSql(
            'ALTER TABLE commandes ADD recupere_par_client TINYINT(1) NOT NULL DEFAULT 0'
        );
    }

    public function down(Schema $schema): void
    {
        $this->addSql('ALTER TABLE commandes DROP recupere_par_client');
    }
}
