<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

final class Version20260817120000 extends AbstractMigration
{
    public function getDescription(): string
    {
        return "Ajoute type_compte (entreprise/particulier) sur clients, independant de type_client (B2B/B2C qui reste reserve a la tarification) ; ajoute les champs de facturation a un tiers (facturer_a_un_tiers, nom/adresse/telephone/email_facturation) sur devis et factures.";
    }

    public function up(Schema $schema): void
    {
        $this->addSql("ALTER TABLE clients ADD type_compte VARCHAR(20) NOT NULL DEFAULT 'particulier'");
        $this->addSql("UPDATE clients SET type_compte = 'entreprise' WHERE type_client = 'B2B'");

        $this->addSql('ALTER TABLE devis ADD facturer_a_un_tiers TINYINT(1) NOT NULL DEFAULT 0, ADD nom_facturation VARCHAR(150) DEFAULT NULL, ADD adresse_facturation VARCHAR(255) DEFAULT NULL, ADD telephone_facturation VARCHAR(30) DEFAULT NULL, ADD email_facturation VARCHAR(255) DEFAULT NULL');

        $this->addSql('ALTER TABLE factures ADD facturer_a_un_tiers TINYINT(1) NOT NULL DEFAULT 0, ADD nom_facturation VARCHAR(150) DEFAULT NULL, ADD adresse_facturation VARCHAR(255) DEFAULT NULL, ADD telephone_facturation VARCHAR(30) DEFAULT NULL, ADD email_facturation VARCHAR(255) DEFAULT NULL');
    }

    public function down(Schema $schema): void
    {
        $this->addSql('ALTER TABLE clients DROP type_compte');
        $this->addSql('ALTER TABLE devis DROP facturer_a_un_tiers, DROP nom_facturation, DROP adresse_facturation, DROP telephone_facturation, DROP email_facturation');
        $this->addSql('ALTER TABLE factures DROP facturer_a_un_tiers, DROP nom_facturation, DROP adresse_facturation, DROP telephone_facturation, DROP email_facturation');
    }
}
