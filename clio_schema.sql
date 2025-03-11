/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19-11.4.5-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: clio_db
-- ------------------------------------------------------
-- Server version	11.4.5-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*M!100616 SET @OLD_NOTE_VERBOSITY=@@NOTE_VERBOSITY, NOTE_VERBOSITY=0 */;

--
-- Table structure for table `genus`
--

DROP TABLE IF EXISTS `genus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `genus` (
  `UUID` char(36) NOT NULL,
  `shortname` varchar(50) NOT NULL,
  `longname` varchar(255) NOT NULL,
  `genus_type_id` int(11) NOT NULL,
  PRIMARY KEY (`UUID`),
  UNIQUE KEY `shortname` (`shortname`),
  KEY `genus_type_id` (`genus_type_id`),
  CONSTRAINT `genus_ibfk_1` FOREIGN KEY (`genus_type_id`) REFERENCES `genus_type` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `genus`
--

LOCK TABLES `genus` WRITE;
/*!40000 ALTER TABLE `genus` DISABLE KEYS */;
INSERT INTO `genus` VALUES
('e14c3d50-f62e-11ef-a353-244bfe55f25a','test','dummy testing genus',1);
/*!40000 ALTER TABLE `genus` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `genus_type`
--

DROP TABLE IF EXISTS `genus_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `genus_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `shortname` varchar(50) NOT NULL,
  `longname` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `shortname` (`shortname`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `genus_type`
--

LOCK TABLES `genus_type` WRITE;
/*!40000 ALTER TABLE `genus_type` DISABLE KEYS */;
INSERT INTO `genus_type` VALUES
(1,'default','default genus');
/*!40000 ALTER TABLE `genus_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `keyword`
--

DROP TABLE IF EXISTS `keyword`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `keyword` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `word` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `word` (`word`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `keyword`
--

LOCK TABLES `keyword` WRITE;
/*!40000 ALTER TABLE `keyword` DISABLE KEYS */;
/*!40000 ALTER TABLE `keyword` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `note`
--

DROP TABLE IF EXISTS `note`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `note` (
  `rec_UUID` char(36) NOT NULL,
  `content` text NOT NULL,
  PRIMARY KEY (`rec_UUID`),
  CONSTRAINT `note_ibfk_1` FOREIGN KEY (`rec_UUID`) REFERENCES `record` (`UUID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `note`
--

LOCK TABLES `note` WRITE;
/*!40000 ALTER TABLE `note` DISABLE KEYS */;
INSERT INTO `note` VALUES
('30fe5bdb-f632-11ef-a353-244bfe55f25a','This is the first test note under the test topic.'),
('30fe5e41-f632-11ef-a353-244bfe55f25a','This is the second test note under the test topic.');
/*!40000 ALTER TABLE `note` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `record`
--

DROP TABLE IF EXISTS `record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `record` (
  `UUID` char(36) NOT NULL,
  `genus_UUID` char(36) NOT NULL,
  `parent_UUID` char(36) DEFAULT NULL,
  `rectype_id` int(11) NOT NULL,
  `create_date` datetime DEFAULT current_timestamp(),
  `modify_date` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `shortname` varchar(255) DEFAULT NULL,
  `longname` varchar(255) DEFAULT NULL,
  `summary` text DEFAULT NULL,
  PRIMARY KEY (`UUID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `record`
--

LOCK TABLES `record` WRITE;
/*!40000 ALTER TABLE `record` DISABLE KEYS */;
INSERT INTO `record` VALUES
('30fe5bdb-f632-11ef-a353-244bfe55f25a','e14c3d50-f62e-11ef-a353-244bfe55f25a','e9e3f3a4-f630-11ef-a353-244bfe55f25a',2,'2025-03-01 01:14:50','2025-03-01 01:14:50',NULL,NULL,NULL),
('30fe5e41-f632-11ef-a353-244bfe55f25a','e14c3d50-f62e-11ef-a353-244bfe55f25a','e9e3f3a4-f630-11ef-a353-244bfe55f25a',2,'2025-03-01 01:14:50','2025-03-01 01:14:50',NULL,NULL,NULL),
('e9e3f3a4-f630-11ef-a353-244bfe55f25a','e14c3d50-f62e-11ef-a353-244bfe55f25a','e14c3d50-f62e-11ef-a353-244bfe55f25a',1,'2025-03-01 01:05:41','2025-03-01 01:05:41',NULL,NULL,NULL);
/*!40000 ALTER TABLE `record` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `record_keyword`
--

DROP TABLE IF EXISTS `record_keyword`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `record_keyword` (
  `record_UUID` char(36) NOT NULL,
  `keyword_id` int(11) NOT NULL,
  PRIMARY KEY (`record_UUID`,`keyword_id`),
  KEY `keyword_id` (`keyword_id`),
  CONSTRAINT `record_keyword_ibfk_1` FOREIGN KEY (`record_UUID`) REFERENCES `record` (`UUID`) ON DELETE CASCADE,
  CONSTRAINT `record_keyword_ibfk_2` FOREIGN KEY (`keyword_id`) REFERENCES `keyword` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `record_keyword`
--

LOCK TABLES `record_keyword` WRITE;
/*!40000 ALTER TABLE `record_keyword` DISABLE KEYS */;
/*!40000 ALTER TABLE `record_keyword` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rectype`
--

DROP TABLE IF EXISTS `rectype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `rectype` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rectype`
--

LOCK TABLES `rectype` WRITE;
/*!40000 ALTER TABLE `rectype` DISABLE KEYS */;
INSERT INTO `rectype` VALUES
(2,'note'),
(1,'topic');
/*!40000 ALTER TABLE `rectype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `topic`
--

DROP TABLE IF EXISTS `topic`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `topic` (
  `rec_UUID` char(36) NOT NULL,
  `shortname` varchar(255) NOT NULL,
  `longname` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  PRIMARY KEY (`rec_UUID`),
  CONSTRAINT `topic_ibfk_1` FOREIGN KEY (`rec_UUID`) REFERENCES `record` (`UUID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `topic`
--

LOCK TABLES `topic` WRITE;
/*!40000 ALTER TABLE `topic` DISABLE KEYS */;
INSERT INTO `topic` VALUES
('e9e3f3a4-f630-11ef-a353-244bfe55f25a','test_topic','Test Topic','This is a test topic for hierarchical structuring.');
/*!40000 ALTER TABLE `topic` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2025-03-01  1:57:58
