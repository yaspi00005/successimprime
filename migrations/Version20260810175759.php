<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260810175759 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE devis_details ADD article_id INT DEFAULT NULL, CHANGE type_ligne type_ligne VARCHAR(20) DEFAULT \'produit\' NOT NULL');
        $this->addSql('ALTER TABLE devis_details ADD CONSTRAINT FK_E0C890D67294869C FOREIGN KEY (article_id) REFERENCES articles (id) ON DELETE SET NULL');
        $this->addSql('CREATE INDEX IDX_E0C890D67294869C ON devis_details (article_id)');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE devis_details DROP FOREIGN KEY FK_E0C890D67294869C');
        $this->addSql('DROP INDEX IDX_E0C890D67294869C ON devis_details');
        $this->addSql('ALTER TABLE devis_details DROP article_id, CHANGE type_ligne type_ligne VARCHAR(30) DEFAULT \'produit\' NOT NULL');
    }
}
