<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

final class Version20260821100000 extends AbstractMigration
{
    public function getDescription(): string
    {
        return "Cree la table notifications (cloche du gabarit de base) : nouvelle commande/devis, "
            . "paiement recu, etape de production, stock bas.";
    }

    public function up(Schema $schema): void
    {
        $this->addSql(
            'CREATE TABLE notifications (
                id INT AUTO_INCREMENT NOT NULL,
                destinataire_id INT NOT NULL,
                message VARCHAR(255) NOT NULL,
                route VARCHAR(100) DEFAULT NULL,
                route_parametres JSON DEFAULT NULL,
                lue TINYINT(1) NOT NULL DEFAULT 0,
                date_creation DATETIME NOT NULL,
                INDEX idx_notification_destinataire_lue (destinataire_id, lue),
                PRIMARY KEY(id)
            ) DEFAULT CHARACTER SET utf8mb4 COLLATE `utf8mb4_unicode_ci` ENGINE = InnoDB'
        );

        $this->addSql(
            'ALTER TABLE notifications ADD CONSTRAINT FK_notifications_destinataire
             FOREIGN KEY (destinataire_id) REFERENCES `user` (id) ON DELETE CASCADE'
        );
    }

    public function down(Schema $schema): void
    {
        $this->addSql('DROP TABLE notifications');
    }
}
