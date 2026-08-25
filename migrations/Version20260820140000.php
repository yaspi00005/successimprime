<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

final class Version20260820140000 extends AbstractMigration
{
    /**
     * Expression SQL du "facteur" d'une ligne (nombre d'unités
     * facturables), identique à DevisDetails::calculerFacteur().
     */
    private const FACTEUR_SQL = "CASE mode_calcul
        WHEN 'forfait' THEN 1
        WHEN 'metre' THEN GREATEST(COALESCE(longueur, 0) * quantite, 0.0001)
        WHEN 'metre_carre' THEN GREATEST(COALESCE(surface, 0) * quantite, 0.0001)
        WHEN 'face' THEN GREATEST(nombre_faces, 1) * quantite
        ELSE quantite
    END";

    public function getDescription(): string
    {
        return "Passe devis_details.remise d'un pourcentage (DECIMAL) a un montant en FCFA "
            . "par unite facturable (INT), aligne sur le module commande (Version20260820120000 "
            . "+ Version20260820130000). Convertit les remises existantes en leur equivalent "
            . "par unite a partir du total_ht deja enregistre, pour ne pas modifier les totaux "
            . "des devis deja enregistres.";
    }

    public function up(Schema $schema): void
    {
        /*
         * La colonne reste DECIMAL le temps du calcul : un montant
         * FCFA equivalent peut largement depasser la plage DECIMAL(7,4)
         * (max 999,9999), il faut donc elargir la colonne AVANT d'y
         * ecrire, pas apres.
         */
        $this->addSql('ALTER TABLE devis_details CHANGE remise remise NUMERIC(15, 4) NOT NULL DEFAULT 0');

        $this->addSql(
            'UPDATE devis_details
             SET remise = CASE
                 WHEN remise > 0 AND remise < 100 THEN
                     ROUND(
                         (total_ht * remise / (100 - remise))
                         / (' . self::FACTEUR_SQL . ')
                     )
                 ELSE 0
             END
             WHERE remise > 0'
        );

        $this->addSql('ALTER TABLE devis_details CHANGE remise remise INT NOT NULL DEFAULT 0');
    }

    public function down(Schema $schema): void
    {
        $this->addSql('ALTER TABLE devis_details CHANGE remise remise NUMERIC(7, 4) NOT NULL DEFAULT 0');
    }
}
