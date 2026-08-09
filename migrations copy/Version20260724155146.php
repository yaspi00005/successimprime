<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260724155146 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('CREATE TABLE finition_types_impression (finition_id INT NOT NULL, types_impression_id INT NOT NULL, INDEX IDX_4EB60CFECB56F5AF (finition_id), INDEX IDX_4EB60CFE9719B876 (types_impression_id), PRIMARY KEY (finition_id, types_impression_id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('ALTER TABLE finition_types_impression ADD CONSTRAINT FK_4EB60CFECB56F5AF FOREIGN KEY (finition_id) REFERENCES finition (id) ON DELETE CASCADE');
        $this->addSql('ALTER TABLE finition_types_impression ADD CONSTRAINT FK_4EB60CFE9719B876 FOREIGN KEY (types_impression_id) REFERENCES types_impression (id) ON DELETE CASCADE');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE finition_types_impression DROP FOREIGN KEY FK_4EB60CFECB56F5AF');
        $this->addSql('ALTER TABLE finition_types_impression DROP FOREIGN KEY FK_4EB60CFE9719B876');
        $this->addSql('DROP TABLE finition_types_impression');
    }
}
