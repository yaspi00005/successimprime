<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

final class Version20260820100000 extends AbstractMigration
{
    public function getDescription(): string
    {
        return "Ajoute la table parametres_paiement (taux frais de retrait / fonds de soutien mobile money) "
            . "et les colonnes correspondantes sur paiements (frais_retrait_inclus, fonds_soutien_inclus, "
            . "montant_frais_retrait, montant_fonds_soutien).";
    }

    public function up(Schema $schema): void
    {
        $this->addSql('CREATE TABLE parametres_paiement (
            id INT AUTO_INCREMENT NOT NULL,
            taux_frais_retrait DOUBLE PRECISION DEFAULT 1.0 NOT NULL,
            taux_fonds_soutien DOUBLE PRECISION DEFAULT 1.0 NOT NULL,
            PRIMARY KEY(id)
        ) DEFAULT CHARACTER SET utf8mb4 COLLATE `utf8mb4_unicode_ci` ENGINE = InnoDB');

        $this->addSql('INSERT INTO parametres_paiement (taux_frais_retrait, taux_fonds_soutien) VALUES (1.0, 1.0)');

        $this->addSql('ALTER TABLE paiements
            ADD frais_retrait_inclus TINYINT(1) DEFAULT 0 NOT NULL,
            ADD fonds_soutien_inclus TINYINT(1) DEFAULT 0 NOT NULL,
            ADD montant_frais_retrait INT DEFAULT 0 NOT NULL,
            ADD montant_fonds_soutien INT DEFAULT 0 NOT NULL');
    }

    public function down(Schema $schema): void
    {
        $this->addSql('ALTER TABLE paiements
            DROP frais_retrait_inclus,
            DROP fonds_soutien_inclus,
            DROP montant_frais_retrait,
            DROP montant_fonds_soutien');

        $this->addSql('DROP TABLE parametres_paiement');
    }
}
