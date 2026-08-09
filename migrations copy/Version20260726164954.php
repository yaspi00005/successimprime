<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260726164954 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('CREATE TABLE categorie_produit (id INT AUTO_INCREMENT NOT NULL, nom VARCHAR(255) NOT NULL, description VARCHAR(500) NOT NULL, publie TINYINT NOT NULL, ordre INT NOT NULL, UNIQUE INDEX UNIQ_762642856C6E55B5 (nom), PRIMARY KEY (id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('CREATE TABLE produits_types_impression (produits_id INT NOT NULL, types_impression_id INT NOT NULL, INDEX IDX_1ADC26C2CD11A2CF (produits_id), INDEX IDX_1ADC26C29719B876 (types_impression_id), PRIMARY KEY (produits_id, types_impression_id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('CREATE TABLE produits_supports (produits_id INT NOT NULL, supports_id INT NOT NULL, INDEX IDX_42046455CD11A2CF (produits_id), INDEX IDX_4204645597185C1E (supports_id), PRIMARY KEY (produits_id, supports_id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('CREATE TABLE produits_format (produits_id INT NOT NULL, format_id INT NOT NULL, INDEX IDX_4FAB693CCD11A2CF (produits_id), INDEX IDX_4FAB693CD629F605 (format_id), PRIMARY KEY (produits_id, format_id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('CREATE TABLE produits_finition (produits_id INT NOT NULL, finition_id INT NOT NULL, INDEX IDX_DF5600F4CD11A2CF (produits_id), INDEX IDX_DF5600F4CB56F5AF (finition_id), PRIMARY KEY (produits_id, finition_id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('ALTER TABLE produits_types_impression ADD CONSTRAINT FK_1ADC26C2CD11A2CF FOREIGN KEY (produits_id) REFERENCES produits (id) ON DELETE CASCADE');
        $this->addSql('ALTER TABLE produits_types_impression ADD CONSTRAINT FK_1ADC26C29719B876 FOREIGN KEY (types_impression_id) REFERENCES types_impression (id) ON DELETE CASCADE');
        $this->addSql('ALTER TABLE produits_supports ADD CONSTRAINT FK_42046455CD11A2CF FOREIGN KEY (produits_id) REFERENCES produits (id) ON DELETE CASCADE');
        $this->addSql('ALTER TABLE produits_supports ADD CONSTRAINT FK_4204645597185C1E FOREIGN KEY (supports_id) REFERENCES supports (id) ON DELETE CASCADE');
        $this->addSql('ALTER TABLE produits_format ADD CONSTRAINT FK_4FAB693CCD11A2CF FOREIGN KEY (produits_id) REFERENCES produits (id) ON DELETE CASCADE');
        $this->addSql('ALTER TABLE produits_format ADD CONSTRAINT FK_4FAB693CD629F605 FOREIGN KEY (format_id) REFERENCES format (id) ON DELETE CASCADE');
        $this->addSql('ALTER TABLE produits_finition ADD CONSTRAINT FK_DF5600F4CD11A2CF FOREIGN KEY (produits_id) REFERENCES produits (id) ON DELETE CASCADE');
        $this->addSql('ALTER TABLE produits_finition ADD CONSTRAINT FK_DF5600F4CB56F5AF FOREIGN KEY (finition_id) REFERENCES finition (id) ON DELETE CASCADE');
        $this->addSql('ALTER TABLE produits ADD nom VARCHAR(255) NOT NULL, ADD ordre INT NOT NULL, ADD categorie_produit_id INT NOT NULL, DROP reference, DROP designations, DROP categorie, DROP grammage, DROP epaisseur, DROP prix_base, CHANGE description description VARCHAR(1000) NOT NULL, CHANGE actif publie TINYINT NOT NULL');
        $this->addSql('ALTER TABLE produits ADD CONSTRAINT FK_BE2DDF8C91FDB457 FOREIGN KEY (categorie_produit_id) REFERENCES categorie_produit (id)');
        $this->addSql('CREATE UNIQUE INDEX UNIQ_BE2DDF8C6C6E55B5 ON produits (nom)');
        $this->addSql('CREATE INDEX IDX_BE2DDF8C91FDB457 ON produits (categorie_produit_id)');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE produits_types_impression DROP FOREIGN KEY FK_1ADC26C2CD11A2CF');
        $this->addSql('ALTER TABLE produits_types_impression DROP FOREIGN KEY FK_1ADC26C29719B876');
        $this->addSql('ALTER TABLE produits_supports DROP FOREIGN KEY FK_42046455CD11A2CF');
        $this->addSql('ALTER TABLE produits_supports DROP FOREIGN KEY FK_4204645597185C1E');
        $this->addSql('ALTER TABLE produits_format DROP FOREIGN KEY FK_4FAB693CCD11A2CF');
        $this->addSql('ALTER TABLE produits_format DROP FOREIGN KEY FK_4FAB693CD629F605');
        $this->addSql('ALTER TABLE produits_finition DROP FOREIGN KEY FK_DF5600F4CD11A2CF');
        $this->addSql('ALTER TABLE produits_finition DROP FOREIGN KEY FK_DF5600F4CB56F5AF');
        $this->addSql('DROP TABLE categorie_produit');
        $this->addSql('DROP TABLE produits_types_impression');
        $this->addSql('DROP TABLE produits_supports');
        $this->addSql('DROP TABLE produits_format');
        $this->addSql('DROP TABLE produits_finition');
        $this->addSql('ALTER TABLE produits DROP FOREIGN KEY FK_BE2DDF8C91FDB457');
        $this->addSql('DROP INDEX UNIQ_BE2DDF8C6C6E55B5 ON produits');
        $this->addSql('DROP INDEX IDX_BE2DDF8C91FDB457 ON produits');
        $this->addSql('ALTER TABLE produits ADD reference VARCHAR(100) NOT NULL, ADD categorie VARCHAR(255) NOT NULL, ADD grammage INT NOT NULL, ADD epaisseur VARCHAR(255) NOT NULL, ADD prix_base INT NOT NULL, DROP ordre, DROP categorie_produit_id, CHANGE description description LONGTEXT NOT NULL, CHANGE nom designations VARCHAR(255) NOT NULL, CHANGE publie actif TINYINT NOT NULL');
    }
}
