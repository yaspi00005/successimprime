<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

final class Version20260820130000 extends AbstractMigration
{
    /**
     * Expression SQL du "facteur" d'une ligne (nombre d'unités
     * facturables), identique à CommandesDetails::calculerFacteur().
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
        return "Corrige la remise de commandes_details pour qu'elle s'applique par unite "
            . "facturable (ex. par m2) et non plus comme un montant fixe sur toute la ligne. "
            . "Detecte automatiquement si la migration precedente (Version20260820120000, "
            . "conversion pourcentage -> montant fixe) a deja ete executee ou non, pour "
            . "reconvertir correctement les remises existantes dans les deux cas.";
    }

    public function up(Schema $schema): void
    {
        $typeActuel = $this->connection->fetchOne(
            'SELECT DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS
             WHERE TABLE_SCHEMA = DATABASE()
               AND TABLE_NAME = \'commandes_details\'
               AND COLUMN_NAME = \'remise\''
        );

        if ($typeActuel === 'decimal') {
            /*
             * Version20260820120000 n'a pas encore converti la colonne
             * en INT : remise contient encore l'ancien pourcentage.
             * On convertit directement pourcentage -> montant par
             * unite, sans passer par l'etape intermediaire "montant
             * fixe sur la ligne".
             */
            $this->addSql(
                'ALTER TABLE commandes_details CHANGE remise remise NUMERIC(15, 4) NOT NULL DEFAULT 0'
            );

            $this->addSql(
                'UPDATE commandes_details
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

            $this->addSql('ALTER TABLE commandes_details CHANGE remise remise INT NOT NULL DEFAULT 0');

            return;
        }

        /*
         * Version20260820120000 a deja converti remise en INT
         * (montant fixe en FCFA sur toute la ligne). On la
         * reconvertit en montant par unite en la divisant par le
         * facteur de la ligne.
         */
        $this->addSql(
            'UPDATE commandes_details
             SET remise = ROUND(remise / (' . self::FACTEUR_SQL . '))
             WHERE remise > 0'
        );
    }

    public function down(Schema $schema): void
    {
        /*
         * Reconversion en montant fixe sur toute la ligne (inverse de
         * la branche "deja en INT" ci-dessus). Comme pour
         * Version20260820120000, on ne revient pas au pourcentage
         * d'origine : cette conversion est volontairement a sens
         * unique.
         */
        $this->addSql(
            'UPDATE commandes_details
             SET remise = ROUND(remise * (' . self::FACTEUR_SQL . '))
             WHERE remise > 0'
        );
    }
}
