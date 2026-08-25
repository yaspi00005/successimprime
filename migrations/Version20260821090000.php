<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

final class Version20260821090000 extends AbstractMigration
{
    public function getDescription(): string
    {
        return "Ajoute reclamations.notification_lue : suit si l'agent a deja vu la notification "
            . "\"reclamation validee, passez a la caisse\" dans la cloche de notifications.";
    }

    public function up(Schema $schema): void
    {
        $this->addSql('ALTER TABLE reclamations ADD notification_lue TINYINT(1) NOT NULL DEFAULT 0');
    }

    public function down(Schema $schema): void
    {
        $this->addSql('ALTER TABLE reclamations DROP notification_lue');
    }
}
