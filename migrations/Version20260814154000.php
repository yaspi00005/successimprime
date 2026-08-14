<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

final class Version20260814154000 extends AbstractMigration
{
    public function getDescription(): string
    {
        return 'Transforme commandes_details.remise en DECIMAL(5,2) pour supporter les remises B2B décimales.';
    }

    public function up(Schema $schema): void
    {
        /*
         * ========================================================
         * REMISE DE LIGNE
         * ========================================================
         *
         * Ancien format :
         *
         * INT NOT NULL DEFAULT 0
         *
         * Nouveau format :
         *
         * DECIMAL(5,2) NOT NULL DEFAULT 0.00
         *
         * Les anciennes valeurs 0, 5, 10, 20...
         * deviennent automatiquement :
         *
         * 0.00
         * 5.00
         * 10.00
         * 20.00
         */
        $this->addSql(
            "ALTER TABLE commandes_details
             MODIFY remise DECIMAL(5,2)
             NOT NULL DEFAULT 0.00"
        );
    }

    public function down(Schema $schema): void
    {
        /*
         * ATTENTION :
         *
         * Un retour arrière arrondit les éventuelles
         * remises décimales.
         *
         * Exemple :
         *
         * 14.29 -> 14
         */
        $this->addSql(
            "UPDATE commandes_details
             SET remise = ROUND(remise)"
        );

        $this->addSql(
            "ALTER TABLE commandes_details
             MODIFY remise INT
             NOT NULL DEFAULT 0"
        );
    }
}