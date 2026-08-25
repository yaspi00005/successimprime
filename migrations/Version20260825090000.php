<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

final class Version20260825090000 extends AbstractMigration
{
    public function getDescription(): string
    {
        return "Cree la table decaissement_recurrent (frais bancaires, "
            . "remboursement de credit... decaisses automatiquement).";
    }

    public function up(Schema $schema): void
    {
        $this->addSql(
            'CREATE TABLE decaissement_recurrent (
                id INT AUTO_INCREMENT NOT NULL,
                compte_source_id INT NOT NULL,
                cree_par_id INT DEFAULT NULL,
                libelle VARCHAR(255) NOT NULL,
                categorie VARCHAR(30) NOT NULL,
                montant INT NOT NULL,
                frequence VARCHAR(20) NOT NULL,
                jour_du_mois SMALLINT NOT NULL,
                mois_de_lannee SMALLINT DEFAULT NULL,
                actif TINYINT(1) NOT NULL,
                date_debut DATE NOT NULL,
                prochaine_date_execution DATE NOT NULL,
                derniere_date_execution DATE DEFAULT NULL,
                date_creation DATETIME NOT NULL,
                notes LONGTEXT DEFAULT NULL,
                INDEX idx_decaissement_recurrent_compte (compte_source_id),
                INDEX idx_decaissement_recurrent_cree_par (cree_par_id),
                INDEX idx_decaissement_recurrent_prochaine_echeance (actif, prochaine_date_execution),
                PRIMARY KEY (id)
            ) DEFAULT CHARACTER SET utf8mb4 COLLATE `utf8mb4_unicode_ci` ENGINE = InnoDB'
        );

        $this->addSql(
            'ALTER TABLE decaissement_recurrent ADD CONSTRAINT FK_decaissement_recurrent_compte
             FOREIGN KEY (compte_source_id) REFERENCES compte_tresorerie (id) ON DELETE RESTRICT'
        );

        $this->addSql(
            'ALTER TABLE decaissement_recurrent ADD CONSTRAINT FK_decaissement_recurrent_cree_par
             FOREIGN KEY (cree_par_id) REFERENCES `user` (id) ON DELETE SET NULL'
        );
    }

    public function down(Schema $schema): void
    {
        $this->addSql('DROP TABLE decaissement_recurrent');
    }
}
