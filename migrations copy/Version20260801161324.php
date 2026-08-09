<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260801161324 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE commandes_details DROP FOREIGN KEY `FK_B48B83DAF347EFB`');
        $this->addSql('ALTER TABLE commandes_details ADD mode_calcul VARCHAR(30) DEFAULT \'unite\' NOT NULL, CHANGE produit_id produit_id INT DEFAULT NULL');
        $this->addSql('ALTER TABLE commandes_details ADD CONSTRAINT FK_B48B83DAF347EFB FOREIGN KEY (produit_id) REFERENCES produits (id) ON DELETE SET NULL');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE commandes_details DROP FOREIGN KEY FK_B48B83DAF347EFB');
        $this->addSql('ALTER TABLE commandes_details DROP mode_calcul, CHANGE produit_id produit_id INT NOT NULL');
        $this->addSql('ALTER TABLE commandes_details ADD CONSTRAINT `FK_B48B83DAF347EFB` FOREIGN KEY (produit_id) REFERENCES produits (id)');
    }
}
