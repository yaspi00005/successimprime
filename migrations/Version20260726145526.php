<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260726145526 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('CREATE TABLE format_types_impression (format_id INT NOT NULL, types_impression_id INT NOT NULL, INDEX IDX_5CE0BAD8D629F605 (format_id), INDEX IDX_5CE0BAD89719B876 (types_impression_id), PRIMARY KEY (format_id, types_impression_id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('ALTER TABLE format_types_impression ADD CONSTRAINT FK_5CE0BAD8D629F605 FOREIGN KEY (format_id) REFERENCES format (id) ON DELETE CASCADE');
        $this->addSql('ALTER TABLE format_types_impression ADD CONSTRAINT FK_5CE0BAD89719B876 FOREIGN KEY (types_impression_id) REFERENCES types_impression (id) ON DELETE CASCADE');
        $this->addSql('ALTER TABLE format ADD unite VARCHAR(10) NOT NULL, ADD description LONGTEXT NOT NULL, ADD publie TINYINT NOT NULL, ADD ordre INT NOT NULL, CHANGE nom nom VARCHAR(150) NOT NULL, CHANGE hauteur hauteur INT NOT NULL');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE format_types_impression DROP FOREIGN KEY FK_5CE0BAD8D629F605');
        $this->addSql('ALTER TABLE format_types_impression DROP FOREIGN KEY FK_5CE0BAD89719B876');
        $this->addSql('DROP TABLE format_types_impression');
        $this->addSql('ALTER TABLE format DROP unite, DROP description, DROP publie, DROP ordre, CHANGE nom nom VARCHAR(255) NOT NULL, CHANGE hauteur hauteur VARCHAR(255) NOT NULL');
    }
}
