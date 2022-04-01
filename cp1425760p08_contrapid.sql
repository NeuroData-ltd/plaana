-- phpMyAdmin SQL Dump
-- version 4.9.7
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Apr 01, 2022 at 02:19 PM
-- Server version: 10.3.34-MariaDB-cll-lve
-- PHP Version: 7.3.33

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `cp1425760p08_contrapid`
--

-- --------------------------------------------------------

--
-- Table structure for table `agents`
--

CREATE TABLE `agents` (
  `username` text DEFAULT NULL,
  `password` text DEFAULT NULL,
  `matricule` varchar(15) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `agents`
--

INSERT INTO `agents` (`username`, `password`, `matricule`) VALUES
('kabore', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', ''),
('rodrigue', '123456', '0051772997'),
('rodrigue', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '0051772997'),
('kabore', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'B1310'),
('y', '11b7cb7706d36816b77ebc6bb660fb611bfa6d16358ddd8aa309362b956ad721', '');

-- --------------------------------------------------------

--
-- Table structure for table `assurance`
--

CREATE TABLE `assurance` (
  `id` int(100) NOT NULL,
  `assureur` varchar(100) NOT NULL,
  `immatriculation` varchar(50) DEFAULT NULL,
  `date_assurance` date NOT NULL,
  `date_expiration` int(11) NOT NULL,
  `type_assurance` varchar(100) NOT NULL,
  `type_vehicule` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `assurance`
--

INSERT INTO `assurance` (`id`, `assureur`, `immatriculation`, `date_assurance`, `date_expiration`, `type_assurance`, `type_vehicule`) VALUES
(1, 'ALLIANZ', NULL, '2022-05-03', 2026, 'Mobile', ''),
(2, 'ALLIANZ', '9563D403', '2022-05-03', 2026, 'Tout Risque', 'VOITURE');

-- --------------------------------------------------------

--
-- Table structure for table `carte_grise`
--

CREATE TABLE `carte_grise` (
  `id` int(100) NOT NULL,
  `immatriculation` varchar(100) NOT NULL,
  `numero_ordre` int(10) NOT NULL,
  `code_securite` varchar(5) DEFAULT NULL,
  `code_alpha` varchar(5) NOT NULL,
  `code_region` varchar(5) NOT NULL,
  `nom` varchar(100) NOT NULL,
  `prenom` varchar(100) NOT NULL,
  `profession` varchar(100) NOT NULL,
  `ville` varchar(100) NOT NULL,
  `province` varchar(100) NOT NULL,
  `adresse` varchar(100) NOT NULL,
  `genre` varchar(100) NOT NULL,
  `marque` varchar(100) NOT NULL,
  `numero_serie` varchar(100) NOT NULL,
  `carrosserie` varchar(100) NOT NULL,
  `type` varchar(100) NOT NULL,
  `modele` varchar(100) NOT NULL,
  `energie` varchar(100) NOT NULL,
  `puissance_administrative` varchar(100) NOT NULL,
  `charge_utile` varchar(100) NOT NULL,
  `ptac` varchar(50) DEFAULT NULL,
  `ptra` varchar(50) DEFAULT NULL,
  `capacite` varchar(100) DEFAULT NULL,
  `nombre_places` int(5) NOT NULL,
  `date_mise_circulation` date DEFAULT NULL,
  `date_carte_precedente` date DEFAULT NULL,
  `immatriculation_precedente` varchar(100) DEFAULT NULL,
  `declaration_perte` tinyint(1) DEFAULT NULL,
  `date_creation` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `carte_grise`
--

INSERT INTO `carte_grise` (`id`, `immatriculation`, `numero_ordre`, `code_securite`, `code_alpha`, `code_region`, `nom`, `prenom`, `profession`, `ville`, `province`, `adresse`, `genre`, `marque`, `numero_serie`, `carrosserie`, `type`, `modele`, `energie`, `puissance_administrative`, `charge_utile`, `ptac`, `ptra`, `capacite`, `nombre_places`, `date_mise_circulation`, `date_carte_precedente`, `immatriculation_precedente`, `declaration_perte`, `date_creation`) VALUES
(1, '46166F03', 4616, '00', '6F', '03', 'OUEDRAOGO', 'MARTIAL', 'ETUDIANT', 'OUAGADOUGOU', 'KADIOGO', 'SECTEUR 1', 'MOTOCYCLE', 'YAMAHA', 'RLCS5C6H0GY24120', 'MOTO SOLO', '110', 'SCOOTER', 'ESSENCE', '01', '180', '245', NULL, NULL, 2, '2020-01-30', NULL, NULL, NULL, '0000-00-00'),
(3, '9563D403', 9588, '00', 'CT', '11', 'KABORE', 'SEGNOGO NOUROUDINE', 'ETUDIANT', 'OUAGADOUGOU', 'KADIOGO', 'SECTEUR 19', '4 ROUES', 'TOYOTA', 'RLCS5C6H0GY248501', 'MOTO SOLO', '110', 'YARIS', 'ESSENCE', '01', '160', '235', 'None', 'None', 2, '2017-08-31', '0000-00-00', 'None', 0, '0000-00-00');

-- --------------------------------------------------------

--
-- Table structure for table `infractions`
--

CREATE TABLE `infractions` (
  `id` int(100) NOT NULL,
  `code_infraction` varchar(50) NOT NULL,
  `immatriculation` varchar(50) NOT NULL,
  `phone` varchar(50) NOT NULL,
  `nom_fautif` varchar(50) NOT NULL,
  `prenom_fautif` varchar(50) NOT NULL,
  `nature_infraction` varchar(200) NOT NULL,
  `lieu_infraction` varchar(100) NOT NULL,
  `date_infraction` date NOT NULL,
  `lieu_recuperation` varchar(100) NOT NULL,
  `nom_agent` varchar(50) NOT NULL,
  `prenom_agent` varchar(50) DEFAULT NULL,
  `statut` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `infractions`
--

INSERT INTO `infractions` (`id`, `code_infraction`, `immatriculation`, `phone`, `nom_fautif`, `prenom_fautif`, `nature_infraction`, `lieu_infraction`, `date_infraction`, `lieu_recuperation`, `nom_agent`, `prenom_agent`, `statut`) VALUES
(1, 'I5564', '52883R03', '72647387', 'BILA', 'EDMOND', 'faux tricolores', 'PROJET ZAKA', '2022-03-17', 'COMMISARIAT CENTRAL', 'ZAGRE', 'GEORGE', 1),
(2, '10022', '52883R03', '72647387', 'BILA', 'ALBERT', 'pas de documents', 'RN1', '2022-02-17', 'TAMPOUY', 'ZERBO', 'MOUSSA', 0),
(3, '10022', '52883R03', '72647387', 'BADINI', 'CREPIN', 'incivisme', 'RN6', '2022-03-15', 'ZONE 1', 'ZERBO', 'MOUSSA', 0),
(4, '100233', '52883R03', '72647387', 'BADINI', 'VALLER', 'incivisme severe', 'RN6', '2022-03-15', 'ZONE 2', 'ZERBO', 'MOUSSA', 0),
(18, '10055', '52883R06', '72647387', 'BAD', 'VALLER', 'incivisme severe', 'RN6', '2022-03-15', 'ZONE 2', 'ZERBO', 'MOUSSA', 0),
(19, '7581', '52883R06', '72647387', 'BOLI', 'Amed', 'faux papiers', 'Tanguy', '2022-03-22', 'Tanguy', 'ZERBO', 'MOUSSA', 0),
(20, '6395', '52883R06', '72647387', 'BOLI', 'Amed', 'faux papiers', 'Tanga', '2022-03-22', 'Tanguy', 'ZERBO', 'MOUSSA', 0),
(0, '5071', '52883R06', '72647387', 'BOLI', 'Amed', 'faux papiers', 'Tanga', '2022-03-22', 'Tanguy', 'ZERBO', 'MOUSSA', 0),
(0, '6881', '52883R88', '72647387', 'BOLI', 'Noure', 'faux documents', 'Tanga', '2022-03-22', 'Karpala', 'ZERBO', 'MOUSSA', 0),
(0, '1251', '52883R98', '72647387', 'BOLI', 'Nourdine', 'faux documents', 'Tanga', '2022-03-22', 'Karpala', 'ZERBO', 'MOUSSA', 0),
(0, '4086', '52883R98', '72647387', 'BOLI', 'Nourdine', 'faux documents', 'Tanga', '2022-03-22', 'Karpala', 'ZERBO', 'MOUSSA', 0),
(0, '6466', '52883R98', '72647387', 'BOLI', 'Nourdine', 'faux documents', 'Tanga', '2022-03-22', 'Karpala', 'ZERBO', 'MOUSSA', 0),
(0, '1817', '52883R98', '+21620143356', 'BOLI', 'Nourdine', 'faux documents', 'Tanga', '2022-03-22', 'Karpala', 'ZERBO', 'MOUSSA', 0),
(0, '3054', '52883R98', '0021620143356', 'BOLI', 'Nourdine', 'faux documents', 'Tanga', '2022-03-22', 'Karpala', 'ZERBO', 'MOUSSA', 0),
(0, '1251', '52883R98', '20143356', 'BOLI', 'Nourdine', 'faux documents', 'Tanga', '2022-03-22', 'Karpala', 'ZERBO', 'MOUSSA', 0),
(0, '7587', '52883R98', '20143356', 'BOLI', 'Nourdine', 'faux documents', 'Tanga', '2022-03-22', 'Karpala', 'ZERBO', 'MOUSSA', 0),
(0, '7726', '52883R98', '20143356', 'BOLI', 'Nourdine', 'faux documents', 'Tanga', '2022-03-22', 'Karpala', 'ZERBO', 'MOUSSA', 0),
(0, '6257', '52883R98', '72647387', 'WebAPP', 'APPaaaa', 'faux documents', 'Tanga', '2022-03-22', 'Karpala', 'ZERBO', 'MOUSSA', 0),
(0, '6466', 'hello', 'sendmelove', 'imyassine', 'sendmepeace', 'sendmelove', 'sendmelove', '2022-03-24', 'sendmelove', 'sendmelove', 'sendmelove', 0),
(0, '5904', 'hello', 'sendmelove', 'imyassine', 'sendmepeace', 'sendmelove', 'sendmelove', '2022-03-24', 'sendmelove', 'sendmelove', 'sendmelove', 0),
(0, '4674', 'hello', '72647387', 'imyassine', 'sendmepeace', 'sendmelove', 'sendmelove', '2022-03-24', 'sendmelove', 'sendmelove', 'sendmelove', 0),
(0, '1986', 'hello', 'klk,mmlj', 'jjjjjj', 'hhjjj', 'qsfqsf', 'qsfqsfqsf', '2022-03-24', 'qsfqsf', 'qsfqsf', 'qsfqsf', 0),
(0, '9291', 'hello', 'qsfqsf', 'qsdqsd', 'qsfdqsf', 'qsfsf', 'qsfqsfqsf', '2022-03-24', 'qsfqsf', 'qsfqsf', 'qsfqsfqsf', 0),
(0, '2859', 'hello', 'QSFQSFQSF', 'QSDFQSF', 'QSFQSF', 'QSFQSFQSF', 'QSFQSF', '2022-03-24', 'QFQFFFFF', 'FFF', 'dddd', 0),
(0, '7781', 'hello', 'QSFQSFQSF', 'QSDFQSF', 'QSFQSF', 'QSFQSFQSF', 'QSFQSF', '2022-03-24', 'QFQFFFFF', 'FFF', 'dddd', 0),
(0, '5586', '9563D403', '72647387', 'byweb', 'byweb', 'documentation', 'tunisia', '2022-03-24', 'tunis', 'kabore', 'Noureddine', 0),
(0, '8221', '46166F03', '72647387', 'KABORE', 'Nouroudine', 'Feux arriÃ¨re', 'Karpala', '2022-03-24', 'Secteur 2', 'KABORE', 'Nouroudine', 0),
(0, '6647', '46166F03', '77731507', 'KABORE', 'Nouroudine', 'Feux', 'Karpala', '2022-03-25', 'Karpala', 'KABORE', 'Nouroudine', 0),
(0, '6497', '46166F03', '72647387', 'KABORE', 'Nouroudine', 'Feux', 'Karpala', '2022-03-25', 'Karpala', 'KABORE', 'Nouroudine', 0),
(0, '2246', '46166F03', '57651764', 'KABORE', 'Nouroudine', 'Faux documents', 'Karpala', '2022-03-25', 'Karpala', 'KABORE', 'Nouroudine', 0),
(0, '4358', '9563D403', '57651764', 'ILBOUDO', 'KADER', 'rien', 'somgande', '2022-03-27', 'somgande', 'NANA', 'Boureima', 0),
(0, '7113', '9563D403', '57651764', 'ILBOUDO', 'KADER', 'rien', 'somgande', '2022-03-27', 'somgande', 'NANA', 'Boureima', 0),
(0, '2832', '52883R98', '57651764', 'BOLI', 'Nourdine', 'faux documents', 'Tanga', '2022-03-22', 'Karpala', 'ZERBO', NULL, 0),
(0, '7839', '9563D403', '57651764', 'KABORE', 'Nouroudine', 'faux documents', 'karpala', '2022-03-28', 'Tampouy', 'B1111', NULL, 0),
(0, '2942', '52883R98', '57651764', 'KQBORE', 'Nourdine', 'faux documents', 'Tanga', '2022-03-22', 'Karpala', 'ZERBO', NULL, 0),
(0, '4295', '9563D403', '57651764', 'KABORE22', 'Nouroudine', 'faux documents', 'karpala', '2022-03-28', 'Tampouy', 'B1111', NULL, 0);

-- --------------------------------------------------------

--
-- Table structure for table `permis_de_conduire`
--

CREATE TABLE `permis_de_conduire` (
  `id` int(100) NOT NULL,
  `nom` varchar(50) NOT NULL,
  `prenom` varchar(50) NOT NULL,
  `date_naissance` date NOT NULL,
  `lieu_naissannce` varchar(50) NOT NULL,
  `domicile` varchar(50) NOT NULL,
  `numero_permis` varchar(10) NOT NULL,
  `date_delivrance` date NOT NULL,
  `lieu_delivrance` varchar(50) NOT NULL,
  `permis_a1` tinyint(1) NOT NULL,
  `permis_a` tinyint(1) DEFAULT NULL,
  `permis_b` tinyint(1) NOT NULL,
  `permis_c` tinyint(1) DEFAULT NULL,
  `permis_d` tinyint(1) DEFAULT NULL,
  `permis_e` tinyint(1) DEFAULT NULL,
  `permis_f` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `userstable`
--

CREATE TABLE `userstable` (
  `username` text DEFAULT NULL,
  `password` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `userstable`
--

INSERT INTO `userstable` (`username`, `password`) VALUES
('kabore', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92');

-- --------------------------------------------------------

--
-- Table structure for table `visite_technique`
--

CREATE TABLE `visite_technique` (
  `id` int(100) NOT NULL,
  `immatriculation` varchar(50) DEFAULT NULL,
  `date_visite` date NOT NULL,
  `date_expiration` date NOT NULL,
  `type_vehicule` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `visite_technique`
--

INSERT INTO `visite_technique` (`id`, `immatriculation`, `date_visite`, `date_expiration`, `type_vehicule`) VALUES
(2, '9563', '2022-08-20', '2026-05-02', 'VOITURE'),
(3, '9563D403', '2022-08-20', '2026-05-02', 'VOITURE');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `assurance`
--
ALTER TABLE `assurance`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `carte_grise`
--
ALTER TABLE `carte_grise`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `permis_de_conduire`
--
ALTER TABLE `permis_de_conduire`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `visite_technique`
--
ALTER TABLE `visite_technique`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `assurance`
--
ALTER TABLE `assurance`
  MODIFY `id` int(100) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `carte_grise`
--
ALTER TABLE `carte_grise`
  MODIFY `id` int(100) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `permis_de_conduire`
--
ALTER TABLE `permis_de_conduire`
  MODIFY `id` int(100) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `visite_technique`
--
ALTER TABLE `visite_technique`
  MODIFY `id` int(100) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
