<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260810142109 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE articles ADD vendable TINYINT DEFAULT 0 NOT NULL');
        $this->addSql('ALTER TABLE commandes_details ADD article_id INT DEFAULT NULL, CHANGE type_ligne type_ligne VARCHAR(20) DEFAULT \'produit\' NOT NULL');
        $this->addSql('ALTER TABLE commandes_details ADD CONSTRAINT FK_B48B83DA7294869C FOREIGN KEY (article_id) REFERENCES articles (id) ON DELETE SET NULL');
        $this->addSql('CREATE INDEX IDX_B48B83DA7294869C ON commandes_details (article_id)');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE articles DROP vendable');
        $this->addSql('ALTER TABLE commandes_details DROP FOREIGN KEY FK_B48B83DA7294869C');
        $this->addSql('DROP INDEX IDX_B48B83DA7294869C ON commandes_details');
        $this->addSql('ALTER TABLE commandes_details DROP article_id, CHANGE type_ligne type_ligne VARCHAR(30) DEFAULT \'produit\' NOT NULL');
    }
}
