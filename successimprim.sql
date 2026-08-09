-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Hôte : localhost
-- Généré le : sam. 01 août 2026 à 23:37
-- Version du serveur : 10.4.28-MariaDB
-- Version de PHP : 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `successimprim`
--

-- --------------------------------------------------------

--
-- Structure de la table `articles`
--

CREATE TABLE `articles` (
  `id` int(11) NOT NULL,
  `reference` varchar(255) NOT NULL,
  `designation` varchar(255) NOT NULL,
  `categorie` varchar(100) NOT NULL,
  `unite` varchar(30) NOT NULL,
  `stock` int(11) NOT NULL,
  `stock_min` varchar(255) NOT NULL,
  `prix_achat` int(11) NOT NULL,
  `prix_vente` int(11) NOT NULL,
  `fournisseur` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `categorie_produit`
--

CREATE TABLE `categorie_produit` (
  `id` int(11) NOT NULL,
  `nom` varchar(255) NOT NULL,
  `description` varchar(500) NOT NULL,
  `publie` tinyint(4) NOT NULL,
  `ordre` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `categorie_produit`
--

INSERT INTO `categorie_produit` (`id`, `nom`, `description`, `publie`, `ordre`) VALUES
(1, 'Papeterie', 'Produits de papeterie et bureautique', 1, 10),
(2, 'Communication', 'Supports de communication visuelle', 1, 20),
(3, 'Signalétique', 'Signalétique intérieure et extérieure', 1, 30),
(4, 'Grand Format', 'Impressions grand format', 1, 40),
(5, 'Événementiel', 'Supports pour événements', 1, 50),
(6, 'Marketing', 'Supports publicitaires', 1, 60),
(7, 'Textile', 'Impression sur textile', 1, 70),
(8, 'Packaging', 'Packaging et étiquettes', 1, 80),
(9, 'Personnalisation', 'Objets publicitaires personnalisés', 1, 90),
(10, 'Administration', 'Documents administratifs', 1, 100);

-- --------------------------------------------------------

--
-- Structure de la table `clients`
--

CREATE TABLE `clients` (
  `id` int(11) NOT NULL,
  `code` varchar(50) NOT NULL,
  `raison_sociale` varchar(100) DEFAULT NULL,
  `nom` varchar(50) NOT NULL,
  `prenom` varchar(50) NOT NULL,
  `telephone` varchar(30) NOT NULL,
  `telephone2` varchar(30) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `adresse` varchar(255) DEFAULT NULL,
  `ville` varchar(100) DEFAULT NULL,
  `nif` varchar(30) DEFAULT NULL,
  `rccm` varchar(50) DEFAULT NULL,
  `type_client` varchar(10) NOT NULL DEFAULT 'B2C',
  `plafond_credit` int(11) DEFAULT NULL,
  `observation` longtext DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `statut` tinyint(4) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `clients`
--

INSERT INTO `clients` (`id`, `code`, `raison_sociale`, `nom`, `prenom`, `telephone`, `telephone2`, `email`, `adresse`, `ville`, `nif`, `rccm`, `type_client`, `plafond_credit`, `observation`, `created_at`, `updated_at`, `statut`) VALUES
(1, 'CLI-000001', 'yaya', 'DIALLO', 'Yaya', '78478742', NULL, 'bayayadiallo1@gmail.com', 'Sotuba Aci 1', 'ABANCOURT', NULL, NULL, 'B2C', 0, NULL, '2026-07-29 21:48:35', '2026-07-29 21:48:35', 0),
(3, 'CLI-000003', 'yaya', 'DIALLO', 'Yaya', '78478746', NULL, 'bayayadiallo1@gmail.com', 'Sotuba Aci 1', 'ABANCOURT', NULL, NULL, 'B2C', 0, NULL, '2026-07-29 21:52:24', '2026-07-29 22:21:50', 1),
(5, 'CLI-000005', 'yaya', 'DIALLO', 'Yaya', '784787424', NULL, 'bayayadiallo1@gmail.com', 'Sotuba Aci 1', 'ABANCOURT', NULL, NULL, 'B2C', 0, NULL, '2026-07-29 21:58:43', '2026-07-29 21:58:43', 0);

-- --------------------------------------------------------

--
-- Structure de la table `commandes`
--

CREATE TABLE `commandes` (
  `id` int(11) NOT NULL,
  `montant_apayer` int(11) NOT NULL DEFAULT 0,
  `deleted` tinyint(4) NOT NULL DEFAULT 0,
  `statut` tinyint(4) NOT NULL DEFAULT 1,
  `numero` varchar(50) DEFAULT NULL,
  `date_commande` datetime NOT NULL,
  `date_livraison` datetime DEFAULT NULL,
  `etat` tinyint(4) NOT NULL DEFAULT 1,
  `remise` int(11) NOT NULL DEFAULT 0,
  `tva` int(11) NOT NULL DEFAULT 0,
  `total_ht` int(11) NOT NULL DEFAULT 0,
  `total_ttc` int(11) NOT NULL DEFAULT 0,
  `observation` longtext DEFAULT NULL,
  `clients_id` int(11) NOT NULL,
  `agents_id` int(11) NOT NULL,
  `reste_apayer` int(11) NOT NULL,
  `total_paye` int(11) NOT NULL,
  `statut_paiement` varchar(20) NOT NULL DEFAULT 'impayee'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `commandes`
--

INSERT INTO `commandes` (`id`, `montant_apayer`, `deleted`, `statut`, `numero`, `date_commande`, `date_livraison`, `etat`, `remise`, `tva`, `total_ht`, `total_ttc`, `observation`, `clients_id`, `agents_id`, `reste_apayer`, `total_paye`, `statut_paiement`) VALUES
(1, 25000, 0, 1, 'CMD-000001-08-2026', '2026-08-01 18:56:40', '2026-08-04 18:56:40', 1, 0, 0, 25000, 25000, NULL, 3, 1, 0, 0, 'impayee'),
(2, 743750, 0, 1, 'CMD-000002-08-2026', '2026-08-01 19:14:41', '2026-08-04 19:14:41', 1, 0, 0, 743750, 743750, NULL, 3, 1, 0, 0, 'impayee'),
(3, 25000, 0, 1, 'CMD-000003-08-2026', '2026-08-01 19:23:53', '2026-08-04 19:23:53', 1, 0, 0, 25000, 25000, NULL, 3, 1, 0, 25000, 'payee');

-- --------------------------------------------------------

--
-- Structure de la table `commandes_details`
--

CREATE TABLE `commandes_details` (
  `id` int(11) NOT NULL,
  `largeur` decimal(10,2) DEFAULT NULL,
  `designation` varchar(255) NOT NULL,
  `longueur` decimal(10,2) DEFAULT NULL,
  `surface` decimal(12,4) DEFAULT NULL,
  `quantite` int(11) NOT NULL DEFAULT 1,
  `prix_unitaire` int(11) NOT NULL DEFAULT 0,
  `cout_revient` int(11) NOT NULL DEFAULT 0,
  `remise` int(11) NOT NULL DEFAULT 0,
  `tva` int(11) NOT NULL DEFAULT 0,
  `total_ht` int(11) NOT NULL DEFAULT 0,
  `total_ttc` int(11) NOT NULL DEFAULT 0,
  `profil_couleurs` varchar(20) DEFAULT NULL,
  `resolution` varchar(50) DEFAULT NULL,
  `grammage` varchar(100) DEFAULT NULL,
  `epaisseur` varchar(50) DEFAULT NULL,
  `recto_verso` tinyint(4) NOT NULL DEFAULT 0,
  `nombre_faces` int(11) NOT NULL DEFAULT 1,
  `laminage` varchar(255) DEFAULT NULL,
  `oeillets` tinyint(4) NOT NULL DEFAULT 0,
  `decoupe` tinyint(4) NOT NULL DEFAULT 0,
  `pliage` varchar(100) DEFAULT NULL,
  `emballage` tinyint(4) NOT NULL DEFAULT 0,
  `bat_valide` tinyint(4) NOT NULL DEFAULT 0,
  `etat` tinyint(4) NOT NULL DEFAULT 1,
  `priorite` varchar(30) NOT NULL DEFAULT 'normale',
  `temps_estime` int(11) DEFAULT NULL,
  `temps_reel` int(11) DEFAULT NULL,
  `fichier` varchar(255) DEFAULT NULL,
  `observation` longtext DEFAULT NULL,
  `commande_id` int(11) NOT NULL,
  `produit_id` int(11) DEFAULT NULL,
  `type_impression_id` int(11) DEFAULT NULL,
  `support_id` int(11) DEFAULT NULL,
  `machine_id` int(11) DEFAULT NULL,
  `format_id` int(11) DEFAULT NULL,
  `produit_configuration_id` int(11) DEFAULT NULL,
  `mode_configuration` varchar(20) NOT NULL DEFAULT 'automatique',
  `mode_calcul` varchar(30) NOT NULL DEFAULT 'unite'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `commandes_details`
--

INSERT INTO `commandes_details` (`id`, `largeur`, `designation`, `longueur`, `surface`, `quantite`, `prix_unitaire`, `cout_revient`, `remise`, `tva`, `total_ht`, `total_ttc`, `profil_couleurs`, `resolution`, `grammage`, `epaisseur`, `recto_verso`, `nombre_faces`, `laminage`, `oeillets`, `decoupe`, `pliage`, `emballage`, `bat_valide`, `etat`, `priorite`, `temps_estime`, `temps_reel`, `fichier`, `observation`, `commande_id`, `produit_id`, `type_impression_id`, `support_id`, `machine_id`, `format_id`, `produit_configuration_id`, `mode_configuration`, `mode_calcul`) VALUES
(1, NULL, 'BACHE', NULL, NULL, 100, 5000, 0, 0, 0, 25000, 25000, NULL, NULL, NULL, NULL, 0, 1, NULL, 0, 0, NULL, 0, 0, 0, 'basse', NULL, NULL, NULL, NULL, 1, 1, 4, 4, NULL, 8, 1, 'automatique', 'forfait'),
(2, 3.00, 'BACHE', 1.00, 3.0000, 1, 7000, 0, 0, 0, 21000, 21000, NULL, NULL, NULL, NULL, 0, 1, NULL, 1, 0, NULL, 0, 0, 0, 'basse', NULL, NULL, NULL, NULL, 2, 20, 2, 10, NULL, 49, NULL, 'manuel', 'metre_carre'),
(3, NULL, 'Carte de viste', NULL, 0.0000, 100, 5000, 0, 0, 0, 500000, 500000, NULL, NULL, NULL, NULL, 0, 1, NULL, 0, 0, NULL, 0, 0, 0, 'basse', NULL, NULL, NULL, NULL, 2, 1, 4, 4, NULL, 8, NULL, 'manuel', 'unite'),
(4, NULL, 'Support Kakemono', NULL, 0.0000, 10, 22500, 0, 1, 0, 222750, 222750, NULL, NULL, NULL, NULL, 0, 1, NULL, 0, 0, NULL, 0, 0, 0, 'basse', NULL, NULL, NULL, NULL, 2, NULL, NULL, NULL, NULL, NULL, NULL, 'libre', 'unite'),
(5, NULL, 'BACHE', NULL, NULL, 100, 5000, 0, 0, 0, 25000, 25000, NULL, NULL, NULL, NULL, 0, 1, NULL, 0, 0, NULL, 0, 0, 0, 'basse', NULL, NULL, NULL, NULL, 3, 1, 4, 4, NULL, 8, 1, 'automatique', 'forfait');

-- --------------------------------------------------------

--
-- Structure de la table `commande_detail_fichier`
--

CREATE TABLE `commande_detail_fichier` (
  `id` int(11) NOT NULL,
  `nom_original` varchar(255) NOT NULL,
  `nom_stockage` varchar(255) NOT NULL,
  `type_mime` varchar(100) NOT NULL,
  `taille` int(11) NOT NULL,
  `statut` varchar(30) NOT NULL,
  `cree_le` datetime NOT NULL,
  `commande_detail_id` int(11) DEFAULT NULL,
  `jeton_upload` varchar(64) NOT NULL,
  `morceaux_recus` int(11) NOT NULL DEFAULT 0,
  `nombre_morceaux` int(11) DEFAULT NULL,
  `termine_le` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `commande_detail_fichier`
--

INSERT INTO `commande_detail_fichier` (`id`, `nom_original`, `nom_stockage`, `type_mime`, `taille`, `statut`, `cree_le`, `commande_detail_id`, `jeton_upload`, `morceaux_recus`, `nombre_morceaux`, `termine_le`) VALUES
(1, 'Balcon Agent.pdf', '9c113d5d3f54e3966c6eb4b2bcb3e91c63c8ff484287642620abd3c5b63e4df4.pdf', 'application/pdf', 2918126, 'TERMINE', '2026-08-01 17:15:10', NULL, '9c113d5d3f54e3966c6eb4b2bcb3e91c63c8ff484287642620abd3c5b63e4df4', 1, 1, '2026-08-01 17:15:10'),
(2, 'COMBATTANTS VIERGE_20260801_103102_0000.pdf', '1f2776ff6aa09b1b37db2f6c415cc32b32ee19750f58297f3d8f8543cfa64411.pdf', 'application/pdf', 1692408, 'TERMINE', '2026-08-01 18:37:34', 1, '1f2776ff6aa09b1b37db2f6c415cc32b32ee19750f58297f3d8f8543cfa64411', 1, 1, '2026-08-01 18:37:34'),
(3, 'Salle Accueil PRO SECURITÉ.pdf', 'bab216c3022f1f16e982de698e1e7d176927e2c26831f8167c3926479b3551be.pdf', 'application/pdf', 106212477, 'TERMINE', '2026-08-01 19:10:13', 2, 'bab216c3022f1f16e982de698e1e7d176927e2c26831f8167c3926479b3551be', 21, 21, '2026-08-01 19:10:14'),
(4, 'Pro-securité.jpg', '2ad7708bf141f7d360735b9d09a22144eb698b9da3f92b75903b28542d2f2c1e.jpg', 'image/jpeg', 19009605, 'TERMINE', '2026-08-01 19:11:09', 3, '2ad7708bf141f7d360735b9d09a22144eb698b9da3f92b75903b28542d2f2c1e', 4, 4, '2026-08-01 19:11:09');

-- --------------------------------------------------------

--
-- Structure de la table `commande_detail_finition`
--

CREATE TABLE `commande_detail_finition` (
  `id` int(11) NOT NULL,
  `prix_applique` int(11) NOT NULL,
  `mode_calcul` varchar(30) NOT NULL,
  `quantite` int(11) NOT NULL,
  `montant` int(11) NOT NULL,
  `commande_detail_id` int(11) NOT NULL,
  `configuration_finition_id` int(11) DEFAULT NULL,
  `nom_finition` varchar(255) NOT NULL,
  `obligatoire` tinyint(4) NOT NULL DEFAULT 0,
  `finition_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `commande_detail_finition`
--

INSERT INTO `commande_detail_finition` (`id`, `prix_applique`, `mode_calcul`, `quantite`, `montant`, `commande_detail_id`, `configuration_finition_id`, `nom_finition`, `obligatoire`, `finition_id`) VALUES
(1, 200, 'unite', 100, 20000, 1, 1, 'Pelliculage Brillant', 1, 23),
(2, 0, 'forfait', 1, 0, 2, NULL, 'Œillets', 0, 8),
(3, 0, 'unite', 10, 0, 3, NULL, 'Lamination Mate', 0, 4),
(4, 200, 'unite', 100, 20000, 5, 1, 'Pelliculage Brillant', 1, 23);

-- --------------------------------------------------------

--
-- Structure de la table `consommation_encres`
--

CREATE TABLE `consommation_encres` (
  `id` int(11) NOT NULL,
  `encre` int(11) NOT NULL DEFAULT 0,
  `quantite` int(11) NOT NULL DEFAULT 0,
  `cout` int(11) NOT NULL DEFAULT 0,
  `production_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `devis`
--

CREATE TABLE `devis` (
  `id` int(11) NOT NULL,
  `numero` varchar(50) NOT NULL,
  `date_creation` datetime NOT NULL,
  `date_validite` datetime NOT NULL,
  `statut` varchar(30) NOT NULL,
  `remise_pourcentage` int(11) NOT NULL DEFAULT 0,
  `montant_remise` int(11) NOT NULL DEFAULT 0,
  `taux_tva` int(11) NOT NULL DEFAULT 0,
  `total_ht` int(11) NOT NULL DEFAULT 0,
  `total_apres_remise` int(11) NOT NULL DEFAULT 0,
  `montant_tva` int(11) NOT NULL DEFAULT 0,
  `total_ttc` int(11) NOT NULL DEFAULT 0,
  `notes` longtext DEFAULT NULL,
  `conditions_commerciales` longtext DEFAULT NULL,
  `client_id` int(11) NOT NULL,
  `commande_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `devis_details`
--

CREATE TABLE `devis_details` (
  `id` int(11) NOT NULL,
  `mode_configuration` varchar(20) NOT NULL DEFAULT 'automatique',
  `designation` varchar(255) NOT NULL,
  `largeur` decimal(10,2) DEFAULT NULL,
  `longueur` decimal(10,2) DEFAULT NULL,
  `surface` decimal(12,4) DEFAULT NULL,
  `quantite` int(11) NOT NULL DEFAULT 1,
  `prix_unitaire` int(11) NOT NULL DEFAULT 0,
  `cout_revient` int(11) NOT NULL DEFAULT 0,
  `remise` int(11) NOT NULL DEFAULT 0,
  `tva` int(11) NOT NULL DEFAULT 0,
  `total_ht` int(11) NOT NULL DEFAULT 0,
  `total_ttc` int(11) NOT NULL DEFAULT 0,
  `profil_couleurs` varchar(20) DEFAULT NULL,
  `resolution` varchar(50) DEFAULT NULL,
  `grammage` varchar(100) DEFAULT NULL,
  `epaisseur` varchar(50) DEFAULT NULL,
  `recto_verso` tinyint(4) NOT NULL DEFAULT 0,
  `nombre_faces` int(11) NOT NULL DEFAULT 1,
  `laminage` varchar(255) DEFAULT NULL,
  `oeillets` tinyint(4) NOT NULL DEFAULT 0,
  `decoupe` tinyint(4) NOT NULL DEFAULT 0,
  `pliage` varchar(100) DEFAULT NULL,
  `emballage` tinyint(4) NOT NULL DEFAULT 0,
  `ordre` int(11) NOT NULL DEFAULT 10,
  `etat` tinyint(4) NOT NULL DEFAULT 1,
  `priorite` varchar(30) NOT NULL DEFAULT 'normale',
  `temps_estime` int(11) DEFAULT NULL,
  `observation` longtext DEFAULT NULL,
  `mode_calcul` varchar(30) NOT NULL DEFAULT 'unite',
  `devis_id` int(11) NOT NULL,
  `produit_id` int(11) DEFAULT NULL,
  `produit_configuration_id` int(11) DEFAULT NULL,
  `type_impression_id` int(11) DEFAULT NULL,
  `support_id` int(11) DEFAULT NULL,
  `format_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `devis_detail_finition`
--

CREATE TABLE `devis_detail_finition` (
  `id` int(11) NOT NULL,
  `nom_finition` varchar(255) NOT NULL,
  `obligatoire` tinyint(4) NOT NULL DEFAULT 0,
  `prix_applique` int(11) NOT NULL DEFAULT 0,
  `mode_calcul` varchar(30) NOT NULL DEFAULT 'forfait',
  `quantite` int(11) NOT NULL DEFAULT 1,
  `montant` int(11) NOT NULL DEFAULT 0,
  `devis_detail_id` int(11) NOT NULL,
  `configuration_finition_id` int(11) DEFAULT NULL,
  `finition_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `doctrine_migration_versions`
--

CREATE TABLE `doctrine_migration_versions` (
  `version` varchar(191) NOT NULL,
  `executed_at` datetime DEFAULT NULL,
  `execution_time` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `doctrine_migration_versions`
--

INSERT INTO `doctrine_migration_versions` (`version`, `executed_at`, `execution_time`) VALUES
('DoctrineMigrations\\Version20260717123948', '2026-07-17 12:53:43', 496),
('DoctrineMigrations\\Version20260721161422', '2026-07-21 16:15:18', 13),
('DoctrineMigrations\\Version20260721182653', '2026-07-21 18:26:58', 19),
('DoctrineMigrations\\Version20260722172653', '2026-07-22 17:26:57', 13),
('DoctrineMigrations\\Version20260722172743', '2026-07-22 17:27:46', 9),
('DoctrineMigrations\\Version20260722204649', '2026-07-22 20:46:56', 9),
('DoctrineMigrations\\Version20260722204726', '2026-07-22 20:47:28', 60),
('DoctrineMigrations\\Version20260722210311', '2026-07-22 21:03:13', 71),
('DoctrineMigrations\\Version20260722212912', '2026-07-22 21:29:15', 64),
('DoctrineMigrations\\Version20260722213948', '2026-07-22 21:39:51', 17),
('DoctrineMigrations\\Version20260724121208', '2026-07-24 12:12:13', 15),
('DoctrineMigrations\\Version20260724141651', '2026-07-24 14:16:53', 9),
('DoctrineMigrations\\Version20260724150258', '2026-07-24 15:03:02', 16),
('DoctrineMigrations\\Version20260724153009', '2026-07-24 15:30:11', 15),
('DoctrineMigrations\\Version20260724155146', '2026-07-24 15:52:09', 68),
('DoctrineMigrations\\Version20260724160244', '2026-07-24 16:02:47', 25),
('DoctrineMigrations\\Version20260725230322', '2026-07-25 23:03:30', 21),
('DoctrineMigrations\\Version20260726145526', '2026-07-26 14:55:34', 95),
('DoctrineMigrations\\Version20260726151637', '2026-07-26 15:16:50', 21),
('DoctrineMigrations\\Version20260726153341', '2026-07-26 15:33:46', 230),
('DoctrineMigrations\\Version20260726163204', '2026-07-26 16:32:10', 192),
('DoctrineMigrations\\Version20260726164954', '2026-07-26 16:50:01', 258),
('DoctrineMigrations\\Version20260726165053', '2026-07-26 16:50:56', 25),
('DoctrineMigrations\\Version20260726171831', '2026-07-26 17:18:33', 228),
('DoctrineMigrations\\Version20260726175036', '2026-07-26 17:50:41', 40),
('DoctrineMigrations\\Version20260726194736', '2026-07-26 19:47:54', 145),
('DoctrineMigrations\\Version20260727160405', '2026-07-27 16:05:06', 82),
('DoctrineMigrations\\Version20260727170618', '2026-07-27 17:08:50', 66),
('DoctrineMigrations\\Version20260727225358', '2026-07-27 22:54:18', 38),
('DoctrineMigrations\\Version20260727230327', '2026-07-27 23:07:02', 26),
('DoctrineMigrations\\Version20260727233821', '2026-07-27 23:38:43', 52),
('DoctrineMigrations\\Version20260729184829', '2026-07-29 18:48:29', 43),
('DoctrineMigrations\\Version20260729185759', '2026-07-29 18:58:00', 10),
('DoctrineMigrations\\Version20260729201032', '2026-07-29 20:13:08', 73),
('DoctrineMigrations\\Version20260729203219', '2026-07-29 20:33:22', 21),
('DoctrineMigrations\\Version20260729210909', '2026-07-29 21:09:20', 7),
('DoctrineMigrations\\Version20260729213401', '2026-07-29 21:34:02', 10),
('DoctrineMigrations\\Version20260730135215', '2026-07-30 14:05:28', 68),
('DoctrineMigrations\\Version20260730164132', '2026-07-30 16:45:08', 77),
('DoctrineMigrations\\Version20260730165831', '2026-07-30 16:58:37', 9),
('DoctrineMigrations\\Version20260730191459', '2026-07-30 19:15:00', 18),
('DoctrineMigrations\\Version20260730211044', '2026-07-30 21:10:45', 21),
('DoctrineMigrations\\Version20260730211252', '2026-07-30 21:12:53', 63),
('DoctrineMigrations\\Version20260801160158', '2026-08-01 16:01:59', 138),
('DoctrineMigrations\\Version20260801161324', '2026-08-01 16:13:24', 63),
('DoctrineMigrations\\Version20260801211741', '2026-08-01 21:25:30', 288);

-- --------------------------------------------------------

--
-- Structure de la table `employes`
--

CREATE TABLE `employes` (
  `id` int(11) NOT NULL,
  `nom` varchar(50) NOT NULL,
  `prenom` varchar(50) NOT NULL,
  `fonction` varchar(255) NOT NULL,
  `telephone` varchar(50) NOT NULL,
  `email` varchar(255) NOT NULL,
  `photos` varchar(255) NOT NULL,
  `cin` varchar(255) NOT NULL,
  `salaires` int(11) NOT NULL,
  `date_naissances` date NOT NULL,
  `matricules` varchar(100) NOT NULL,
  `date_embauches` date NOT NULL,
  `adresses` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `employes`
--

INSERT INTO `employes` (`id`, `nom`, `prenom`, `fonction`, `telephone`, `email`, `photos`, `cin`, `salaires`, `date_naissances`, `matricules`, `date_embauches`, `adresses`) VALUES
(1, 'DIALLO', 'Yaya', 'Gérant', '78478742', 'bayayadiallo1@gmail.com', 'photo_6a5fd00e093c9.png', 'cin_6a5fd00e09ad5.jpg', 140000, '2026-07-21', '001', '2024-05-15', ''),
(2, 'DIALLO', 'Chenon', 'Gérant', '78478742', 'bayayadiallo1@gmail.com', 'photo_6a60d18a124be.jpg', 'cin_6a60d18a12b8f.jpg', 140000, '2026-07-22', '001', '0000-00-00', ''),
(3, 'DIALLO', 'Chenon', 'Gérant', '78478742', 'bayayadiallo1@gmail.com', 'photo_6a60d1f07cc19.jpg', 'cin_6a60d1f07cf28.jpg', 140000, '2026-07-22', '001', '0000-00-00', ''),
(4, 'DIALLO', 'Chenon', 'Gérant', '78478742', 'bayayadiallo1@gmail.com', 'photo_6a60d2069e340.jpg', 'cin_6a60d2069e644.jpg', 140000, '2026-07-22', '001', '0000-00-00', '');

-- --------------------------------------------------------

--
-- Structure de la table `factures`
--

CREATE TABLE `factures` (
  `id` int(11) NOT NULL,
  `numero` int(11) NOT NULL,
  `date` datetime NOT NULL,
  `montant` int(11) NOT NULL,
  `etat` tinyint(4) NOT NULL,
  `commande_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `finition`
--

CREATE TABLE `finition` (
  `id` int(11) NOT NULL,
  `nom` varchar(255) NOT NULL,
  `publie` tinyint(4) NOT NULL,
  `ordre` int(11) NOT NULL,
  `description` longtext NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `finition`
--

INSERT INTO `finition` (`id`, `nom`, `publie`, `ordre`, `description`) VALUES
(1, 'Découpe', 1, 10, 'Découpe droite ou aux dimensions finales du support imprimé.'),
(2, 'Échenillage', 1, 20, 'Retrait des parties inutiles après la découpe du vinyle.'),
(3, 'Pose Tape', 1, 30, 'Application d’un film de transfert sur le vinyle découpé.'),
(4, 'Lamination Mate', 0, 40, 'Protection mate contre les rayures, l’humidité et les UV.'),
(5, 'Lamination Brillante', 0, 50, 'Protection brillante donnant plus d’éclat à l’impression.'),
(6, 'Contrecollage PVC', 1, 60, 'Collage de l’impression sur une plaque PVC rigide.'),
(7, 'Contrecollage Dibond', 1, 70, 'Collage de l’impression sur une plaque aluminium Dibond.'),
(8, 'Œillets', 1, 80, 'Pose d’œillets métalliques pour faciliter la fixation des bâches.'),
(9, 'Ourlet', 1, 90, 'Renforcement des bords d’une bâche par pliage et soudure ou couture.'),
(10, 'Couture', 1, 100, 'Assemblage ou renforcement textile et bâche par couture.'),
(11, 'Massicotage', 1, 110, 'Découpe précise du papier au format final.'),
(12, 'Rainage', 1, 120, 'Création d’une ligne de pli pour éviter de casser le papier.'),
(13, 'Pli Simple', 1, 130, 'Pliage du document en deux parties.'),
(14, 'Pli Accordéon', 1, 140, 'Pliage successif en forme d’accordéon.'),
(15, 'Pli Roulé', 1, 150, 'Pliage des volets les uns à l’intérieur des autres.'),
(16, 'Perforation', 1, 160, 'Création de trous ou de lignes détachables dans le papier.'),
(17, 'Numérotation', 1, 170, 'Ajout automatique de numéros uniques sur les documents.'),
(18, 'Agrafage', 1, 180, 'Assemblage des feuilles avec une ou plusieurs agrafes.'),
(19, 'Reliure Spirale', 1, 190, 'Assemblage des pages avec une spirale plastique ou métallique.'),
(20, 'Reliure Thermique', 1, 200, 'Assemblage des pages à l’aide d’une colle activée par la chaleur.'),
(21, 'Reliure Dos Carré Collé', 1, 210, 'Reliure professionnelle avec couverture collée sur le dos.'),
(22, 'Pelliculage Mat', 1, 220, 'Film mat de protection appliqué sur le papier.'),
(23, 'Pelliculage Brillant', 1, 230, 'Film brillant de protection appliqué sur le papier.'),
(24, 'Coins Arrondis', 1, 240, 'Arrondissement des angles des cartes ou documents.'),
(25, 'Découpe Forme', 1, 250, 'Découpe personnalisée selon un contour ou une forme spécifique.'),
(26, 'Impression DTF', 1, 260, 'Impression du visuel sur un film spécial pour transfert textile.'),
(27, 'Poudrage', 1, 270, 'Application de poudre thermofusible sur l’encre DTF.'),
(28, 'Cuisson', 1, 280, 'Chauffage du film pour faire fondre et fixer la poudre DTF.'),
(29, 'Découpe Film', 1, 290, 'Découpe du film DTF selon les motifs ou les commandes.'),
(30, 'Pressage', 1, 300, 'Transfert du visuel sur le textile à l’aide d’une presse à chaud.'),
(31, 'Double Pressage', 1, 310, 'Deuxième passage sous presse pour améliorer la fixation et la tenue.'),
(32, 'Refroidissement', 1, 320, 'Temps de repos après pressage avant retrait ou emballage.'),
(33, 'Impression Sublimation', 1, 330, 'Impression du visuel sur papier transfert pour sublimation.'),
(34, 'Découpe Papier Sublimation', 1, 340, 'Découpe du papier imprimé avant le pressage.'),
(35, 'Pressage Sublimation', 1, 350, 'Transfert thermique sur textile polyester ou objet compatible.'),
(36, 'Découpe Sticker', 1, 360, 'Découpe des autocollants au format ou au contour.'),
(37, 'Lamination Sticker', 1, 370, 'Protection transparente des autocollants imprimés.'),
(38, 'Découpe Vinyle', 1, 380, 'Découpe de textes, logos ou formes dans du vinyle adhésif.'),
(39, 'Pliage Textile', 1, 390, 'Pliage propre des vêtements après impression ou pressage.'),
(40, 'Contrôle Qualité', 1, 400, 'Vérification de la couleur, du placement, de la finition et des défauts.'),
(41, 'Emballage Individuel', 1, 410, 'Mise de chaque produit dans un emballage séparé.'),
(42, 'Mise en Carton', 1, 420, 'Regroupement et rangement des produits dans des cartons.'),
(43, 'Étiquetage', 1, 430, 'Ajout d’une étiquette produit, taille, client ou commande.'),
(44, 'Retrait Client', 1, 440, 'Commande récupérée directement par le client à l’atelier.'),
(45, 'Livraison', 1, 450, 'Commande remise au client par un livreur.'),
(46, 'Aucune Finition', 1, 460, 'Aucune opération supplémentaire après l’impression.'),
(48, 'Montage support kakemono', 1, 470, 'Montage sur le support demandé');

-- --------------------------------------------------------

--
-- Structure de la table `finition_types_impression`
--

CREATE TABLE `finition_types_impression` (
  `finition_id` int(11) NOT NULL,
  `types_impression_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `finition_types_impression`
--

INSERT INTO `finition_types_impression` (`finition_id`, `types_impression_id`) VALUES
(1, 2),
(1, 11),
(1, 13),
(1, 14),
(1, 15),
(1, 16),
(1, 17),
(1, 18),
(1, 19),
(1, 20),
(2, 11),
(2, 14),
(3, 11),
(4, 2),
(4, 13),
(4, 14),
(4, 18),
(4, 19),
(5, 2),
(5, 13),
(5, 14),
(5, 18),
(5, 19),
(6, 15),
(7, 16),
(8, 12),
(8, 13),
(9, 13),
(10, 13),
(11, 4),
(11, 5),
(11, 6),
(11, 7),
(11, 8),
(11, 19),
(11, 20),
(12, 4),
(12, 7),
(12, 8),
(13, 4),
(13, 7),
(13, 8),
(14, 4),
(14, 7),
(14, 8),
(15, 4),
(15, 7),
(15, 8),
(16, 4),
(16, 7),
(16, 8),
(17, 4),
(17, 7),
(18, 4),
(18, 5),
(18, 7),
(18, 8),
(19, 4),
(19, 5),
(19, 7),
(19, 8),
(20, 4),
(20, 5),
(20, 7),
(20, 8),
(21, 7),
(21, 8),
(22, 4),
(22, 7),
(22, 8),
(23, 4),
(23, 7),
(23, 8),
(24, 4),
(24, 7),
(24, 8),
(25, 4),
(25, 7),
(25, 8),
(26, 1),
(27, 1),
(28, 1),
(29, 1),
(30, 1),
(31, 1),
(32, 1),
(33, 9),
(34, 9),
(35, 9),
(36, 14),
(37, 14),
(38, 11),
(39, 1),
(39, 9),
(39, 10),
(40, 1),
(40, 2),
(40, 3),
(40, 4),
(40, 5),
(40, 6),
(40, 7),
(40, 8),
(40, 9),
(40, 10),
(40, 11),
(40, 12),
(40, 13),
(40, 14),
(40, 15),
(40, 16),
(40, 17),
(40, 18),
(40, 19),
(40, 20),
(41, 1),
(41, 2),
(41, 3),
(41, 4),
(41, 5),
(41, 6),
(41, 7),
(41, 8),
(41, 9),
(41, 10),
(41, 11),
(41, 12),
(41, 13),
(41, 14),
(41, 15),
(41, 16),
(41, 17),
(41, 18),
(41, 19),
(41, 20),
(42, 1),
(42, 2),
(42, 3),
(42, 4),
(42, 5),
(42, 6),
(42, 7),
(42, 8),
(42, 9),
(42, 10),
(42, 11),
(42, 12),
(42, 13),
(42, 14),
(42, 15),
(42, 16),
(42, 17),
(42, 18),
(42, 19),
(42, 20),
(43, 1),
(43, 2),
(43, 3),
(43, 4),
(43, 5),
(43, 6),
(43, 7),
(43, 8),
(43, 9),
(43, 10),
(43, 11),
(43, 12),
(43, 13),
(43, 14),
(43, 15),
(43, 16),
(43, 17),
(43, 18),
(43, 19),
(43, 20),
(44, 1),
(44, 2),
(44, 3),
(44, 4),
(44, 5),
(44, 6),
(44, 7),
(44, 8),
(44, 9),
(44, 10),
(44, 11),
(44, 12),
(44, 13),
(44, 14),
(44, 15),
(44, 16),
(44, 17),
(44, 18),
(44, 19),
(44, 20),
(45, 1),
(45, 2),
(45, 3),
(45, 4),
(45, 5),
(45, 6),
(45, 7),
(45, 8),
(45, 9),
(45, 10),
(45, 11),
(45, 12),
(45, 13),
(45, 14),
(45, 15),
(45, 16),
(45, 17),
(45, 18),
(45, 19),
(45, 20),
(46, 1),
(46, 2),
(46, 3),
(46, 4),
(46, 5),
(46, 6),
(46, 7),
(46, 8),
(46, 9),
(46, 10),
(46, 11),
(46, 12),
(46, 13),
(46, 14),
(46, 15),
(46, 16),
(46, 17),
(46, 18),
(46, 19),
(46, 20),
(48, 2);

-- --------------------------------------------------------

--
-- Structure de la table `format`
--

CREATE TABLE `format` (
  `id` int(11) NOT NULL,
  `nom` varchar(150) NOT NULL,
  `largeur` decimal(10,2) NOT NULL,
  `hauteur` decimal(10,2) NOT NULL,
  `unite` varchar(10) NOT NULL,
  `description` longtext NOT NULL,
  `publie` tinyint(4) NOT NULL,
  `ordre` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `format`
--

INSERT INTO `format` (`id`, `nom`, `largeur`, `hauteur`, `unite`, `description`, `publie`, `ordre`) VALUES
(1, 'A6', 10.50, 14.80, 'cm', 'Petit format adapté aux flyers, cartes et documents courts.', 1, 10),
(2, 'A5', 14.80, 21.00, 'cm', 'Format adapté aux flyers, carnets, brochures et transferts textiles.', 1, 20),
(3, 'A4', 21.00, 29.70, 'cm', 'Format standard pour documents, affiches, DTF et sublimation.', 1, 30),
(4, 'A3', 29.70, 42.00, 'cm', 'Grand format papier adapté aux affiches et transferts textiles.', 1, 40),
(5, 'A2', 42.00, 59.40, 'cm', 'Format d’affiche, plan et impression grand format.', 1, 50),
(6, 'A1', 59.40, 84.10, 'cm', 'Format destiné aux affiches, plans et supports grand format.', 1, 60),
(7, 'A0', 84.10, 118.90, 'cm', 'Très grand format adapté aux plans et affiches professionnelles.', 1, 70),
(8, 'Carte de visite', 8.50, 5.50, 'cm', 'Format standard pour les cartes de visite professionnelles.', 1, 80),
(9, 'Carte PVC', 8.60, 5.40, 'cm', 'Format standard pour badge, carte d’accès ou carte de fidélité PVC.', 1, 90),
(10, 'Flyer DL', 9.90, 21.00, 'cm', 'Format allongé pour flyers publicitaires et dépliants.', 1, 100),
(11, 'Carré 10 × 10', 10.00, 10.00, 'cm', 'Petit format carré pour cartes, stickers et supports promotionnels.', 1, 110),
(12, 'Carré 15 × 15', 15.00, 15.00, 'cm', 'Format carré pour flyers, invitations et impressions décoratives.', 1, 120),
(13, 'Affiche 30 × 40', 30.00, 40.00, 'cm', 'Petit format d’affiche publicitaire ou décorative.', 1, 130),
(14, 'Affiche 40 × 60', 40.00, 60.00, 'cm', 'Format courant pour affiches publicitaires.', 1, 140),
(15, 'Affiche 50 × 70', 50.00, 70.00, 'cm', 'Format d’affiche moyenne pour communication intérieure.', 1, 150),
(16, 'Affiche 60 × 80', 60.00, 80.00, 'cm', 'Grand format d’affiche publicitaire.', 1, 160),
(17, 'Affiche 80 × 120', 80.00, 120.00, 'cm', 'Très grand format pour affichage événementiel et commercial.', 1, 170),
(18, 'Roll-up 85 × 200', 85.00, 200.00, 'cm', 'Format standard de roll-up pour salons et événements.', 1, 180),
(19, 'Roll-up 100 × 200', 100.00, 200.00, 'cm', 'Roll-up large pour communication visuelle.', 1, 190),
(20, 'Roll-up 120 × 200', 120.00, 200.00, 'cm', 'Grand roll-up pour événements et espaces commerciaux.', 1, 200),
(21, 'X-Banner 60 × 160', 60.00, 160.00, 'cm', 'Format compact pour support publicitaire X-Banner.', 1, 210),
(22, 'X-Banner 80 × 180', 80.00, 180.00, 'cm', 'Grand format pour support publicitaire X-Banner.', 1, 220),
(23, 'Bâche 100 × 200', 100.00, 200.00, 'cm', 'Petite bâche pour communication intérieure ou extérieure.', 1, 230),
(24, 'Bâche 100 × 300', 100.00, 300.00, 'cm', 'Bâche horizontale adaptée aux enseignes et événements.', 1, 240),
(25, 'Bâche 200 × 300', 200.00, 300.00, 'cm', 'Grande bâche publicitaire pour façade ou événement.', 1, 250),
(26, 'Bâche 300 × 500', 300.00, 500.00, 'cm', 'Très grande bâche pour affichage extérieur.', 1, 260),
(27, 'Sticker 5 × 5', 5.00, 5.00, 'cm', 'Petit autocollant carré pour logo, emballage ou produit.', 1, 270),
(28, 'Sticker 10 × 10', 10.00, 10.00, 'cm', 'Autocollant moyen pour communication et étiquetage.', 1, 280),
(29, 'Sticker A5', 14.80, 21.00, 'cm', 'Autocollant au format A5.', 1, 290),
(30, 'Sticker A4', 21.00, 29.70, 'cm', 'Autocollant au format A4.', 1, 300),
(31, 'Logo poitrine', 10.00, 10.00, 'cm', 'Petit marquage textile destiné à la poitrine.', 1, 310),
(32, 'Marquage textile A5', 14.80, 21.00, 'cm', 'Petit visuel textile pour devant, manche ou accessoire.', 1, 320),
(33, 'Marquage textile A4', 21.00, 29.70, 'cm', 'Format moyen pour impression textile.', 1, 330),
(34, 'Marquage textile A3', 29.70, 42.00, 'cm', 'Grand marquage textile pour devant ou dos.', 1, 340),
(35, 'Dos textile 28 × 35', 28.00, 35.00, 'cm', 'Format courant pour impression au dos d’un t-shirt ou polo.', 1, 350),
(36, 'Mug standard', 20.00, 9.00, 'cm', 'Zone d’impression standard pour mug sublimable.', 1, 360),
(37, 'Tasse panoramique', 22.00, 10.00, 'cm', 'Zone d’impression panoramique pour tasse ou mug.', 1, 370),
(38, 'Canvas 30 × 40', 30.00, 40.00, 'cm', 'Petit tableau décoratif imprimé sur toile Canvas.', 1, 380),
(39, 'Canvas 40 × 60', 40.00, 60.00, 'cm', 'Tableau décoratif moyen sur toile Canvas.', 1, 390),
(40, 'Canvas 60 × 80', 60.00, 80.00, 'cm', 'Grand tableau décoratif sur toile Canvas.', 1, 400),
(41, 'Photo 10 × 15', 10.00, 15.00, 'cm', 'Format photographique classique.', 1, 410),
(42, 'Photo 13 × 18', 13.00, 18.00, 'cm', 'Format photo moyen pour album ou cadre.', 1, 420),
(43, 'Photo 15 × 21', 15.00, 21.00, 'cm', 'Format photo proche du format A5.', 1, 430),
(44, 'Photo 20 × 30', 20.00, 30.00, 'cm', 'Grand format photographique.', 1, 440),
(45, 'Panneau 30 × 40', 30.00, 40.00, 'cm', 'Petit panneau rigide pour PVC, Forex ou Dibond.', 1, 450),
(46, 'Panneau 40 × 60', 40.00, 60.00, 'cm', 'Panneau rigide moyen pour signalétique.', 1, 460),
(47, 'Panneau 60 × 80', 60.00, 80.00, 'cm', 'Grand panneau rigide pour affichage et signalétique.', 1, 470),
(48, 'Panneau 100 × 200', 100.00, 200.00, 'cm', 'Très grand panneau pour enseigne ou signalétique.', 1, 480),
(49, 'Bâche 200 cm / 100', 200.00, 100.00, 'cm', 'TEST', 1, 490);

-- --------------------------------------------------------

--
-- Structure de la table `format_types_impression`
--

CREATE TABLE `format_types_impression` (
  `format_id` int(11) NOT NULL,
  `types_impression_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `format_types_impression`
--

INSERT INTO `format_types_impression` (`format_id`, `types_impression_id`) VALUES
(1, 1),
(1, 2),
(1, 4),
(1, 5),
(1, 6),
(1, 7),
(1, 8),
(1, 14),
(1, 19),
(2, 1),
(2, 4),
(2, 5),
(2, 6),
(2, 7),
(2, 8),
(2, 9),
(2, 10),
(2, 14),
(2, 19),
(3, 1),
(3, 3),
(3, 4),
(3, 5),
(3, 6),
(3, 7),
(3, 8),
(3, 9),
(3, 10),
(3, 11),
(3, 14),
(3, 19),
(4, 1),
(4, 2),
(4, 3),
(4, 4),
(4, 5),
(4, 7),
(4, 8),
(4, 9),
(4, 10),
(4, 11),
(4, 14),
(4, 19),
(4, 20),
(5, 2),
(5, 3),
(5, 7),
(5, 8),
(5, 14),
(5, 18),
(5, 19),
(5, 20),
(6, 2),
(6, 3),
(6, 14),
(6, 18),
(6, 19),
(6, 20),
(7, 2),
(7, 3),
(7, 14),
(7, 18),
(7, 19),
(7, 20),
(8, 3),
(8, 4),
(8, 5),
(8, 7),
(8, 8),
(9, 3),
(9, 8),
(9, 15),
(10, 4),
(10, 5),
(10, 7),
(10, 8),
(11, 3),
(11, 4),
(11, 7),
(11, 8),
(11, 14),
(11, 19),
(12, 3),
(12, 4),
(12, 7),
(12, 8),
(12, 14),
(12, 19),
(13, 2),
(13, 3),
(13, 7),
(13, 8),
(13, 14),
(13, 18),
(13, 19),
(14, 2),
(14, 3),
(14, 8),
(14, 14),
(14, 18),
(14, 19),
(15, 2),
(15, 3),
(15, 8),
(15, 14),
(15, 18),
(15, 19),
(16, 2),
(16, 3),
(16, 14),
(16, 18),
(16, 19),
(17, 2),
(17, 3),
(17, 14),
(17, 18),
(17, 19),
(18, 2),
(18, 12),
(19, 2),
(19, 12),
(20, 2),
(20, 12),
(21, 2),
(21, 12),
(22, 2),
(22, 12),
(23, 2),
(23, 13),
(24, 2),
(24, 13),
(25, 2),
(25, 13),
(26, 2),
(26, 13),
(27, 2),
(27, 3),
(27, 11),
(27, 14),
(28, 2),
(28, 3),
(28, 11),
(28, 14),
(29, 2),
(29, 3),
(29, 11),
(29, 14),
(30, 2),
(30, 3),
(30, 11),
(30, 14),
(31, 1),
(31, 9),
(31, 10),
(32, 1),
(32, 9),
(32, 10),
(33, 1),
(33, 9),
(33, 10),
(34, 1),
(34, 9),
(34, 10),
(35, 1),
(35, 9),
(35, 10),
(36, 9),
(37, 9),
(38, 2),
(38, 3),
(38, 18),
(39, 2),
(39, 3),
(39, 18),
(40, 2),
(40, 3),
(40, 18),
(41, 4),
(41, 8),
(41, 19),
(42, 4),
(42, 8),
(42, 19),
(43, 4),
(43, 8),
(43, 19),
(44, 2),
(44, 4),
(44, 8),
(44, 19),
(45, 2),
(45, 3),
(45, 15),
(45, 16),
(45, 17),
(46, 2),
(46, 3),
(46, 15),
(46, 16),
(46, 17),
(47, 2),
(47, 3),
(47, 15),
(47, 16),
(47, 17),
(48, 2),
(48, 3),
(48, 15),
(48, 16),
(48, 17),
(49, 2);

-- --------------------------------------------------------

--
-- Structure de la table `fournisseurs`
--

CREATE TABLE `fournisseurs` (
  `id` int(11) NOT NULL,
  `nom` varchar(255) NOT NULL,
  `telephone` int(11) NOT NULL,
  `email` varchar(255) NOT NULL,
  `adresse` longtext NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `machines`
--

CREATE TABLE `machines` (
  `id` int(11) NOT NULL,
  `nom` varchar(255) NOT NULL,
  `marque` varchar(100) NOT NULL,
  `modeles` varchar(100) NOT NULL,
  `numero_serie` varchar(100) NOT NULL,
  `type_machine` varchar(100) NOT NULL,
  `largeur_impression` varchar(10) NOT NULL,
  `nb_tetes` int(11) NOT NULL,
  `date_achat` date NOT NULL,
  `date_mise_service` date NOT NULL,
  `compteur_m2` int(11) NOT NULL,
  `compteur_heures` int(11) NOT NULL,
  `etat` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `maintenance`
--

CREATE TABLE `maintenance` (
  `id` int(11) NOT NULL,
  `date` datetime NOT NULL,
  `type` varchar(255) NOT NULL,
  `description` varchar(255) NOT NULL,
  `cout` varchar(100) NOT NULL,
  `technicien` varchar(255) NOT NULL,
  `machine_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `messenger_messages`
--

CREATE TABLE `messenger_messages` (
  `id` bigint(20) NOT NULL,
  `body` longtext NOT NULL,
  `headers` longtext NOT NULL,
  `queue_name` varchar(190) NOT NULL,
  `created_at` datetime NOT NULL,
  `available_at` datetime NOT NULL,
  `delivered_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `paiements`
--

CREATE TABLE `paiements` (
  `id` int(11) NOT NULL,
  `montant` int(11) NOT NULL,
  `mode` varchar(100) NOT NULL,
  `date` datetime NOT NULL,
  `reference` varchar(255) DEFAULT NULL,
  `commande_id` int(11) NOT NULL,
  `encaisse_par_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `paiements`
--

INSERT INTO `paiements` (`id`, `montant`, `mode`, `date`, `reference`, `commande_id`, `encaisse_par_id`) VALUES
(1, 5000, 'Orange Money', '2026-07-30 17:37:15', 'YAYA', 4, 1),
(2, 5000, 'Orange Money', '2026-07-30 17:39:53', 'YAYA', 4, 1),
(3, 5000, 'Espèces', '2026-07-30 18:45:33', 'YAYA', 4, 1),
(4, 4000, 'Espèces', '2026-07-30 19:15:46', NULL, 4, 1),
(5, 5000, 'Espèces', '2026-07-30 19:23:11', NULL, 4, 1),
(6, 5000, 'Espèces', '2026-07-30 19:34:31', NULL, 4, 1),
(7, 25000, 'Espèces', '2026-08-01 19:07:50', NULL, 1, 1),
(8, 15000, 'Espèces', '2026-08-01 19:25:10', 'TEST', 3, 1),
(9, 5000, 'Espèces', '2026-08-01 19:35:47', NULL, 3, 1),
(10, 5000, 'Orange Money', '2026-08-01 19:40:41', NULL, 3, 1);

-- --------------------------------------------------------

--
-- Structure de la table `production`
--

CREATE TABLE `production` (
  `id` int(11) NOT NULL,
  `date_debut` datetime NOT NULL,
  `date_fin` datetime NOT NULL,
  `temps` int(11) NOT NULL,
  `m2_imprimes` int(11) NOT NULL,
  `etat` tinyint(4) NOT NULL,
  `commande_details_id` int(11) DEFAULT NULL,
  `machine_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `produits`
--

CREATE TABLE `produits` (
  `id` int(11) NOT NULL,
  `description` varchar(1000) NOT NULL,
  `publie` tinyint(4) NOT NULL DEFAULT 1,
  `nom` varchar(255) NOT NULL,
  `ordre` int(11) NOT NULL DEFAULT 10,
  `categorie_produit_id` int(11) NOT NULL,
  `code` varchar(50) NOT NULL,
  `prix_base` double DEFAULT NULL,
  `personnalisable` tinyint(4) NOT NULL DEFAULT 1,
  `actif` tinyint(4) NOT NULL DEFAULT 1,
  `prix_b2_b` double DEFAULT NULL,
  `mode_calcul` varchar(30) NOT NULL DEFAULT 'unite'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `produits`
--

INSERT INTO `produits` (`id`, `description`, `publie`, `nom`, `ordre`, `categorie_produit_id`, `code`, `prix_base`, `personnalisable`, `actif`, `prix_b2_b`, `mode_calcul`) VALUES
(1, 'Carte de visite professionnelle', 1, 'Carte de visite', 30, 1, 'CV001', 0, 1, 1, NULL, 'unite'),
(2, 'Papier à en-tête personnalisé', 1, 'Papier à en-tête', 10, 1, 'LT001', 0, 1, 1, NULL, 'unite'),
(3, 'Enveloppe personnalisée', 1, 'Enveloppe', 20, 1, 'EV001', 0, 1, 1, NULL, 'unite'),
(4, 'Carnet autocopiant', 1, 'Bon de commande', 40, 1, 'BC001', 0, 1, 1, NULL, 'unite'),
(5, 'Facture autocopiante', 1, 'Facture', 50, 1, 'FC001', 0, 1, 1, NULL, 'unite'),
(6, 'Carnet de reçus', 1, 'Reçu', 60, 1, 'RC001', 0, 1, 1, NULL, 'unite'),
(7, 'Carte de fidélité PVC ou papier', 1, 'Carte de fidélité', 70, 1, 'CT001', 0, 1, 1, NULL, 'unite'),
(8, 'Flyer publicitaire', 1, 'Flyer', 80, 2, 'FL001', 0, 1, 1, NULL, 'unite'),
(9, 'Dépliant plié', 1, 'Dépliant', 90, 2, 'DL001', 0, 1, 1, NULL, 'unite'),
(10, 'Brochure agrafée', 1, 'Brochure', 100, 2, 'BR001', 0, 1, 1, NULL, 'unite'),
(11, 'Catalogue produits', 1, 'Catalogue', 110, 2, 'CTG001', 0, 1, 1, NULL, 'unite'),
(12, 'Affiche publicitaire', 1, 'Affiche', 120, 2, 'AF001', 0, 1, 1, NULL, 'unite'),
(13, 'Chemise personnalisée', 1, 'Chemise à rabat', 130, 2, 'CH001', 0, 1, 1, NULL, 'unite'),
(14, 'Calendrier personnalisé', 1, 'Calendrier', 140, 2, 'CL001', 0, 1, 1, NULL, 'unite'),
(15, 'Panneau PVC', 1, 'Panneau PVC', 150, 3, 'PN001', 0, 1, 1, NULL, 'unite'),
(16, 'Plaque Akylux', 1, 'Plaque Akylux', 160, 3, 'AK001', 0, 1, 1, NULL, 'unite'),
(17, 'Plaque Plexiglas', 1, 'Plaque Plexiglas', 170, 3, 'PM001', 0, 1, 1, NULL, 'unite'),
(18, 'Sticker découpé', 1, 'Sticker', 180, 3, 'ST001', 0, 1, 1, NULL, 'unite'),
(19, 'Vitrophanie', 1, 'Vitrophanie', 190, 3, 'VT001', 0, 1, 1, NULL, 'unite'),
(20, 'Bâche publicitaire', 1, 'Bâche', 200, 4, 'BK001', 3500, 1, 1, NULL, 'unite'),
(21, 'Roll-up', 1, 'Roll-up', 210, 4, 'RU001', 0, 1, 1, NULL, 'unite'),
(22, 'Kakémono', 1, 'Kakémono', 220, 4, 'KK001', 35000, 1, 1, NULL, 'unite'),
(23, 'Toile Canvas', 1, 'Toile Canvas', 230, 4, 'TP001', 0, 1, 1, NULL, 'unite'),
(24, 'Badge personnalisé', 1, 'Badge', 240, 5, 'BD001', 0, 1, 1, NULL, 'unite'),
(25, 'Bracelet personnalisé', 1, 'Bracelet événementiel', 250, 5, 'BV001', 0, 1, 1, NULL, 'unite'),
(26, 'Ticket numéroté', 0, 'Ticket', 260, 5, 'TB001', 0, 1, 1, NULL, 'unite'),
(27, 'Étiquette en rouleau', 1, 'Roll Label', 270, 6, 'RL001', 0, 1, 1, NULL, 'unite'),
(28, 'Étiquette adhésive', 1, 'Étiquette', 280, 6, 'ET001', 0, 1, 1, NULL, 'unite'),
(29, 'Pochette personnalisée', 1, 'Pochette', 290, 6, 'PL001', 0, 1, 1, NULL, 'unite'),
(30, 'Impression sur T-shirt', 1, 'T-shirt', 300, 7, 'TS001', 0, 1, 1, NULL, 'unite'),
(31, 'Impression sur Polo', 1, 'Polo', 310, 7, 'PL002', 4000, 1, 1, NULL, 'unite'),
(32, 'Casquette personnalisée', 1, 'Casquette', 320, 7, 'CS001', 0, 1, 1, NULL, 'unite'),
(33, 'Gilet personnalisé', 1, 'Gilet', 340, 7, 'GB001', 0, 1, 1, NULL, 'unite'),
(34, 'Veste personnalisée', 1, 'Veste', 330, 7, 'VT002', 0, 1, 1, NULL, 'unite'),
(35, 'Boîte personnalisée', 1, 'Boîte', 350, 8, 'BX001', 0, 1, 1, NULL, 'unite'),
(36, 'Sac papier personnalisé', 1, 'Sac papier', 360, 8, 'SC001', 0, 1, 1, NULL, 'unite'),
(37, 'Sac biodégradable', 1, 'Sac biodégradable', 370, 8, 'SB001', 0, 1, 1, NULL, 'unite'),
(38, 'Mug personnalisé', 1, 'Mug', 380, 9, 'MG001', 0, 1, 1, NULL, 'unite'),
(39, 'Clé USB personnalisée', 1, 'Clé USB', 390, 9, 'CLF001', 0, 1, 1, NULL, 'unite'),
(40, 'Stylo personnalisé', 1, 'Stylo', 400, 9, 'STY001', 0, 1, 1, NULL, 'unite'),
(41, 'Agenda personnalisé', 1, 'Agenda', 410, 9, 'AG001', 0, 1, 1, NULL, 'unite'),
(42, 'Dossier administratif', 1, 'Dossier administratif', 420, 10, 'DS001', 0, 1, 1, NULL, 'unite'),
(43, 'Registre', 1, 'Registre', 430, 10, 'RG001', 0, 1, 1, NULL, 'unite'),
(44, 'Fiche administrative', 1, 'Fiche', 440, 10, 'FI001', 0, 1, 1, NULL, 'unite'),
(45, 'Carnet personnalisé', 1, 'Carnet', 450, 10, 'CN001', 0, 1, 1, NULL, 'unite');

-- --------------------------------------------------------

--
-- Structure de la table `produits_finition`
--

CREATE TABLE `produits_finition` (
  `produits_id` int(11) NOT NULL,
  `finition_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `produits_finition`
--

INSERT INTO `produits_finition` (`produits_id`, `finition_id`) VALUES
(1, 1),
(1, 4),
(1, 5),
(1, 22),
(1, 23),
(2, 1),
(4, 17),
(4, 18),
(5, 17),
(5, 18),
(6, 17),
(8, 1),
(8, 11),
(8, 13),
(8, 14),
(8, 15),
(8, 16),
(9, 1),
(9, 11),
(9, 13),
(9, 14),
(9, 15),
(9, 16),
(10, 10),
(10, 11),
(11, 12),
(12, 1),
(13, 1),
(13, 4),
(14, 11),
(18, 19),
(19, 19),
(20, 6),
(20, 7),
(20, 8),
(21, 22),
(22, 14),
(22, 48),
(23, 22),
(24, 22),
(25, 22),
(30, 20),
(31, 20),
(32, 20),
(33, 20),
(34, 20),
(39, 21),
(40, 21),
(41, 11);

-- --------------------------------------------------------

--
-- Structure de la table `produits_format`
--

CREATE TABLE `produits_format` (
  `produits_id` int(11) NOT NULL,
  `format_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `produits_format`
--

INSERT INTO `produits_format` (`produits_id`, `format_id`) VALUES
(1, 8),
(1, 9),
(2, 2),
(2, 3),
(3, 10),
(3, 11),
(3, 12),
(4, 2),
(4, 3),
(5, 2),
(5, 3),
(6, 2),
(6, 3),
(7, 8),
(8, 1),
(8, 2),
(8, 3),
(8, 4),
(9, 1),
(9, 2),
(9, 3),
(9, 4),
(9, 10),
(10, 2),
(10, 3),
(11, 2),
(11, 3),
(12, 3),
(12, 4),
(12, 5),
(12, 6),
(12, 7),
(13, 3),
(14, 3),
(14, 4),
(15, 16),
(16, 16),
(17, 16),
(18, 16),
(19, 16),
(20, 14),
(20, 15),
(20, 16),
(20, 18),
(20, 49),
(21, 13),
(21, 14),
(21, 15),
(22, 18),
(22, 19),
(22, 20),
(22, 21),
(22, 22),
(23, 16),
(24, 16),
(25, 16),
(26, 16),
(27, 16),
(28, 16),
(29, 16),
(30, 16),
(31, 1),
(31, 2),
(31, 3),
(31, 4),
(32, 16),
(33, 16),
(34, 16),
(35, 16),
(36, 16),
(37, 16),
(38, 16),
(39, 16),
(40, 16),
(41, 2),
(42, 3),
(43, 3),
(44, 3),
(45, 3);

-- --------------------------------------------------------

--
-- Structure de la table `produits_supports`
--

CREATE TABLE `produits_supports` (
  `produits_id` int(11) NOT NULL,
  `supports_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `produits_supports`
--

INSERT INTO `produits_supports` (`produits_id`, `supports_id`) VALUES
(1, 2),
(1, 3),
(1, 4),
(2, 1),
(3, 1),
(4, 14),
(5, 14),
(6, 14),
(7, 4),
(8, 2),
(8, 3),
(8, 4),
(8, 8),
(9, 2),
(9, 3),
(9, 4),
(9, 5),
(10, 2),
(11, 2),
(12, 2),
(13, 3),
(14, 2),
(15, 4),
(16, 7),
(17, 4),
(18, 5),
(18, 6),
(19, 6),
(20, 8),
(20, 9),
(20, 10),
(20, 11),
(21, 11),
(22, 32),
(23, 10),
(24, 16),
(25, 17),
(26, 1),
(27, 17),
(28, 17),
(29, 13),
(30, 12),
(31, 20),
(31, 21),
(32, 12),
(33, 12),
(34, 12),
(35, 13),
(36, 13),
(37, 13),
(38, 15),
(39, 16),
(40, 17),
(41, 2),
(42, 1),
(43, 1),
(44, 1),
(45, 1);

-- --------------------------------------------------------

--
-- Structure de la table `produits_types_impression`
--

CREATE TABLE `produits_types_impression` (
  `produits_id` int(11) NOT NULL,
  `types_impression_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `produits_types_impression`
--

INSERT INTO `produits_types_impression` (`produits_id`, `types_impression_id`) VALUES
(1, 4),
(1, 5),
(2, 1),
(2, 2),
(3, 1),
(3, 2),
(4, 1),
(4, 2),
(5, 1),
(5, 2),
(6, 1),
(6, 2),
(7, 1),
(7, 2),
(8, 4),
(8, 5),
(8, 6),
(8, 8),
(9, 5),
(9, 6),
(9, 8),
(10, 1),
(10, 2),
(11, 1),
(11, 2),
(12, 1),
(12, 2),
(13, 2),
(14, 1),
(14, 2),
(15, 6),
(16, 6),
(17, 6),
(18, 3),
(18, 6),
(19, 3),
(19, 6),
(20, 2),
(21, 3),
(22, 2),
(23, 3),
(24, 5),
(24, 6),
(25, 5),
(26, 1),
(27, 1),
(27, 2),
(28, 1),
(28, 2),
(29, 1),
(29, 2),
(30, 4),
(30, 5),
(30, 9),
(31, 1),
(31, 9),
(31, 10),
(32, 4),
(32, 8),
(33, 4),
(33, 5),
(34, 4),
(34, 5),
(35, 1),
(35, 2),
(36, 1),
(36, 2),
(37, 1),
(37, 2),
(38, 5),
(39, 6),
(40, 6),
(40, 7),
(41, 1),
(41, 2),
(42, 1),
(42, 2),
(43, 1),
(43, 2),
(44, 1),
(44, 2),
(45, 1),
(45, 2);

-- --------------------------------------------------------

--
-- Structure de la table `produit_configuration`
--

CREATE TABLE `produit_configuration` (
  `id` int(11) NOT NULL,
  `active` tinyint(4) NOT NULL,
  `ordre` int(11) NOT NULL,
  `description` longtext DEFAULT NULL,
  `prix_base` int(11) DEFAULT NULL,
  `mode_calcul` varchar(30) NOT NULL,
  `quantite_minimale` int(11) NOT NULL,
  `quantite_maximale` int(11) DEFAULT NULL,
  `produit_id` int(11) NOT NULL,
  `type_impression_id` int(11) NOT NULL,
  `support_id` int(11) NOT NULL,
  `format_id` int(11) DEFAULT NULL,
  `prix_b2_b` int(11) DEFAULT NULL,
  `mode_dimension` varchar(20) NOT NULL DEFAULT 'format',
  `largeur_defaut` decimal(10,3) DEFAULT NULL,
  `longueur_defaut` decimal(10,3) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `produit_configuration`
--

INSERT INTO `produit_configuration` (`id`, `active`, `ordre`, `description`, `prix_base`, `mode_calcul`, `quantite_minimale`, `quantite_maximale`, `produit_id`, `type_impression_id`, `support_id`, `format_id`, `prix_b2_b`, `mode_dimension`, `largeur_defaut`, `longueur_defaut`) VALUES
(1, 1, 40, NULL, 5000, 'forfait', 100, NULL, 1, 4, 4, 8, NULL, 'format', NULL, NULL),
(2, 1, 10, NULL, 250, 'forfait', 20, NULL, 8, 4, 3, 3, NULL, 'format', NULL, NULL),
(3, 1, 30, NULL, 35000, 'forfait', 1, NULL, 22, 2, 32, 18, NULL, 'format', NULL, NULL),
(4, 1, 20, NULL, 70000, 'forfait', 1, NULL, 22, 2, 32, 20, NULL, 'format', NULL, NULL),
(5, 1, 10, NULL, 7000, 'forfait', 1, NULL, 20, 2, 10, 49, NULL, 'format', NULL, NULL);

-- --------------------------------------------------------

--
-- Structure de la table `produit_configuration_finition`
--

CREATE TABLE `produit_configuration_finition` (
  `id` int(11) NOT NULL,
  `obligatoire` tinyint(4) NOT NULL,
  `selectionnee_par_defaut` tinyint(4) NOT NULL,
  `payante` tinyint(4) NOT NULL,
  `prix` int(11) NOT NULL,
  `mode_calcul` varchar(30) NOT NULL,
  `quantite_minimale` int(11) NOT NULL,
  `quantite_maximale` int(11) DEFAULT NULL,
  `active` tinyint(4) NOT NULL,
  `ordre` int(11) NOT NULL,
  `description` varchar(500) DEFAULT NULL,
  `produit_configuration_id` int(11) NOT NULL,
  `finition_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `produit_configuration_finition`
--

INSERT INTO `produit_configuration_finition` (`id`, `obligatoire`, `selectionnee_par_defaut`, `payante`, `prix`, `mode_calcul`, `quantite_minimale`, `quantite_maximale`, `active`, `ordre`, `description`, `produit_configuration_id`, `finition_id`) VALUES
(1, 1, 1, 1, 200, 'unite', 1, NULL, 1, 10, '', 1, 23),
(2, 0, 0, 1, 20, 'forfait', 1, NULL, 1, 10, '', 2, 13),
(3, 0, 0, 0, 0, 'forfait', 1, NULL, 1, 10, '', 2, 11),
(4, 1, 1, 0, 0, 'forfait', 1, NULL, 1, 10, '', 3, 48),
(5, 0, 0, 0, 0, 'forfait', 1, NULL, 1, 10, '', 4, 48),
(6, 1, 1, 0, 0, 'forfait', 1, NULL, 1, 10, '', 5, 8);

-- --------------------------------------------------------

--
-- Structure de la table `stock_entrees`
--

CREATE TABLE `stock_entrees` (
  `id` int(11) NOT NULL,
  `quantites` int(11) NOT NULL,
  `prix` int(11) NOT NULL,
  `date` datetime NOT NULL,
  `article_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `stock_sorties`
--

CREATE TABLE `stock_sorties` (
  `id` int(11) NOT NULL,
  `quantite` int(11) NOT NULL,
  `date` datetime NOT NULL,
  `article_id` int(11) DEFAULT NULL,
  `commande_detail_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `supports`
--

CREATE TABLE `supports` (
  `id` int(11) NOT NULL,
  `nom` varchar(255) NOT NULL,
  `description` longtext NOT NULL,
  `publie` tinyint(4) NOT NULL,
  `ordre` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `supports`
--

INSERT INTO `supports` (`id`, `nom`, `description`, `publie`, `ordre`) VALUES
(1, 'Papier offset 80 g', 'Papier non couché utilisé pour les impressions courantes, documents administratifs, blocs et carnets.', 1, 10),
(2, 'Papier couché mat 135 g', 'Papier couché mat adapté aux flyers, affiches, dépliants et documents publicitaires.', 1, 20),
(3, 'Papier couché brillant 170 g', 'Papier brillant destiné aux flyers, brochures et impressions promotionnelles.', 1, 30),
(4, 'Papier couché 300 g', 'Papier épais adapté aux cartes de visite, couvertures, invitations et cartes commerciales.', 1, 40),
(5, 'Bristol 250 g', 'Papier cartonné rigide utilisé pour les cartes, invitations, chemises et supports promotionnels.', 1, 50),
(6, 'Papier kraft', 'Papier naturel brun utilisé pour les emballages, étiquettes, cartes et créations écologiques.', 1, 60),
(7, 'Papier photo brillant', 'Papier haute définition destiné à l’impression de photographies et visuels de qualité.', 1, 70),
(8, 'Papier autocollant', 'Papier adhésif imprimable destiné aux étiquettes, stickers et autocollants.', 1, 80),
(9, 'Papier plan 80 g', 'Papier en rouleau destiné à l’impression de plans d’architecture et de documents techniques.', 1, 90),
(10, 'Bâche Frontlit 440 g', 'Bâche PVC blanche pour impression grand format intérieure et extérieure.', 1, 100),
(11, 'Bâche Backlit', 'Bâche translucide destinée aux caissons lumineux et supports rétroéclairés.', 1, 110),
(12, 'Vinyle adhésif blanc', 'Vinyle blanc imprimable utilisé pour les stickers, enseignes, vitrines et véhicules.', 1, 120),
(13, 'Vinyle adhésif transparent', 'Vinyle transparent utilisé pour les vitrines, objets et supports nécessitant de la transparence.', 1, 130),
(14, 'Vinyle microperforé One Way Vision', 'Vinyle microperforé destiné aux vitrines et surfaces vitrées.', 1, 140),
(15, 'Toile Canvas', 'Toile textile destinée aux tableaux décoratifs et reproductions artistiques.', 1, 150),
(16, 'Film Backlit', 'Film translucide imprimable destiné aux caissons et affichages lumineux.', 1, 160),
(17, 'Film DTF standard', 'Film PET utilisé pour l’impression et le transfert DTF sur textile.', 1, 170),
(18, 'Film DTF pailleté', 'Film DTF spécial produisant un effet pailleté sur le textile.', 1, 180),
(19, 'Papier sublimation', 'Papier transfert utilisé pour la sublimation sur textile polyester et objets compatibles.', 1, 190),
(20, 'T-shirt coton', 'T-shirt en coton compatible avec le DTF et l’impression directe textile.', 1, 200),
(21, 'Polo', 'Polo textile compatible avec le marquage DTF, la broderie et certains transferts.', 1, 210),
(22, 'Sweat', 'Vêtement épais compatible avec le DTF et le marquage textile.', 1, 220),
(23, 'Casquette', 'Casquette compatible avec le DTF, la sublimation et le transfert textile.', 1, 230),
(24, 'Tote bag', 'Sac textile compatible avec le DTF, la sublimation et le marquage.', 1, 240),
(25, 'Mug sublimable', 'Mug spécialement traité pour recevoir une impression par sublimation.', 1, 250),
(26, 'PVC expansé', 'Plaque légère et rigide utilisée pour la signalétique et les panneaux.', 1, 260),
(27, 'Forex', 'Plaque PVC expansée utilisée pour les panneaux publicitaires et la décoration.', 1, 270),
(28, 'Dibond', 'Panneau composite aluminium utilisé pour les enseignes et la signalétique durable.', 1, 280),
(29, 'Plexiglas', 'Plaque transparente ou opaque destinée à l’impression UV et à la signalétique.', 1, 290),
(30, 'Bois', 'Support rigide naturel compatible avec l’impression UV et la personnalisation.', 1, 300),
(31, 'Aluminium', 'Plaque métallique compatible avec l’impression UV et la signalétique.', 1, 310),
(32, 'Film polypropylène dos gris', 'Le support premium anti-reflet et 100% opaque pour vos roll-ups et kakémonos intérieurs. Ses bords restent parfaitement plats sans jamais gondoler.', 1, 320);

-- --------------------------------------------------------

--
-- Structure de la table `support_finition`
--

CREATE TABLE `support_finition` (
  `support_id` int(11) NOT NULL,
  `finition_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `support_finition`
--

INSERT INTO `support_finition` (`support_id`, `finition_id`) VALUES
(1, 11),
(1, 12),
(1, 13),
(1, 14),
(1, 15),
(1, 16),
(1, 17),
(1, 18),
(2, 11),
(2, 12),
(2, 13),
(2, 14),
(2, 15),
(2, 16),
(2, 17),
(2, 18),
(2, 22),
(2, 23),
(3, 11),
(3, 12),
(3, 13),
(3, 14),
(3, 15),
(3, 16),
(3, 17),
(3, 18),
(3, 22),
(3, 23),
(4, 11),
(4, 12),
(4, 22),
(4, 23),
(4, 24),
(4, 25),
(5, 11),
(5, 12),
(5, 22),
(5, 23),
(5, 24),
(6, 11),
(6, 12),
(6, 13),
(7, 11),
(7, 22),
(7, 23),
(8, 11),
(8, 36),
(8, 37),
(9, 11),
(9, 13),
(10, 1),
(10, 8),
(10, 9),
(10, 10),
(11, 1),
(11, 8),
(11, 9),
(12, 1),
(12, 2),
(12, 3),
(12, 4),
(12, 5),
(13, 1),
(13, 2),
(13, 3),
(13, 4),
(13, 5),
(14, 1),
(14, 4),
(14, 5),
(15, 1),
(15, 40),
(16, 1),
(16, 4),
(17, 26),
(17, 27),
(17, 28),
(17, 29),
(17, 30),
(18, 26),
(18, 27),
(18, 28),
(18, 29),
(18, 30),
(19, 33),
(19, 34),
(19, 35),
(20, 30),
(20, 31),
(20, 32),
(21, 30),
(21, 31),
(21, 32),
(22, 30),
(22, 31),
(22, 32),
(23, 30),
(23, 31),
(24, 30),
(24, 31),
(24, 32),
(25, 33),
(25, 35),
(26, 1),
(26, 6),
(27, 1),
(27, 6),
(28, 1),
(28, 7),
(29, 1),
(30, 1),
(31, 1),
(32, 48);

-- --------------------------------------------------------

--
-- Structure de la table `support_format`
--

CREATE TABLE `support_format` (
  `support_id` int(11) NOT NULL,
  `format_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `support_format`
--

INSERT INTO `support_format` (`support_id`, `format_id`) VALUES
(1, 1),
(1, 2),
(1, 3),
(1, 4),
(1, 5),
(1, 10),
(2, 1),
(2, 2),
(2, 3),
(2, 4),
(2, 5),
(2, 10),
(2, 13),
(2, 14),
(3, 1),
(3, 2),
(3, 3),
(3, 4),
(3, 5),
(3, 10),
(3, 13),
(3, 14),
(4, 1),
(4, 2),
(4, 3),
(4, 4),
(4, 8),
(4, 10),
(4, 11),
(4, 12),
(5, 1),
(5, 2),
(5, 3),
(5, 4),
(5, 8),
(5, 9),
(5, 11),
(5, 12),
(6, 1),
(6, 2),
(6, 3),
(6, 4),
(6, 8),
(6, 11),
(7, 1),
(7, 2),
(7, 3),
(7, 4),
(7, 41),
(7, 42),
(7, 43),
(7, 44),
(8, 1),
(8, 2),
(8, 3),
(8, 4),
(8, 11),
(8, 12),
(8, 27),
(8, 28),
(8, 29),
(8, 30),
(9, 4),
(9, 5),
(9, 6),
(9, 7),
(10, 18),
(10, 19),
(10, 20),
(10, 21),
(10, 22),
(10, 23),
(10, 24),
(10, 25),
(10, 26),
(10, 49),
(11, 23),
(11, 24),
(11, 25),
(11, 26),
(12, 3),
(12, 4),
(12, 5),
(12, 6),
(12, 7),
(12, 13),
(12, 14),
(12, 15),
(12, 16),
(12, 17),
(12, 27),
(12, 28),
(12, 29),
(12, 30),
(13, 3),
(13, 4),
(13, 5),
(13, 6),
(13, 7),
(13, 13),
(13, 14),
(13, 15),
(13, 16),
(13, 17),
(13, 27),
(13, 28),
(13, 29),
(13, 30),
(14, 13),
(14, 14),
(14, 15),
(14, 16),
(14, 17),
(15, 38),
(15, 39),
(15, 40),
(16, 13),
(16, 14),
(16, 15),
(16, 16),
(16, 17),
(17, 2),
(17, 3),
(17, 4),
(17, 31),
(17, 32),
(17, 33),
(17, 34),
(17, 35),
(18, 2),
(18, 3),
(18, 4),
(18, 31),
(18, 32),
(18, 33),
(18, 34),
(18, 35),
(19, 2),
(19, 3),
(19, 4),
(19, 31),
(19, 32),
(19, 33),
(19, 34),
(19, 35),
(19, 36),
(19, 37),
(20, 31),
(20, 32),
(20, 33),
(20, 34),
(20, 35),
(21, 31),
(21, 32),
(21, 33),
(21, 34),
(21, 35),
(22, 31),
(22, 32),
(22, 33),
(22, 34),
(22, 35),
(23, 31),
(23, 32),
(24, 31),
(24, 32),
(24, 33),
(24, 34),
(25, 36),
(25, 37),
(26, 45),
(26, 46),
(26, 47),
(26, 48),
(27, 45),
(27, 46),
(27, 47),
(27, 48),
(28, 45),
(28, 46),
(28, 47),
(28, 48),
(29, 45),
(29, 46),
(29, 47),
(30, 45),
(30, 46),
(30, 47),
(31, 45),
(31, 46),
(31, 47),
(31, 48),
(32, 18),
(32, 19),
(32, 20),
(32, 21),
(32, 22);

-- --------------------------------------------------------

--
-- Structure de la table `support_types_impression`
--

CREATE TABLE `support_types_impression` (
  `support_id` int(11) NOT NULL,
  `types_impression_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `support_types_impression`
--

INSERT INTO `support_types_impression` (`support_id`, `types_impression_id`) VALUES
(1, 4),
(1, 5),
(1, 6),
(1, 7),
(1, 8),
(2, 4),
(2, 7),
(2, 8),
(3, 4),
(3, 7),
(3, 8),
(4, 4),
(4, 7),
(4, 8),
(5, 4),
(5, 7),
(5, 8),
(6, 4),
(6, 7),
(6, 8),
(7, 4),
(7, 8),
(7, 19),
(8, 4),
(8, 7),
(8, 8),
(8, 14),
(9, 5),
(9, 8),
(9, 20),
(10, 2),
(10, 12),
(10, 13),
(11, 2),
(11, 13),
(12, 2),
(12, 3),
(12, 11),
(12, 14),
(13, 2),
(13, 3),
(13, 11),
(13, 14),
(14, 2),
(14, 11),
(14, 14),
(15, 2),
(15, 3),
(15, 18),
(16, 2),
(16, 3),
(17, 1),
(18, 1),
(19, 9),
(20, 1),
(20, 9),
(20, 10),
(21, 1),
(21, 9),
(21, 10),
(22, 1),
(22, 10),
(23, 1),
(23, 9),
(24, 1),
(24, 9),
(24, 10),
(25, 9),
(26, 2),
(26, 3),
(26, 15),
(27, 2),
(27, 3),
(27, 17),
(28, 2),
(28, 3),
(28, 16),
(29, 3),
(30, 3),
(31, 3),
(31, 16),
(32, 2);

-- --------------------------------------------------------

--
-- Structure de la table `types_impression`
--

CREATE TABLE `types_impression` (
  `id` int(11) NOT NULL,
  `nom` varchar(255) NOT NULL,
  `description` varchar(255) NOT NULL,
  `publie` tinyint(4) NOT NULL,
  `ordre` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `types_impression`
--

INSERT INTO `types_impression` (`id`, `nom`, `description`, `publie`, `ordre`) VALUES
(1, 'Impression DTF', 'Impression Direct To Film sur film PET pour transfert textile.', 1, 10),
(2, 'Impression Traceur Éco-solvant', 'Impression grand format sur vinyle, bâche, adhésif et autres supports.', 1, 20),
(3, 'Impression UV', 'Impression UV directe sur supports rigides et souples.', 1, 30),
(4, 'Impression Laser Couleur', 'Impression numérique laser couleur petit format.', 1, 40),
(5, 'Impression Laser Noir & Blanc', 'Impression numérique laser noir et blanc.', 1, 50),
(6, 'Photocopie', 'Photocopie couleur et noir & blanc.', 1, 60),
(7, 'Impression Offset', 'Impression offset pour les grandes séries.', 0, 70),
(8, 'Impression Numérique', 'Impression numérique haute qualité.', 1, 80),
(9, 'Impression Sublimation', 'Impression par sublimation sur textile et objets.', 1, 90),
(10, 'Impression DTG', 'Impression directe sur textile (Direct To Garment).', 1, 100),
(11, 'Impression Vinyle Découpe', 'Découpe de vinyle adhésif et transfert.', 1, 110),
(12, 'Impression Roll-up', 'Fabrication de Roll-up et Kakémonos.', 1, 120),
(13, 'Impression Bâche', 'Impression sur bâche PVC intérieure et extérieure.', 1, 130),
(14, 'Impression Autocollant', 'Impression d’étiquettes et autocollants.', 1, 140),
(15, 'Impression PVC', 'Impression sur plaques PVC expansé.', 1, 150),
(16, 'Impression Dibond', 'Impression sur panneaux aluminium Dibond.', 0, 160),
(17, 'Impression Forex', 'Impression sur panneaux Forex.', 1, 170),
(18, 'Impression Toile Canvas', 'Impression sur toile artistique Canvas.', 1, 180),
(19, 'Impression Papier Photo', 'Impression sur papier photo haute résolution.', 1, 190),
(20, 'Impression Plan', 'Impression de plans d’architecture et d’ingénierie.', 1, 200);

-- --------------------------------------------------------

--
-- Structure de la table `user`
--

CREATE TABLE `user` (
  `id` int(11) NOT NULL,
  `username` varchar(180) NOT NULL,
  `roles` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`roles`)),
  `password` varchar(255) NOT NULL,
  `actif` tinyint(4) NOT NULL,
  `employe_id` int(11) NOT NULL,
  `date_add` datetime NOT NULL,
  `date_update` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `user`
--

INSERT INTO `user` (`id`, `username`, `roles`, `password`, `actif`, `employe_id`, `date_add`, `date_update`) VALUES
(1, 'ydiallo', '[\"ROLE_ADMIN\"]', '$2y$13$.ViZRrVjSaGOET/4o9hQL.C57N//UmLWsv3ZmXN1727JR9RMn23.C', 1, 1, '0000-00-00 00:00:00', '2026-07-22 23:22:52');

--
-- Index pour les tables déchargées
--

--
-- Index pour la table `articles`
--
ALTER TABLE `articles`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `categorie_produit`
--
ALTER TABLE `categorie_produit`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `UNIQ_762642856C6E55B5` (`nom`);

--
-- Index pour la table `clients`
--
ALTER TABLE `clients`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `UNIQ_C82E7477153098` (`code`),
  ADD UNIQUE KEY `UNIQ_C82E74450FF010` (`telephone`);

--
-- Index pour la table `commandes`
--
ALTER TABLE `commandes`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `UNIQ_35D4282CF55AE19E` (`numero`),
  ADD KEY `IDX_35D4282CAB014612` (`clients_id`),
  ADD KEY `IDX_35D4282C709770DC` (`agents_id`);

--
-- Index pour la table `commandes_details`
--
ALTER TABLE `commandes_details`
  ADD PRIMARY KEY (`id`),
  ADD KEY `IDX_B48B83DA82EA2E54` (`commande_id`),
  ADD KEY `IDX_B48B83DAF347EFB` (`produit_id`),
  ADD KEY `IDX_B48B83DAD357F183` (`type_impression_id`),
  ADD KEY `IDX_B48B83DA315B405` (`support_id`),
  ADD KEY `IDX_B48B83DAF6B75B26` (`machine_id`),
  ADD KEY `IDX_B48B83DAD629F605` (`format_id`),
  ADD KEY `IDX_B48B83DA806A5250` (`produit_configuration_id`);

--
-- Index pour la table `commande_detail_fichier`
--
ALTER TABLE `commande_detail_fichier`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `UNIQ_39E2DA1052C87F80` (`jeton_upload`),
  ADD KEY `IDX_39E2DA10C8DC59F9` (`commande_detail_id`);

--
-- Index pour la table `commande_detail_finition`
--
ALTER TABLE `commande_detail_finition`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uniq_commande_detail_finition` (`commande_detail_id`,`finition_id`),
  ADD KEY `IDX_B07D7138C8DC59F9` (`commande_detail_id`),
  ADD KEY `IDX_B07D7138A0C197D7` (`configuration_finition_id`),
  ADD KEY `IDX_B07D7138CB56F5AF` (`finition_id`);

--
-- Index pour la table `consommation_encres`
--
ALTER TABLE `consommation_encres`
  ADD PRIMARY KEY (`id`),
  ADD KEY `IDX_31C495E1ECC6147F` (`production_id`);

--
-- Index pour la table `devis`
--
ALTER TABLE `devis`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uniq_devis_numero` (`numero`),
  ADD UNIQUE KEY `UNIQ_8B27C52B82EA2E54` (`commande_id`),
  ADD KEY `IDX_8B27C52B19EB6921` (`client_id`);

--
-- Index pour la table `devis_details`
--
ALTER TABLE `devis_details`
  ADD PRIMARY KEY (`id`),
  ADD KEY `IDX_E0C890D641DEFADA` (`devis_id`),
  ADD KEY `IDX_E0C890D6F347EFB` (`produit_id`),
  ADD KEY `IDX_E0C890D6806A5250` (`produit_configuration_id`),
  ADD KEY `IDX_E0C890D6D357F183` (`type_impression_id`),
  ADD KEY `IDX_E0C890D6315B405` (`support_id`),
  ADD KEY `IDX_E0C890D6D629F605` (`format_id`);

--
-- Index pour la table `devis_detail_finition`
--
ALTER TABLE `devis_detail_finition`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uniq_devis_detail_finition` (`devis_detail_id`,`finition_id`),
  ADD KEY `IDX_BE70DB30A903C9C1` (`devis_detail_id`),
  ADD KEY `IDX_BE70DB30A0C197D7` (`configuration_finition_id`),
  ADD KEY `IDX_BE70DB30CB56F5AF` (`finition_id`);

--
-- Index pour la table `doctrine_migration_versions`
--
ALTER TABLE `doctrine_migration_versions`
  ADD PRIMARY KEY (`version`);

--
-- Index pour la table `employes`
--
ALTER TABLE `employes`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `factures`
--
ALTER TABLE `factures`
  ADD PRIMARY KEY (`id`),
  ADD KEY `IDX_647590B82EA2E54` (`commande_id`);

--
-- Index pour la table `finition`
--
ALTER TABLE `finition`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `finition_types_impression`
--
ALTER TABLE `finition_types_impression`
  ADD PRIMARY KEY (`finition_id`,`types_impression_id`),
  ADD KEY `IDX_4EB60CFECB56F5AF` (`finition_id`),
  ADD KEY `IDX_4EB60CFE9719B876` (`types_impression_id`);

--
-- Index pour la table `format`
--
ALTER TABLE `format`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `format_types_impression`
--
ALTER TABLE `format_types_impression`
  ADD PRIMARY KEY (`format_id`,`types_impression_id`),
  ADD KEY `IDX_5CE0BAD8D629F605` (`format_id`),
  ADD KEY `IDX_5CE0BAD89719B876` (`types_impression_id`);

--
-- Index pour la table `fournisseurs`
--
ALTER TABLE `fournisseurs`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `machines`
--
ALTER TABLE `machines`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `maintenance`
--
ALTER TABLE `maintenance`
  ADD PRIMARY KEY (`id`),
  ADD KEY `IDX_2F84F8E9F6B75B26` (`machine_id`);

--
-- Index pour la table `messenger_messages`
--
ALTER TABLE `messenger_messages`
  ADD PRIMARY KEY (`id`),
  ADD KEY `IDX_75EA56E0FB7336F0E3BD61CE16BA31DBBF396750` (`queue_name`,`available_at`,`delivered_at`,`id`);

--
-- Index pour la table `paiements`
--
ALTER TABLE `paiements`
  ADD PRIMARY KEY (`id`),
  ADD KEY `IDX_E1B02E1282EA2E54` (`commande_id`),
  ADD KEY `IDX_E1B02E12A4FBCD6F` (`encaisse_par_id`);

--
-- Index pour la table `production`
--
ALTER TABLE `production`
  ADD PRIMARY KEY (`id`),
  ADD KEY `IDX_D3EDB1E023D82BC4` (`commande_details_id`),
  ADD KEY `IDX_D3EDB1E0F6B75B26` (`machine_id`);

--
-- Index pour la table `produits`
--
ALTER TABLE `produits`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `UNIQ_BE2DDF8C6C6E55B5` (`nom`),
  ADD UNIQUE KEY `UNIQ_BE2DDF8C77153098` (`code`),
  ADD KEY `IDX_BE2DDF8C91FDB457` (`categorie_produit_id`);

--
-- Index pour la table `produits_finition`
--
ALTER TABLE `produits_finition`
  ADD PRIMARY KEY (`produits_id`,`finition_id`),
  ADD KEY `IDX_DF5600F4CD11A2CF` (`produits_id`),
  ADD KEY `IDX_DF5600F4CB56F5AF` (`finition_id`);

--
-- Index pour la table `produits_format`
--
ALTER TABLE `produits_format`
  ADD PRIMARY KEY (`produits_id`,`format_id`),
  ADD KEY `IDX_4FAB693CCD11A2CF` (`produits_id`),
  ADD KEY `IDX_4FAB693CD629F605` (`format_id`);

--
-- Index pour la table `produits_supports`
--
ALTER TABLE `produits_supports`
  ADD PRIMARY KEY (`produits_id`,`supports_id`),
  ADD KEY `IDX_42046455CD11A2CF` (`produits_id`),
  ADD KEY `IDX_4204645597185C1E` (`supports_id`);

--
-- Index pour la table `produits_types_impression`
--
ALTER TABLE `produits_types_impression`
  ADD PRIMARY KEY (`produits_id`,`types_impression_id`),
  ADD KEY `IDX_1ADC26C2CD11A2CF` (`produits_id`),
  ADD KEY `IDX_1ADC26C29719B876` (`types_impression_id`);

--
-- Index pour la table `produit_configuration`
--
ALTER TABLE `produit_configuration`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uniq_produit_configuration` (`produit_id`,`type_impression_id`,`support_id`,`format_id`),
  ADD KEY `IDX_8BBC0309F347EFB` (`produit_id`),
  ADD KEY `IDX_8BBC0309D357F183` (`type_impression_id`),
  ADD KEY `IDX_8BBC0309315B405` (`support_id`),
  ADD KEY `IDX_8BBC0309D629F605` (`format_id`);

--
-- Index pour la table `produit_configuration_finition`
--
ALTER TABLE `produit_configuration_finition`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uniq_configuration_finition` (`produit_configuration_id`,`finition_id`),
  ADD KEY `IDX_BF2ECD31806A5250` (`produit_configuration_id`),
  ADD KEY `IDX_BF2ECD31CB56F5AF` (`finition_id`);

--
-- Index pour la table `stock_entrees`
--
ALTER TABLE `stock_entrees`
  ADD PRIMARY KEY (`id`),
  ADD KEY `IDX_3D445A027294869C` (`article_id`);

--
-- Index pour la table `stock_sorties`
--
ALTER TABLE `stock_sorties`
  ADD PRIMARY KEY (`id`),
  ADD KEY `IDX_5127734B7294869C` (`article_id`),
  ADD KEY `IDX_5127734BC8DC59F9` (`commande_detail_id`);

--
-- Index pour la table `supports`
--
ALTER TABLE `supports`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `support_finition`
--
ALTER TABLE `support_finition`
  ADD PRIMARY KEY (`support_id`,`finition_id`),
  ADD KEY `IDX_94D67319CB56F5AF` (`finition_id`),
  ADD KEY `IDX_94D67319315B405` (`support_id`);

--
-- Index pour la table `support_format`
--
ALTER TABLE `support_format`
  ADD PRIMARY KEY (`support_id`,`format_id`),
  ADD KEY `IDX_5640922FD629F605` (`format_id`),
  ADD KEY `IDX_5640922F315B405` (`support_id`);

--
-- Index pour la table `support_types_impression`
--
ALTER TABLE `support_types_impression`
  ADD PRIMARY KEY (`support_id`,`types_impression_id`),
  ADD KEY `IDX_EE1AA1449719B876` (`types_impression_id`),
  ADD KEY `IDX_EE1AA144315B405` (`support_id`);

--
-- Index pour la table `types_impression`
--
ALTER TABLE `types_impression`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `UNIQ_IDENTIFIER_USERNAME` (`username`),
  ADD UNIQUE KEY `UNIQ_8D93D6491B65292` (`employe_id`);

--
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `articles`
--
ALTER TABLE `articles`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `categorie_produit`
--
ALTER TABLE `categorie_produit`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT pour la table `clients`
--
ALTER TABLE `clients`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT pour la table `commandes`
--
ALTER TABLE `commandes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT pour la table `commandes_details`
--
ALTER TABLE `commandes_details`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT pour la table `commande_detail_fichier`
--
ALTER TABLE `commande_detail_fichier`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT pour la table `commande_detail_finition`
--
ALTER TABLE `commande_detail_finition`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT pour la table `consommation_encres`
--
ALTER TABLE `consommation_encres`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `devis`
--
ALTER TABLE `devis`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `devis_details`
--
ALTER TABLE `devis_details`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `devis_detail_finition`
--
ALTER TABLE `devis_detail_finition`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `employes`
--
ALTER TABLE `employes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT pour la table `factures`
--
ALTER TABLE `factures`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `finition`
--
ALTER TABLE `finition`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=49;

--
-- AUTO_INCREMENT pour la table `format`
--
ALTER TABLE `format`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=50;

--
-- AUTO_INCREMENT pour la table `fournisseurs`
--
ALTER TABLE `fournisseurs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `machines`
--
ALTER TABLE `machines`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `maintenance`
--
ALTER TABLE `maintenance`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `messenger_messages`
--
ALTER TABLE `messenger_messages`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `paiements`
--
ALTER TABLE `paiements`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT pour la table `production`
--
ALTER TABLE `production`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `produits`
--
ALTER TABLE `produits`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=46;

--
-- AUTO_INCREMENT pour la table `produit_configuration`
--
ALTER TABLE `produit_configuration`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT pour la table `produit_configuration_finition`
--
ALTER TABLE `produit_configuration_finition`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT pour la table `stock_entrees`
--
ALTER TABLE `stock_entrees`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `stock_sorties`
--
ALTER TABLE `stock_sorties`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `supports`
--
ALTER TABLE `supports`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=33;

--
-- AUTO_INCREMENT pour la table `types_impression`
--
ALTER TABLE `types_impression`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;

--
-- AUTO_INCREMENT pour la table `user`
--
ALTER TABLE `user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `commandes`
--
ALTER TABLE `commandes`
  ADD CONSTRAINT `FK_35D4282C709770DC` FOREIGN KEY (`agents_id`) REFERENCES `user` (`id`),
  ADD CONSTRAINT `FK_35D4282CAB014612` FOREIGN KEY (`clients_id`) REFERENCES `clients` (`id`);

--
-- Contraintes pour la table `commandes_details`
--
ALTER TABLE `commandes_details`
  ADD CONSTRAINT `FK_B48B83DA315B405` FOREIGN KEY (`support_id`) REFERENCES `supports` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `FK_B48B83DA806A5250` FOREIGN KEY (`produit_configuration_id`) REFERENCES `produit_configuration` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `FK_B48B83DA82EA2E54` FOREIGN KEY (`commande_id`) REFERENCES `commandes` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `FK_B48B83DAD357F183` FOREIGN KEY (`type_impression_id`) REFERENCES `types_impression` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `FK_B48B83DAD629F605` FOREIGN KEY (`format_id`) REFERENCES `format` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `FK_B48B83DAF347EFB` FOREIGN KEY (`produit_id`) REFERENCES `produits` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `FK_B48B83DAF6B75B26` FOREIGN KEY (`machine_id`) REFERENCES `machines` (`id`) ON DELETE SET NULL;

--
-- Contraintes pour la table `commande_detail_fichier`
--
ALTER TABLE `commande_detail_fichier`
  ADD CONSTRAINT `FK_39E2DA10C8DC59F9` FOREIGN KEY (`commande_detail_id`) REFERENCES `commandes_details` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `commande_detail_finition`
--
ALTER TABLE `commande_detail_finition`
  ADD CONSTRAINT `FK_B07D7138A0C197D7` FOREIGN KEY (`configuration_finition_id`) REFERENCES `produit_configuration_finition` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `FK_B07D7138C8DC59F9` FOREIGN KEY (`commande_detail_id`) REFERENCES `commandes_details` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `FK_B07D7138CB56F5AF` FOREIGN KEY (`finition_id`) REFERENCES `finition` (`id`);

--
-- Contraintes pour la table `consommation_encres`
--
ALTER TABLE `consommation_encres`
  ADD CONSTRAINT `FK_31C495E1ECC6147F` FOREIGN KEY (`production_id`) REFERENCES `production` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `devis`
--
ALTER TABLE `devis`
  ADD CONSTRAINT `FK_8B27C52B19EB6921` FOREIGN KEY (`client_id`) REFERENCES `clients` (`id`),
  ADD CONSTRAINT `FK_8B27C52B82EA2E54` FOREIGN KEY (`commande_id`) REFERENCES `commandes` (`id`) ON DELETE SET NULL;

--
-- Contraintes pour la table `devis_details`
--
ALTER TABLE `devis_details`
  ADD CONSTRAINT `FK_E0C890D6315B405` FOREIGN KEY (`support_id`) REFERENCES `supports` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `FK_E0C890D641DEFADA` FOREIGN KEY (`devis_id`) REFERENCES `devis` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `FK_E0C890D6806A5250` FOREIGN KEY (`produit_configuration_id`) REFERENCES `produit_configuration` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `FK_E0C890D6D357F183` FOREIGN KEY (`type_impression_id`) REFERENCES `types_impression` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `FK_E0C890D6D629F605` FOREIGN KEY (`format_id`) REFERENCES `format` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `FK_E0C890D6F347EFB` FOREIGN KEY (`produit_id`) REFERENCES `produits` (`id`) ON DELETE SET NULL;

--
-- Contraintes pour la table `devis_detail_finition`
--
ALTER TABLE `devis_detail_finition`
  ADD CONSTRAINT `FK_BE70DB30A0C197D7` FOREIGN KEY (`configuration_finition_id`) REFERENCES `produit_configuration_finition` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `FK_BE70DB30A903C9C1` FOREIGN KEY (`devis_detail_id`) REFERENCES `devis_details` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `FK_BE70DB30CB56F5AF` FOREIGN KEY (`finition_id`) REFERENCES `finition` (`id`);

--
-- Contraintes pour la table `factures`
--
ALTER TABLE `factures`
  ADD CONSTRAINT `FK_647590B82EA2E54` FOREIGN KEY (`commande_id`) REFERENCES `commandes` (`id`);

--
-- Contraintes pour la table `finition_types_impression`
--
ALTER TABLE `finition_types_impression`
  ADD CONSTRAINT `FK_4EB60CFE9719B876` FOREIGN KEY (`types_impression_id`) REFERENCES `types_impression` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `FK_4EB60CFECB56F5AF` FOREIGN KEY (`finition_id`) REFERENCES `finition` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `format_types_impression`
--
ALTER TABLE `format_types_impression`
  ADD CONSTRAINT `FK_5CE0BAD89719B876` FOREIGN KEY (`types_impression_id`) REFERENCES `types_impression` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `FK_5CE0BAD8D629F605` FOREIGN KEY (`format_id`) REFERENCES `format` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `maintenance`
--
ALTER TABLE `maintenance`
  ADD CONSTRAINT `FK_2F84F8E9F6B75B26` FOREIGN KEY (`machine_id`) REFERENCES `machines` (`id`);

--
-- Contraintes pour la table `paiements`
--
ALTER TABLE `paiements`
  ADD CONSTRAINT `FK_E1B02E1282EA2E54` FOREIGN KEY (`commande_id`) REFERENCES `commandes` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `FK_E1B02E12A4FBCD6F` FOREIGN KEY (`encaisse_par_id`) REFERENCES `user` (`id`);

--
-- Contraintes pour la table `production`
--
ALTER TABLE `production`
  ADD CONSTRAINT `FK_D3EDB1E023D82BC4` FOREIGN KEY (`commande_details_id`) REFERENCES `commandes_details` (`id`),
  ADD CONSTRAINT `FK_D3EDB1E0F6B75B26` FOREIGN KEY (`machine_id`) REFERENCES `machines` (`id`);

--
-- Contraintes pour la table `produits`
--
ALTER TABLE `produits`
  ADD CONSTRAINT `FK_BE2DDF8C91FDB457` FOREIGN KEY (`categorie_produit_id`) REFERENCES `categorie_produit` (`id`);

--
-- Contraintes pour la table `produits_finition`
--
ALTER TABLE `produits_finition`
  ADD CONSTRAINT `FK_DF5600F4CB56F5AF` FOREIGN KEY (`finition_id`) REFERENCES `finition` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `FK_DF5600F4CD11A2CF` FOREIGN KEY (`produits_id`) REFERENCES `produits` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `produits_format`
--
ALTER TABLE `produits_format`
  ADD CONSTRAINT `FK_4FAB693CCD11A2CF` FOREIGN KEY (`produits_id`) REFERENCES `produits` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `FK_4FAB693CD629F605` FOREIGN KEY (`format_id`) REFERENCES `format` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `produits_supports`
--
ALTER TABLE `produits_supports`
  ADD CONSTRAINT `FK_4204645597185C1E` FOREIGN KEY (`supports_id`) REFERENCES `supports` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `FK_42046455CD11A2CF` FOREIGN KEY (`produits_id`) REFERENCES `produits` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `produits_types_impression`
--
ALTER TABLE `produits_types_impression`
  ADD CONSTRAINT `FK_1ADC26C29719B876` FOREIGN KEY (`types_impression_id`) REFERENCES `types_impression` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `FK_1ADC26C2CD11A2CF` FOREIGN KEY (`produits_id`) REFERENCES `produits` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `produit_configuration`
--
ALTER TABLE `produit_configuration`
  ADD CONSTRAINT `FK_8BBC0309315B405` FOREIGN KEY (`support_id`) REFERENCES `supports` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `FK_8BBC0309D357F183` FOREIGN KEY (`type_impression_id`) REFERENCES `types_impression` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `FK_8BBC0309D629F605` FOREIGN KEY (`format_id`) REFERENCES `format` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `FK_8BBC0309F347EFB` FOREIGN KEY (`produit_id`) REFERENCES `produits` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `produit_configuration_finition`
--
ALTER TABLE `produit_configuration_finition`
  ADD CONSTRAINT `FK_BF2ECD31806A5250` FOREIGN KEY (`produit_configuration_id`) REFERENCES `produit_configuration` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `FK_BF2ECD31CB56F5AF` FOREIGN KEY (`finition_id`) REFERENCES `finition` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `stock_entrees`
--
ALTER TABLE `stock_entrees`
  ADD CONSTRAINT `FK_3D445A027294869C` FOREIGN KEY (`article_id`) REFERENCES `articles` (`id`);

--
-- Contraintes pour la table `stock_sorties`
--
ALTER TABLE `stock_sorties`
  ADD CONSTRAINT `FK_5127734B7294869C` FOREIGN KEY (`article_id`) REFERENCES `articles` (`id`),
  ADD CONSTRAINT `FK_5127734BC8DC59F9` FOREIGN KEY (`commande_detail_id`) REFERENCES `commandes_details` (`id`);

--
-- Contraintes pour la table `support_finition`
--
ALTER TABLE `support_finition`
  ADD CONSTRAINT `FK_94D67319315B405` FOREIGN KEY (`support_id`) REFERENCES `supports` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `FK_94D67319CB56F5AF` FOREIGN KEY (`finition_id`) REFERENCES `finition` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `support_format`
--
ALTER TABLE `support_format`
  ADD CONSTRAINT `FK_5640922F315B405` FOREIGN KEY (`support_id`) REFERENCES `supports` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `FK_5640922FD629F605` FOREIGN KEY (`format_id`) REFERENCES `format` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `support_types_impression`
--
ALTER TABLE `support_types_impression`
  ADD CONSTRAINT `FK_EE1AA144315B405` FOREIGN KEY (`support_id`) REFERENCES `supports` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `FK_EE1AA1449719B876` FOREIGN KEY (`types_impression_id`) REFERENCES `types_impression` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `user`
--
ALTER TABLE `user`
  ADD CONSTRAINT `FK_8D93D6491B65292` FOREIGN KEY (`employe_id`) REFERENCES `employes` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
