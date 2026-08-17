<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260817154824 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE commandes_details CHANGE remise remise NUMERIC(5, 2) DEFAULT 0 NOT NULL');
        $this->addSql('ALTER TABLE devis CHANGE facturer_a_un_tiers facturer_aun_tiers TINYINT DEFAULT 0 NOT NULL');
        $this->addSql('ALTER TABLE factures CHANGE facturer_a_un_tiers facturer_aun_tiers TINYINT DEFAULT 0 NOT NULL');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE commandes_details CHANGE remise remise NUMERIC(5, 2) DEFAULT \'0.00\' NOT NULL');
        $this->addSql('ALTER TABLE devis CHANGE facturer_aun_tiers facturer_a_un_tiers TINYINT DEFAULT 0 NOT NULL');
        $this->addSql('ALTER TABLE factures CHANGE facturer_aun_tiers facturer_a_un_tiers TINYINT DEFAULT 0 NOT NULL');
    }
}
