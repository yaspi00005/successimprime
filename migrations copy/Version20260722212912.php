<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260722212912 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE user DROP FOREIGN KEY `FK_8D93D649F971F91F`');
        $this->addSql('DROP INDEX UNIQ_8D93D649F971F91F ON user');
        $this->addSql('ALTER TABLE user CHANGE employes_id employe_id INT NOT NULL');
        $this->addSql('ALTER TABLE user ADD CONSTRAINT FK_8D93D6491B65292 FOREIGN KEY (employe_id) REFERENCES employes (id)');
        $this->addSql('CREATE UNIQUE INDEX UNIQ_8D93D6491B65292 ON user (employe_id)');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE `user` DROP FOREIGN KEY FK_8D93D6491B65292');
        $this->addSql('DROP INDEX UNIQ_8D93D6491B65292 ON `user`');
        $this->addSql('ALTER TABLE `user` CHANGE employe_id employes_id INT NOT NULL');
        $this->addSql('ALTER TABLE `user` ADD CONSTRAINT `FK_8D93D649F971F91F` FOREIGN KEY (employes_id) REFERENCES employes (id)');
        $this->addSql('CREATE UNIQUE INDEX UNIQ_8D93D649F971F91F ON `user` (employes_id)');
    }
}
