<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

final class Version20260816120000 extends AbstractMigration
{
    public function getDescription(): string
    {
        return "Passe commandes_details.remise de INT a DECIMAL(5,2) pour autoriser les pourcentages decimaux (remise B2B exacte, sans arrondi premature).";
    }

    public function up(Schema $schema): void
    {
        $this->addSql('ALTER TABLE commandes_details CHANGE remise remise NUMERIC(5, 2) NOT NULL DEFAULT 0');
    }

    public function down(Schema $schema): void
    {
        $this->addSql('ALTER TABLE commandes_details CHANGE remise remise INT NOT NULL DEFAULT 0');
    }
}
