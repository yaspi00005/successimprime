<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260805225618 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE commande_detail_fichier ADD chemin VARCHAR(500) DEFAULT NULL, ADD origine VARCHAR(30) NOT NULL, ADD etat VARCHAR(30) NOT NULL, ADD deja_traite TINYINT DEFAULT 0 NOT NULL, ADD fichier_production TINYINT DEFAULT 0 NOT NULL, ADD actif TINYINT DEFAULT 1 NOT NULL, ADD version INT DEFAULT 1 NOT NULL, ADD quantite_aproduire INT DEFAULT NULL, ADD face VARCHAR(30) DEFAULT NULL, ADD designation VARCHAR(255) DEFAULT NULL, ADD groupe_fichier VARCHAR(100) DEFAULT NULL, ADD observation LONGTEXT DEFAULT NULL, ADD fichier_source_id INT DEFAULT NULL, ADD ajoute_par_id INT DEFAULT NULL, CHANGE type_mime type_mime VARCHAR(100) DEFAULT NULL, CHANGE taille taille INT DEFAULT NULL');
        $this->addSql('ALTER TABLE commande_detail_fichier ADD CONSTRAINT FK_39E2DA10B130D9F1 FOREIGN KEY (fichier_source_id) REFERENCES commande_detail_fichier (id) ON DELETE SET NULL');
        $this->addSql('ALTER TABLE commande_detail_fichier ADD CONSTRAINT FK_39E2DA10DAA76F43 FOREIGN KEY (ajoute_par_id) REFERENCES `user` (id) ON DELETE SET NULL');
        $this->addSql('CREATE INDEX IDX_39E2DA10B130D9F1 ON commande_detail_fichier (fichier_source_id)');
        $this->addSql('CREATE INDEX IDX_39E2DA10DAA76F43 ON commande_detail_fichier (ajoute_par_id)');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE commande_detail_fichier DROP FOREIGN KEY FK_39E2DA10B130D9F1');
        $this->addSql('ALTER TABLE commande_detail_fichier DROP FOREIGN KEY FK_39E2DA10DAA76F43');
        $this->addSql('DROP INDEX IDX_39E2DA10B130D9F1 ON commande_detail_fichier');
        $this->addSql('DROP INDEX IDX_39E2DA10DAA76F43 ON commande_detail_fichier');
        $this->addSql('ALTER TABLE commande_detail_fichier DROP chemin, DROP origine, DROP etat, DROP deja_traite, DROP fichier_production, DROP actif, DROP version, DROP quantite_aproduire, DROP face, DROP designation, DROP groupe_fichier, DROP observation, DROP fichier_source_id, DROP ajoute_par_id, CHANGE type_mime type_mime VARCHAR(100) NOT NULL, CHANGE taille taille INT NOT NULL');
    }
}
