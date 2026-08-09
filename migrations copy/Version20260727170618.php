<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260727170618 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('CREATE TABLE commande_detail_finition (id INT AUTO_INCREMENT NOT NULL, prix_applique INT NOT NULL, mode_calcul VARCHAR(30) NOT NULL, quantite INT NOT NULL, montant INT NOT NULL, commande_detail_id INT NOT NULL, configuration_finition_id INT NOT NULL, INDEX IDX_B07D7138C8DC59F9 (commande_detail_id), INDEX IDX_B07D7138A0C197D7 (configuration_finition_id), UNIQUE INDEX uniq_commande_detail_configuration_finition (commande_detail_id, configuration_finition_id), PRIMARY KEY (id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('ALTER TABLE commande_detail_finition ADD CONSTRAINT FK_B07D7138C8DC59F9 FOREIGN KEY (commande_detail_id) REFERENCES commandes_details (id) ON DELETE CASCADE');
        $this->addSql('ALTER TABLE commande_detail_finition ADD CONSTRAINT FK_B07D7138A0C197D7 FOREIGN KEY (configuration_finition_id) REFERENCES produit_configuration_finition (id) ON DELETE RESTRICT');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE commande_detail_finition DROP FOREIGN KEY FK_B07D7138C8DC59F9');
        $this->addSql('ALTER TABLE commande_detail_finition DROP FOREIGN KEY FK_B07D7138A0C197D7');
        $this->addSql('DROP TABLE commande_detail_finition');
    }
}
