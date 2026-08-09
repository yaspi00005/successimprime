<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260726163204 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE support_types_impression DROP FOREIGN KEY `FK_EE1AA14497185C1E`');
        $this->addSql('DROP INDEX IDX_EE1AA14497185C1E ON support_types_impression');
        $this->addSql('ALTER TABLE support_types_impression CHANGE supports_id support_id INT NOT NULL, DROP PRIMARY KEY, ADD PRIMARY KEY (support_id, types_impression_id)');
        $this->addSql('ALTER TABLE support_types_impression ADD CONSTRAINT FK_EE1AA144315B405 FOREIGN KEY (support_id) REFERENCES supports (id) ON DELETE CASCADE');
        $this->addSql('CREATE INDEX IDX_EE1AA144315B405 ON support_types_impression (support_id)');
        $this->addSql('ALTER TABLE support_format DROP FOREIGN KEY `FK_5640922F97185C1E`');
        $this->addSql('DROP INDEX IDX_5640922F97185C1E ON support_format');
        $this->addSql('ALTER TABLE support_format CHANGE supports_id support_id INT NOT NULL, DROP PRIMARY KEY, ADD PRIMARY KEY (support_id, format_id)');
        $this->addSql('ALTER TABLE support_format ADD CONSTRAINT FK_5640922F315B405 FOREIGN KEY (support_id) REFERENCES supports (id) ON DELETE CASCADE');
        $this->addSql('CREATE INDEX IDX_5640922F315B405 ON support_format (support_id)');
        $this->addSql('ALTER TABLE support_finition DROP FOREIGN KEY `FK_94D6731997185C1E`');
        $this->addSql('DROP INDEX IDX_94D6731997185C1E ON support_finition');
        $this->addSql('ALTER TABLE support_finition CHANGE supports_id support_id INT NOT NULL, DROP PRIMARY KEY, ADD PRIMARY KEY (support_id, finition_id)');
        $this->addSql('ALTER TABLE support_finition ADD CONSTRAINT FK_94D67319315B405 FOREIGN KEY (support_id) REFERENCES supports (id) ON DELETE CASCADE');
        $this->addSql('CREATE INDEX IDX_94D67319315B405 ON support_finition (support_id)');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE support_finition DROP FOREIGN KEY FK_94D67319315B405');
        $this->addSql('DROP INDEX IDX_94D67319315B405 ON support_finition');
        $this->addSql('ALTER TABLE support_finition CHANGE support_id supports_id INT NOT NULL, DROP PRIMARY KEY, ADD PRIMARY KEY (supports_id, finition_id)');
        $this->addSql('ALTER TABLE support_finition ADD CONSTRAINT `FK_94D6731997185C1E` FOREIGN KEY (supports_id) REFERENCES supports (id) ON DELETE CASCADE');
        $this->addSql('CREATE INDEX IDX_94D6731997185C1E ON support_finition (supports_id)');
        $this->addSql('ALTER TABLE support_format DROP FOREIGN KEY FK_5640922F315B405');
        $this->addSql('DROP INDEX IDX_5640922F315B405 ON support_format');
        $this->addSql('ALTER TABLE support_format CHANGE support_id supports_id INT NOT NULL, DROP PRIMARY KEY, ADD PRIMARY KEY (supports_id, format_id)');
        $this->addSql('ALTER TABLE support_format ADD CONSTRAINT `FK_5640922F97185C1E` FOREIGN KEY (supports_id) REFERENCES supports (id) ON DELETE CASCADE');
        $this->addSql('CREATE INDEX IDX_5640922F97185C1E ON support_format (supports_id)');
        $this->addSql('ALTER TABLE support_types_impression DROP FOREIGN KEY FK_EE1AA144315B405');
        $this->addSql('DROP INDEX IDX_EE1AA144315B405 ON support_types_impression');
        $this->addSql('ALTER TABLE support_types_impression CHANGE support_id supports_id INT NOT NULL, DROP PRIMARY KEY, ADD PRIMARY KEY (supports_id, types_impression_id)');
        $this->addSql('ALTER TABLE support_types_impression ADD CONSTRAINT `FK_EE1AA14497185C1E` FOREIGN KEY (supports_id) REFERENCES supports (id) ON DELETE CASCADE');
        $this->addSql('CREATE INDEX IDX_EE1AA14497185C1E ON support_types_impression (supports_id)');
    }
}
