<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

final class Version20260821140000 extends AbstractMigration
{
    public function getDescription(): string
    {
        return "Ajoute les pieces jointes (fichier/image) aux messages du chat interne.";
    }

    public function up(Schema $schema): void
    {
        $this->addSql(
            'ALTER TABLE messages_chat ADD piece_jointe_fichier VARCHAR(255) DEFAULT NULL, '
            . 'ADD piece_jointe_nom_original VARCHAR(255) DEFAULT NULL'
        );
    }

    public function down(Schema $schema): void
    {
        $this->addSql(
            'ALTER TABLE messages_chat DROP piece_jointe_fichier, DROP piece_jointe_nom_original'
        );
    }
}
