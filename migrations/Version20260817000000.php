<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

final class Version20260817000000 extends AbstractMigration
{
    public function getDescription(): string
    {
        return "Ajoute le suivi de rentabilite/amortissement sur machines (mode de facturation metre_carre/feuille, prix d'achat, duree d'amortissement, revenu recapitule avant suivi applicatif) et seed le recap Traceur 1.8 issu du classeur Amortissement.";
    }

    public function up(Schema $schema): void
    {
        $this->addSql("ALTER TABLE machines ADD mode_facturation VARCHAR(20) NOT NULL DEFAULT 'metre_carre', ADD prix_achat INT DEFAULT NULL, ADD duree_amortissement_mois INT DEFAULT NULL, ADD revenu_avant_suivi INT NOT NULL DEFAULT 0, ADD date_debut_suivi DATE DEFAULT NULL");

        /*
         * Recap du classeur "Amortissement" (Traceur 1.8) : 13 243 916 F CFA
         * factures entre janvier et aout 2026, avant le debut du suivi
         * applicatif via les commandes liees a la machine. Sans effet si
         * aucune machine "Traceur 1.8" n'existe encore.
         */
        $this->addSql("UPDATE machines SET mode_facturation = 'metre_carre', revenu_avant_suivi = 13243916, date_debut_suivi = '2026-08-17' WHERE nom LIKE '%Traceur 1.8%'");
    }

    public function down(Schema $schema): void
    {
        $this->addSql('ALTER TABLE machines DROP mode_facturation, DROP prix_achat, DROP duree_amortissement_mois, DROP revenu_avant_suivi, DROP date_debut_suivi');
    }
}
