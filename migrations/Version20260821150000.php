<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

final class Version20260821150000 extends AbstractMigration
{
    public function getDescription(): string
    {
        return "Ajoute conversations.jeton (identifiant opaque utilise dans l'URL a la "
            . "place de l'id numerique) et le remplit pour les conversations existantes.";
    }

    public function up(Schema $schema): void
    {
        $this->addSql(
            'ALTER TABLE conversations ADD jeton VARCHAR(32) DEFAULT NULL'
        );

        $this->addSql(
            "UPDATE conversations SET jeton = LOWER(SUBSTRING(REPLACE(UUID(), '-', ''), 1, 32)) WHERE jeton IS NULL"
        );

        $this->addSql(
            'ALTER TABLE conversations CHANGE jeton jeton VARCHAR(32) NOT NULL'
        );

        $this->addSql(
            'ALTER TABLE conversations ADD UNIQUE INDEX uniq_conversation_jeton (jeton)'
        );
    }

    public function down(Schema $schema): void
    {
        $this->addSql('ALTER TABLE conversations DROP INDEX uniq_conversation_jeton');
        $this->addSql('ALTER TABLE conversations DROP jeton');
    }
}
