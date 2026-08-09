<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260727230327 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE commande_detail_fichier ADD jeton_upload VARCHAR(64) NOT NULL, ADD morceaux_recus INT DEFAULT 0 NOT NULL, ADD nombre_morceaux INT DEFAULT NULL, ADD termine_le DATETIME DEFAULT NULL, CHANGE commande_detail_id commande_detail_id INT DEFAULT NULL');
        $this->addSql('CREATE UNIQUE INDEX UNIQ_39E2DA1052C87F80 ON commande_detail_fichier (jeton_upload)');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('DROP INDEX UNIQ_39E2DA1052C87F80 ON commande_detail_fichier');
        $this->addSql('ALTER TABLE commande_detail_fichier DROP jeton_upload, DROP morceaux_recus, DROP nombre_morceaux, DROP termine_le, CHANGE commande_detail_id commande_detail_id INT NOT NULL');
    }
}
