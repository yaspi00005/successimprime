<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260804224752 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE mouvement_tresorerie ADD agent_id INT DEFAULT NULL');
        $this->addSql('ALTER TABLE mouvement_tresorerie ADD CONSTRAINT FK_516E74683414710B FOREIGN KEY (agent_id) REFERENCES `user` (id) ON DELETE SET NULL');
        $this->addSql('CREATE INDEX IDX_516E74683414710B ON mouvement_tresorerie (agent_id)');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE mouvement_tresorerie DROP FOREIGN KEY FK_516E74683414710B');
        $this->addSql('DROP INDEX IDX_516E74683414710B ON mouvement_tresorerie');
        $this->addSql('ALTER TABLE mouvement_tresorerie DROP agent_id');
    }
}
