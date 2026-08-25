<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

final class Version20260821130000 extends AbstractMigration
{
    public function getDescription(): string
    {
        return "Cree les tables de la messagerie interne (chat) : conversations, "
            . "conversation_participants, messages_chat.";
    }

    public function up(Schema $schema): void
    {
        $this->addSql(
            'CREATE TABLE conversations (
                id INT AUTO_INCREMENT NOT NULL,
                date_creation DATETIME NOT NULL,
                date_dernier_message DATETIME DEFAULT NULL,
                PRIMARY KEY(id)
            ) DEFAULT CHARACTER SET utf8mb4 COLLATE `utf8mb4_unicode_ci` ENGINE = InnoDB'
        );

        $this->addSql(
            'CREATE TABLE conversation_participants (
                id INT AUTO_INCREMENT NOT NULL,
                conversation_id INT NOT NULL,
                utilisateur_id INT NOT NULL,
                date_derniere_lecture DATETIME DEFAULT NULL,
                UNIQUE INDEX uniq_conversation_utilisateur (conversation_id, utilisateur_id),
                INDEX idx_conversation_participant_utilisateur (utilisateur_id),
                PRIMARY KEY(id)
            ) DEFAULT CHARACTER SET utf8mb4 COLLATE `utf8mb4_unicode_ci` ENGINE = InnoDB'
        );

        $this->addSql(
            'CREATE TABLE messages_chat (
                id INT AUTO_INCREMENT NOT NULL,
                conversation_id INT NOT NULL,
                auteur_id INT NOT NULL,
                contenu LONGTEXT NOT NULL,
                date_envoi DATETIME NOT NULL,
                INDEX idx_message_conversation (conversation_id),
                PRIMARY KEY(id)
            ) DEFAULT CHARACTER SET utf8mb4 COLLATE `utf8mb4_unicode_ci` ENGINE = InnoDB'
        );

        $this->addSql(
            'ALTER TABLE conversation_participants ADD CONSTRAINT FK_conv_part_conversation
             FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE'
        );

        $this->addSql(
            'ALTER TABLE conversation_participants ADD CONSTRAINT FK_conv_part_utilisateur
             FOREIGN KEY (utilisateur_id) REFERENCES `user` (id) ON DELETE CASCADE'
        );

        $this->addSql(
            'ALTER TABLE messages_chat ADD CONSTRAINT FK_messages_chat_conversation
             FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE'
        );

        $this->addSql(
            'ALTER TABLE messages_chat ADD CONSTRAINT FK_messages_chat_auteur
             FOREIGN KEY (auteur_id) REFERENCES `user` (id) ON DELETE CASCADE'
        );
    }

    public function down(Schema $schema): void
    {
        $this->addSql('DROP TABLE messages_chat');
        $this->addSql('DROP TABLE conversation_participants');
        $this->addSql('DROP TABLE conversations');
    }
}
