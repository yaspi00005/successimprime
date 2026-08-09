<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260717123948 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('CREATE TABLE articles (id INT AUTO_INCREMENT NOT NULL, reference VARCHAR(255) NOT NULL, designation VARCHAR(255) NOT NULL, categorie VARCHAR(100) NOT NULL, unite VARCHAR(30) NOT NULL, stock INT NOT NULL, stock_min VARCHAR(255) NOT NULL, prix_achat INT NOT NULL, prix_vente INT NOT NULL, fournisseur VARCHAR(50) NOT NULL, PRIMARY KEY (id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('CREATE TABLE clients (id INT AUTO_INCREMENT NOT NULL, code VARCHAR(50) NOT NULL, raison_sociale VARCHAR(100) NOT NULL, nom VARCHAR(50) NOT NULL, prenom VARCHAR(50) NOT NULL, telephone INT NOT NULL, telephone2 INT NOT NULL, email VARCHAR(255) NOT NULL, adresse VARCHAR(255) NOT NULL, ville VARCHAR(100) NOT NULL, nif VARCHAR(30) NOT NULL, rccm VARCHAR(50) NOT NULL, type_client VARCHAR(50) NOT NULL, plafond_credit INT NOT NULL, observation LONGTEXT NOT NULL, created_at DATETIME NOT NULL, updated_at DATETIME NOT NULL, PRIMARY KEY (id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('CREATE TABLE commandes (id INT AUTO_INCREMENT NOT NULL, commandes VARCHAR(30) NOT NULL, montant_total INT NOT NULL, remises INT NOT NULL, montant_apayer INT NOT NULL, date_commandes DATETIME NOT NULL, date_livraisons DATETIME NOT NULL, deleted TINYINT NOT NULL, statut TINYINT NOT NULL, numero VARCHAR(50) NOT NULL, date_commande DATE NOT NULL, date_livraison DATETIME NOT NULL, etat TINYINT NOT NULL, remise INT NOT NULL, tva INT NOT NULL, total_ht INT NOT NULL, total_ttc INT NOT NULL, observation LONGTEXT NOT NULL, clients_id INT NOT NULL, agents_id INT NOT NULL, INDEX IDX_35D4282CAB014612 (clients_id), INDEX IDX_35D4282C709770DC (agents_id), PRIMARY KEY (id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('CREATE TABLE commandes_details (id INT AUTO_INCREMENT NOT NULL, types_impressions VARCHAR(50) NOT NULL, longueurs INT NOT NULL, largeur INT NOT NULL, prix INT NOT NULL, remises INT NOT NULL, quantites INT NOT NULL, designation VARCHAR(255) NOT NULL, longueur INT NOT NULL, surface VARCHAR(100) DEFAULT NULL, quantite INT NOT NULL, prix_unitaire INT NOT NULL, cout_revient INT NOT NULL, remise INT NOT NULL, tva INT NOT NULL, total_ht INT NOT NULL, total_ttc INT NOT NULL, profil_couleurs VARCHAR(5) NOT NULL, resolution LONGTEXT NOT NULL, grammage VARCHAR(100) NOT NULL, epaisseur VARCHAR(50) NOT NULL, recto_verso TINYINT NOT NULL, nombre_faces INT NOT NULL, laminage VARCHAR(255) NOT NULL, oeillets TINYINT NOT NULL, decoupe TINYINT NOT NULL, pliage BIGINT DEFAULT NULL, emballage TINYINT DEFAULT NULL, bat_valide BIGINT NOT NULL, etat TINYINT NOT NULL, priorite VARCHAR(30) NOT NULL, temps_estime INT NOT NULL, temps_reel INT NOT NULL, fichier VARCHAR(255) NOT NULL, observation LONGTEXT NOT NULL, commande_id INT DEFAULT NULL, produit_id INT DEFAULT NULL, type_impression_id INT DEFAULT NULL, support_id INT DEFAULT NULL, machine_id INT DEFAULT NULL, format_id INT DEFAULT NULL, INDEX IDX_B48B83DA82EA2E54 (commande_id), INDEX IDX_B48B83DAF347EFB (produit_id), INDEX IDX_B48B83DAD357F183 (type_impression_id), INDEX IDX_B48B83DA315B405 (support_id), INDEX IDX_B48B83DAF6B75B26 (machine_id), INDEX IDX_B48B83DAD629F605 (format_id), PRIMARY KEY (id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('CREATE TABLE consommation_encres (id INT AUTO_INCREMENT NOT NULL, encre INT NOT NULL, quantite INT NOT NULL, cout VARCHAR(40) NOT NULL, production_id INT DEFAULT NULL, INDEX IDX_31C495E1ECC6147F (production_id), PRIMARY KEY (id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('CREATE TABLE employes (id INT AUTO_INCREMENT NOT NULL, nom VARCHAR(50) NOT NULL, prenom VARCHAR(50) NOT NULL, fonction VARCHAR(255) NOT NULL, telephone VARCHAR(50) NOT NULL, email VARCHAR(255) NOT NULL, PRIMARY KEY (id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('CREATE TABLE factures (id INT AUTO_INCREMENT NOT NULL, numero INT NOT NULL, date DATETIME NOT NULL, montant INT NOT NULL, etat TINYINT NOT NULL, commande_id INT NOT NULL, INDEX IDX_647590B82EA2E54 (commande_id), PRIMARY KEY (id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('CREATE TABLE finition (id INT AUTO_INCREMENT NOT NULL, nom VARCHAR(255) NOT NULL, PRIMARY KEY (id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('CREATE TABLE format (id INT AUTO_INCREMENT NOT NULL, nom VARCHAR(255) NOT NULL, largeur INT NOT NULL, hauteur VARCHAR(255) NOT NULL, PRIMARY KEY (id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('CREATE TABLE fournisseurs (id INT AUTO_INCREMENT NOT NULL, nom VARCHAR(255) NOT NULL, telephone INT NOT NULL, email VARCHAR(255) NOT NULL, adresse LONGTEXT NOT NULL, PRIMARY KEY (id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('CREATE TABLE machines (id INT AUTO_INCREMENT NOT NULL, nom VARCHAR(255) NOT NULL, marque VARCHAR(100) NOT NULL, modeles VARCHAR(100) NOT NULL, numero_serie VARCHAR(100) NOT NULL, type_machine VARCHAR(100) NOT NULL, largeur_impression VARCHAR(10) NOT NULL, nb_tetes INT NOT NULL, date_achat DATE NOT NULL, date_mise_service DATE NOT NULL, compteur_m2 INT NOT NULL, compteur_heures INT NOT NULL, etat VARCHAR(20) NOT NULL, PRIMARY KEY (id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('CREATE TABLE maintenance (id INT AUTO_INCREMENT NOT NULL, date DATETIME NOT NULL, type VARCHAR(255) NOT NULL, description VARCHAR(255) NOT NULL, cout VARCHAR(100) NOT NULL, technicien VARCHAR(255) NOT NULL, machine_id INT DEFAULT NULL, INDEX IDX_2F84F8E9F6B75B26 (machine_id), PRIMARY KEY (id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('CREATE TABLE paiements (id INT AUTO_INCREMENT NOT NULL, montant INT NOT NULL, mode VARCHAR(100) NOT NULL, date DATETIME NOT NULL, reference VARCHAR(255) NOT NULL, commande_id INT NOT NULL, INDEX IDX_E1B02E1282EA2E54 (commande_id), PRIMARY KEY (id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('CREATE TABLE production (id INT AUTO_INCREMENT NOT NULL, date_debut DATETIME NOT NULL, date_fin DATETIME NOT NULL, temps INT NOT NULL, m2_imprimes INT NOT NULL, etat TINYINT NOT NULL, commande_details_id INT DEFAULT NULL, machine_id INT DEFAULT NULL, INDEX IDX_D3EDB1E023D82BC4 (commande_details_id), INDEX IDX_D3EDB1E0F6B75B26 (machine_id), PRIMARY KEY (id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('CREATE TABLE produits (id INT AUTO_INCREMENT NOT NULL, reference VARCHAR(100) NOT NULL, designations VARCHAR(255) NOT NULL, categorie VARCHAR(255) NOT NULL, grammage INT NOT NULL, epaisseur VARCHAR(255) NOT NULL, prix_base INT NOT NULL, description LONGTEXT NOT NULL, actif TINYINT NOT NULL, PRIMARY KEY (id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('CREATE TABLE stock_entrees (id INT AUTO_INCREMENT NOT NULL, quantites INT NOT NULL, prix INT NOT NULL, date DATETIME NOT NULL, article_id INT DEFAULT NULL, INDEX IDX_3D445A027294869C (article_id), PRIMARY KEY (id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('CREATE TABLE stock_sorties (id INT AUTO_INCREMENT NOT NULL, quantite INT NOT NULL, date DATETIME NOT NULL, article_id INT DEFAULT NULL, commande_detail_id INT DEFAULT NULL, INDEX IDX_5127734B7294869C (article_id), INDEX IDX_5127734BC8DC59F9 (commande_detail_id), PRIMARY KEY (id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('CREATE TABLE supports (id INT AUTO_INCREMENT NOT NULL, nom VARCHAR(255) NOT NULL, PRIMARY KEY (id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('CREATE TABLE types_impression (id INT AUTO_INCREMENT NOT NULL, nom VARCHAR(255) NOT NULL, PRIMARY KEY (id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('CREATE TABLE `user` (id INT AUTO_INCREMENT NOT NULL, username VARCHAR(180) NOT NULL, roles JSON NOT NULL, password VARCHAR(255) NOT NULL, UNIQUE INDEX UNIQ_IDENTIFIER_USERNAME (username), PRIMARY KEY (id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('CREATE TABLE messenger_messages (id BIGINT AUTO_INCREMENT NOT NULL, body LONGTEXT NOT NULL, headers LONGTEXT NOT NULL, queue_name VARCHAR(190) NOT NULL, created_at DATETIME NOT NULL, available_at DATETIME NOT NULL, delivered_at DATETIME DEFAULT NULL, INDEX IDX_75EA56E0FB7336F0E3BD61CE16BA31DBBF396750 (queue_name, available_at, delivered_at, id), PRIMARY KEY (id)) DEFAULT CHARACTER SET utf8mb4');
        $this->addSql('ALTER TABLE commandes ADD CONSTRAINT FK_35D4282CAB014612 FOREIGN KEY (clients_id) REFERENCES clients (id)');
        $this->addSql('ALTER TABLE commandes ADD CONSTRAINT FK_35D4282C709770DC FOREIGN KEY (agents_id) REFERENCES `user` (id)');
        $this->addSql('ALTER TABLE commandes_details ADD CONSTRAINT FK_B48B83DA82EA2E54 FOREIGN KEY (commande_id) REFERENCES commandes (id)');
        $this->addSql('ALTER TABLE commandes_details ADD CONSTRAINT FK_B48B83DAF347EFB FOREIGN KEY (produit_id) REFERENCES produits (id)');
        $this->addSql('ALTER TABLE commandes_details ADD CONSTRAINT FK_B48B83DAD357F183 FOREIGN KEY (type_impression_id) REFERENCES types_impression (id)');
        $this->addSql('ALTER TABLE commandes_details ADD CONSTRAINT FK_B48B83DA315B405 FOREIGN KEY (support_id) REFERENCES supports (id)');
        $this->addSql('ALTER TABLE commandes_details ADD CONSTRAINT FK_B48B83DAF6B75B26 FOREIGN KEY (machine_id) REFERENCES machines (id)');
        $this->addSql('ALTER TABLE commandes_details ADD CONSTRAINT FK_B48B83DAD629F605 FOREIGN KEY (format_id) REFERENCES format (id)');
        $this->addSql('ALTER TABLE consommation_encres ADD CONSTRAINT FK_31C495E1ECC6147F FOREIGN KEY (production_id) REFERENCES production (id)');
        $this->addSql('ALTER TABLE factures ADD CONSTRAINT FK_647590B82EA2E54 FOREIGN KEY (commande_id) REFERENCES commandes (id)');
        $this->addSql('ALTER TABLE maintenance ADD CONSTRAINT FK_2F84F8E9F6B75B26 FOREIGN KEY (machine_id) REFERENCES machines (id)');
        $this->addSql('ALTER TABLE paiements ADD CONSTRAINT FK_E1B02E1282EA2E54 FOREIGN KEY (commande_id) REFERENCES commandes (id)');
        $this->addSql('ALTER TABLE production ADD CONSTRAINT FK_D3EDB1E023D82BC4 FOREIGN KEY (commande_details_id) REFERENCES commandes_details (id)');
        $this->addSql('ALTER TABLE production ADD CONSTRAINT FK_D3EDB1E0F6B75B26 FOREIGN KEY (machine_id) REFERENCES machines (id)');
        $this->addSql('ALTER TABLE stock_entrees ADD CONSTRAINT FK_3D445A027294869C FOREIGN KEY (article_id) REFERENCES articles (id)');
        $this->addSql('ALTER TABLE stock_sorties ADD CONSTRAINT FK_5127734B7294869C FOREIGN KEY (article_id) REFERENCES articles (id)');
        $this->addSql('ALTER TABLE stock_sorties ADD CONSTRAINT FK_5127734BC8DC59F9 FOREIGN KEY (commande_detail_id) REFERENCES commandes_details (id)');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE commandes DROP FOREIGN KEY FK_35D4282CAB014612');
        $this->addSql('ALTER TABLE commandes DROP FOREIGN KEY FK_35D4282C709770DC');
        $this->addSql('ALTER TABLE commandes_details DROP FOREIGN KEY FK_B48B83DA82EA2E54');
        $this->addSql('ALTER TABLE commandes_details DROP FOREIGN KEY FK_B48B83DAF347EFB');
        $this->addSql('ALTER TABLE commandes_details DROP FOREIGN KEY FK_B48B83DAD357F183');
        $this->addSql('ALTER TABLE commandes_details DROP FOREIGN KEY FK_B48B83DA315B405');
        $this->addSql('ALTER TABLE commandes_details DROP FOREIGN KEY FK_B48B83DAF6B75B26');
        $this->addSql('ALTER TABLE commandes_details DROP FOREIGN KEY FK_B48B83DAD629F605');
        $this->addSql('ALTER TABLE consommation_encres DROP FOREIGN KEY FK_31C495E1ECC6147F');
        $this->addSql('ALTER TABLE factures DROP FOREIGN KEY FK_647590B82EA2E54');
        $this->addSql('ALTER TABLE maintenance DROP FOREIGN KEY FK_2F84F8E9F6B75B26');
        $this->addSql('ALTER TABLE paiements DROP FOREIGN KEY FK_E1B02E1282EA2E54');
        $this->addSql('ALTER TABLE production DROP FOREIGN KEY FK_D3EDB1E023D82BC4');
        $this->addSql('ALTER TABLE production DROP FOREIGN KEY FK_D3EDB1E0F6B75B26');
        $this->addSql('ALTER TABLE stock_entrees DROP FOREIGN KEY FK_3D445A027294869C');
        $this->addSql('ALTER TABLE stock_sorties DROP FOREIGN KEY FK_5127734B7294869C');
        $this->addSql('ALTER TABLE stock_sorties DROP FOREIGN KEY FK_5127734BC8DC59F9');
        $this->addSql('DROP TABLE articles');
        $this->addSql('DROP TABLE clients');
        $this->addSql('DROP TABLE commandes');
        $this->addSql('DROP TABLE commandes_details');
        $this->addSql('DROP TABLE consommation_encres');
        $this->addSql('DROP TABLE employes');
        $this->addSql('DROP TABLE factures');
        $this->addSql('DROP TABLE finition');
        $this->addSql('DROP TABLE format');
        $this->addSql('DROP TABLE fournisseurs');
        $this->addSql('DROP TABLE machines');
        $this->addSql('DROP TABLE maintenance');
        $this->addSql('DROP TABLE paiements');
        $this->addSql('DROP TABLE production');
        $this->addSql('DROP TABLE produits');
        $this->addSql('DROP TABLE stock_entrees');
        $this->addSql('DROP TABLE stock_sorties');
        $this->addSql('DROP TABLE supports');
        $this->addSql('DROP TABLE types_impression');
        $this->addSql('DROP TABLE `user`');
        $this->addSql('DROP TABLE messenger_messages');
    }
}
