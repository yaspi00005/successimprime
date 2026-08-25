<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

final class Version20260820120000 extends AbstractMigration
{
    public function getDescription(): string
    {
        return "Passe commandes_details.remise d'un pourcentage (DECIMAL) a un montant fixe en FCFA (INT), "
            . "plus simple a saisir precisement qu'un pourcentage. Convertit les remises existantes en leur "
            . "equivalent FCFA a partir du total_ht deja enregistre, pour ne pas modifier les totaux des "
            . "commandes deja passees.";
    }

    public function up(Schema $schema): void
    {
        /*
         * La colonne reste DECIMAL(7,4) (max 999,9999) le temps du
         * calcul : un montant FCFA equivalent peut largement
         * depasser cette plage (ex. 2001 FCFA), il faut donc
         * elargir la colonne AVANT d'y ecrire, pas apres.
         */
        $this->addSql('ALTER TABLE commandes_details CHANGE remise remise NUMERIC(15, 4) NOT NULL DEFAULT 0');

        $this->addSql(
            'UPDATE commandes_details
             SET remise = CASE
                 WHEN remise > 0 AND remise < 100 THEN ROUND(total_ht * remise / (100 - remise))
                 ELSE 0
             END
             WHERE remise > 0'
        );

        $this->addSql('ALTER TABLE commandes_details CHANGE remise remise INT NOT NULL DEFAULT 0');
    }

    public function down(Schema $schema): void
    {
        $this->addSql('ALTER TABLE commandes_details CHANGE remise remise NUMERIC(7, 4) NOT NULL DEFAULT 0');
    }
}
