<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260726153341 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('CREATE TABLE support_types_impression (supports_id INT NOT NULL, types_impression_id INT NOT NULL, INDEX IDX_EE1AA14497185C1E (supports_id), INDEX IDX_EE1AA1449719B876 (types_impression_id), PRIMARY KEY (supports_id, types_impression_id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('CREATE TABLE support_format (supports_id INT NOT NULL, format_id INT NOT NULL, INDEX IDX_5640922F97185C1E (supports_id), INDEX IDX_5640922FD629F605 (format_id), PRIMARY KEY (supports_id, format_id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('CREATE TABLE support_finition (supports_id INT NOT NULL, finition_id INT NOT NULL, INDEX IDX_94D6731997185C1E (supports_id), INDEX IDX_94D67319CB56F5AF (finition_id), PRIMARY KEY (supports_id, finition_id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('ALTER TABLE support_types_impression ADD CONSTRAINT FK_EE1AA14497185C1E FOREIGN KEY (supports_id) REFERENCES supports (id) ON DELETE CASCADE');
        $this->addSql('ALTER TABLE support_types_impression ADD CONSTRAINT FK_EE1AA1449719B876 FOREIGN KEY (types_impression_id) REFERENCES types_impression (id) ON DELETE CASCADE');
        $this->addSql('ALTER TABLE support_format ADD CONSTRAINT FK_5640922F97185C1E FOREIGN KEY (supports_id) REFERENCES supports (id) ON DELETE CASCADE');
        $this->addSql('ALTER TABLE support_format ADD CONSTRAINT FK_5640922FD629F605 FOREIGN KEY (format_id) REFERENCES format (id) ON DELETE CASCADE');
        $this->addSql('ALTER TABLE support_finition ADD CONSTRAINT FK_94D6731997185C1E FOREIGN KEY (supports_id) REFERENCES supports (id) ON DELETE CASCADE');
        $this->addSql('ALTER TABLE support_finition ADD CONSTRAINT FK_94D67319CB56F5AF FOREIGN KEY (finition_id) REFERENCES finition (id) ON DELETE CASCADE');
        $this->addSql('ALTER TABLE commandes_details ADD supports_id INT DEFAULT NULL');
        $this->addSql('ALTER TABLE commandes_details ADD CONSTRAINT FK_B48B83DA97185C1E FOREIGN KEY (supports_id) REFERENCES supports (id)');
        $this->addSql('CREATE INDEX IDX_B48B83DA97185C1E ON commandes_details (supports_id)');
        $this->addSql('ALTER TABLE supports ADD description LONGTEXT NOT NULL, ADD publie TINYINT NOT NULL, ADD ordre INT NOT NULL');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE support_types_impression DROP FOREIGN KEY FK_EE1AA14497185C1E');
        $this->addSql('ALTER TABLE support_types_impression DROP FOREIGN KEY FK_EE1AA1449719B876');
        $this->addSql('ALTER TABLE support_format DROP FOREIGN KEY FK_5640922F97185C1E');
        $this->addSql('ALTER TABLE support_format DROP FOREIGN KEY FK_5640922FD629F605');
        $this->addSql('ALTER TABLE support_finition DROP FOREIGN KEY FK_94D6731997185C1E');
        $this->addSql('ALTER TABLE support_finition DROP FOREIGN KEY FK_94D67319CB56F5AF');
        $this->addSql('DROP TABLE support_types_impression');
        $this->addSql('DROP TABLE support_format');
        $this->addSql('DROP TABLE support_finition');
        $this->addSql('ALTER TABLE commandes_details DROP FOREIGN KEY FK_B48B83DA97185C1E');
        $this->addSql('DROP INDEX IDX_B48B83DA97185C1E ON commandes_details');
        $this->addSql('ALTER TABLE commandes_details DROP supports_id');
        $this->addSql('ALTER TABLE supports DROP description, DROP publie, DROP ordre');
    }
}
