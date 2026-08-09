<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260808233614 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('CREATE TABLE produit_article_stock (id INT AUTO_INCREMENT NOT NULL, coefficient NUMERIC(12, 3) DEFAULT \'1.000\' NOT NULL, mode_calcul VARCHAR(30) DEFAULT \'quantite\' NOT NULL, actif TINYINT DEFAULT 1 NOT NULL, obligatoire TINYINT DEFAULT 1 NOT NULL, observation LONGTEXT DEFAULT NULL, ordre INT DEFAULT 10 NOT NULL, produit_id INT NOT NULL, article_id INT NOT NULL, INDEX IDX_12DF82AFF347EFB (produit_id), INDEX IDX_12DF82AF7294869C (article_id), UNIQUE INDEX uniq_produit_article_stock (produit_id, article_id), PRIMARY KEY (id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('ALTER TABLE produit_article_stock ADD CONSTRAINT FK_12DF82AFF347EFB FOREIGN KEY (produit_id) REFERENCES produits (id) ON DELETE CASCADE');
        $this->addSql('ALTER TABLE produit_article_stock ADD CONSTRAINT FK_12DF82AF7294869C FOREIGN KEY (article_id) REFERENCES articles (id) ON DELETE RESTRICT');
        $this->addSql('ALTER TABLE bon_livraison ADD gestion_stock TINYINT DEFAULT 0 NOT NULL, ADD coefficient_stock NUMERIC(10, 3) DEFAULT \'1.000\' NOT NULL, ADD article_stock_id INT DEFAULT NULL');
        $this->addSql('ALTER TABLE bon_livraison ADD CONSTRAINT FK_31A531A45825957B FOREIGN KEY (article_stock_id) REFERENCES articles (id) ON DELETE SET NULL');
        $this->addSql('CREATE INDEX IDX_31A531A45825957B ON bon_livraison (article_stock_id)');
        $this->addSql('ALTER TABLE production ADD gestion_stock TINYINT DEFAULT 0 NOT NULL');
        $this->addSql('ALTER TABLE produits ADD gestion_stock TINYINT DEFAULT 0 NOT NULL, ADD article_stock_id INT DEFAULT NULL');
        $this->addSql('ALTER TABLE produits ADD CONSTRAINT FK_BE2DDF8C5825957B FOREIGN KEY (article_stock_id) REFERENCES articles (id) ON DELETE SET NULL');
        $this->addSql('CREATE INDEX IDX_BE2DDF8C5825957B ON produits (article_stock_id)');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE produit_article_stock DROP FOREIGN KEY FK_12DF82AFF347EFB');
        $this->addSql('ALTER TABLE produit_article_stock DROP FOREIGN KEY FK_12DF82AF7294869C');
        $this->addSql('DROP TABLE produit_article_stock');
        $this->addSql('ALTER TABLE bon_livraison DROP FOREIGN KEY FK_31A531A45825957B');
        $this->addSql('DROP INDEX IDX_31A531A45825957B ON bon_livraison');
        $this->addSql('ALTER TABLE bon_livraison DROP gestion_stock, DROP coefficient_stock, DROP article_stock_id');
        $this->addSql('ALTER TABLE production DROP gestion_stock');
        $this->addSql('ALTER TABLE produits DROP FOREIGN KEY FK_BE2DDF8C5825957B');
        $this->addSql('DROP INDEX IDX_BE2DDF8C5825957B ON produits');
        $this->addSql('ALTER TABLE produits DROP gestion_stock, DROP article_stock_id');
    }
}
