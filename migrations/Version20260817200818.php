<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260817200818 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE commandes_details CHANGE remise remise NUMERIC(5, 2) DEFAULT 0 NOT NULL');
        $this->addSql('ALTER TABLE mouvement_tresorerie ADD verifie TINYINT DEFAULT 0 NOT NULL, ADD date_verification DATETIME DEFAULT NULL, ADD verifie_par_id INT DEFAULT NULL');
        $this->addSql('ALTER TABLE mouvement_tresorerie ADD CONSTRAINT FK_516E7468A5CB0CEF FOREIGN KEY (verifie_par_id) REFERENCES `user` (id) ON DELETE SET NULL');
        $this->addSql('CREATE INDEX IDX_516E7468A5CB0CEF ON mouvement_tresorerie (verifie_par_id)');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE commandes_details CHANGE remise remise NUMERIC(5, 2) DEFAULT \'0.00\' NOT NULL');
        $this->addSql('ALTER TABLE mouvement_tresorerie DROP FOREIGN KEY FK_516E7468A5CB0CEF');
        $this->addSql('DROP INDEX IDX_516E7468A5CB0CEF ON mouvement_tresorerie');
        $this->addSql('ALTER TABLE mouvement_tresorerie DROP verifie, DROP date_verification, DROP verifie_par_id');
    }
}
