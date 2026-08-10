<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260809222234 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('CREATE TABLE stock_reservation (id INT AUTO_INCREMENT NOT NULL, quantite NUMERIC(14, 3) NOT NULL, statut VARCHAR(30) DEFAULT \'active\' NOT NULL, date_reservation DATETIME NOT NULL, date_liberation DATETIME DEFAULT NULL, date_consommation DATETIME DEFAULT NULL, observation VARCHAR(255) DEFAULT NULL, article_id INT NOT NULL, commande_detail_id INT NOT NULL, INDEX idx_stock_reservation_article (article_id), INDEX idx_stock_reservation_detail (commande_detail_id), INDEX idx_stock_reservation_statut (statut), PRIMARY KEY (id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('ALTER TABLE stock_reservation ADD CONSTRAINT FK_9D06EF617294869C FOREIGN KEY (article_id) REFERENCES articles (id) ON DELETE RESTRICT');
        $this->addSql('ALTER TABLE stock_reservation ADD CONSTRAINT FK_9D06EF61C8DC59F9 FOREIGN KEY (commande_detail_id) REFERENCES commandes_details (id) ON DELETE CASCADE');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE stock_reservation DROP FOREIGN KEY FK_9D06EF617294869C');
        $this->addSql('ALTER TABLE stock_reservation DROP FOREIGN KEY FK_9D06EF61C8DC59F9');
        $this->addSql('DROP TABLE stock_reservation');
    }
}
