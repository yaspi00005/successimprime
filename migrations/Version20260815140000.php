<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

final class Version20260815140000 extends AbstractMigration
{
    public function getDescription(): string
    {
        return "Ajoute la table journal_activite (journal d'activite avant/apres, alimente automatiquement par AuditSubscriber).";
    }

    public function up(Schema $schema): void
    {
        $this->addSql('CREATE TABLE journal_activite (id INT AUTO_INCREMENT NOT NULL, entite VARCHAR(100) NOT NULL, entite_id INT NOT NULL, action VARCHAR(20) NOT NULL, donnees_avant JSON DEFAULT NULL, donnees_apres JSON DEFAULT NULL, utilisateur_id INT DEFAULT NULL, created_at DATETIME NOT NULL, INDEX IDX_journal_activite_utilisateur (utilisateur_id), INDEX IDX_journal_activite_entite (entite, entite_id), INDEX IDX_journal_activite_created_at (created_at), PRIMARY KEY (id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('ALTER TABLE journal_activite ADD CONSTRAINT FK_journal_activite_utilisateur FOREIGN KEY (utilisateur_id) REFERENCES `user` (id) ON DELETE SET NULL');
    }

    public function down(Schema $schema): void
    {
        $this->addSql('ALTER TABLE journal_activite DROP FOREIGN KEY FK_journal_activite_utilisateur');
        $this->addSql('DROP TABLE journal_activite');
    }
}
