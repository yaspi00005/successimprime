<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260730164132 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE paiements DROP FOREIGN KEY `FK_E1B02E1282EA2E54`');
        $this->addSql('ALTER TABLE paiements ADD encaisse_par_id INT NOT NULL, CHANGE reference reference VARCHAR(255) DEFAULT NULL');
        $this->addSql('ALTER TABLE paiements ADD CONSTRAINT FK_E1B02E1282EA2E54 FOREIGN KEY (commande_id) REFERENCES commandes (id) ON DELETE CASCADE');
        $this->addSql('ALTER TABLE paiements ADD CONSTRAINT FK_E1B02E12A4FBCD6F FOREIGN KEY (encaisse_par_id) REFERENCES `user` (id)');
        $this->addSql('CREATE INDEX IDX_E1B02E12A4FBCD6F ON paiements (encaisse_par_id)');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE paiements DROP FOREIGN KEY FK_E1B02E1282EA2E54');
        $this->addSql('ALTER TABLE paiements DROP FOREIGN KEY FK_E1B02E12A4FBCD6F');
        $this->addSql('DROP INDEX IDX_E1B02E12A4FBCD6F ON paiements');
        $this->addSql('ALTER TABLE paiements DROP encaisse_par_id, CHANGE reference reference VARCHAR(255) NOT NULL');
        $this->addSql('ALTER TABLE paiements ADD CONSTRAINT `FK_E1B02E1282EA2E54` FOREIGN KEY (commande_id) REFERENCES commandes (id)');
    }
}
