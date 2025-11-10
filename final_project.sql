-- -------------------------------------------------------
-- WILDLIFE CONSERVATION MANAGEMENT SYSTEM
-- Master SQL Setup Script (DDL, DML, Procedures, Functions, Triggers)
-- -------------------------------------------------------

-- DATABASE SETUP
CREATE DATABASE IF NOT EXISTS wildlife_conservation;
USE wildlife_conservation;

-- -------------------------------------------------------
-- 1. DDL (CREATE TABLE STATEMENTS)

-- Species Table
CREATE TABLE Species (
    Sp_ID INT PRIMARY KEY AUTO_INCREMENT,
    common_name VARCHAR(100),
    Scientific_name VARCHAR(150),
    conservation_status VARCHAR(50),
    Avg_lifespan INT
);

-- Alternative Names (multi-valued attribute for Species)
CREATE TABLE Alt_Names (
    Sp_ID INT,
    Alt_Name VARCHAR(100),
    PRIMARY KEY (Sp_ID, Alt_Name),
    FOREIGN KEY (Sp_ID) REFERENCES Species(Sp_ID) ON DELETE CASCADE
);

-- Habitat Table
CREATE TABLE Habitat (
    Habitat_ID INT PRIMARY KEY AUTO_INCREMENT,
    habitat_type VARCHAR(100),
    climate VARCHAR(100),
    region VARCHAR(100),
    area_size DECIMAL(10,2)
);

-- Inhabits (M:N relation b/w species & habitats)
CREATE TABLE Inhabits (
    Sp_ID INT,
    Habitat_ID INT,
    PRIMARY KEY (Sp_ID, Habitat_ID),
    FOREIGN KEY (Sp_ID) REFERENCES Species(Sp_ID) ON DELETE CASCADE,
    FOREIGN KEY (Habitat_ID) REFERENCES Habitat(Habitat_ID) ON DELETE CASCADE
);

-- Ranger Table (Super_Ranger_ID implements self-referential relationship)
CREATE TABLE Ranger (
    Ranger_ID INT PRIMARY KEY AUTO_INCREMENT,
    fname VARCHAR(100),
    raankOfRanger VARCHAR(50),
    date_joined DATE,
    Phone VARCHAR(20),
    email VARCHAR(100),
    Super_Ranger_ID INT,
    FOREIGN KEY (Super_Ranger_ID) REFERENCES Ranger(Ranger_ID) ON DELETE SET NULL
);

-- Assigned_To (M:N relationship b/w habitat & ranger)
CREATE TABLE Assigned_To (
    Ranger_ID INT,
    Habitat_ID INT,
    Assigned_Date DATE,
    PRIMARY KEY (Ranger_ID, Habitat_ID),
    FOREIGN KEY (Ranger_ID) REFERENCES Ranger(Ranger_ID) ON DELETE CASCADE,
    FOREIGN KEY (Habitat_ID) REFERENCES Habitat(Habitat_ID) ON DELETE CASCADE
);

-- Animal Table (Composite Primary Key)
CREATE TABLE Animal (
    Animal_ID INT,
    Sp_ID INT,
    Tracking_ID VARCHAR(20),
    DOB DATE,
    Gender VARCHAR(10),
    Health_status VARCHAR(50),
    PRIMARY KEY (Animal_ID, Sp_ID),
    FOREIGN KEY (Sp_ID) REFERENCES Species(Sp_ID)

);

-- Threat Report Table
CREATE TABLE Threat_Report (
    Report_ID INT PRIMARY KEY AUTO_INCREMENT,
    Habitat_ID INT,
    Ranger_ID INT,
    Report_Date DATE,
    Threat_Level VARCHAR(20),
    Description TEXT,
    FOREIGN KEY (Habitat_ID) REFERENCES Habitat(Habitat_ID) ON DELETE CASCADE,
    FOREIGN KEY (Ranger_ID) REFERENCES Ranger(Ranger_ID) ON DELETE CASCADE
);


-- Organization Table
CREATE TABLE Organization (
    Org_ID INT PRIMARY KEY AUTO_INCREMENT,
    fi_name VARCHAR(100),
    typeOrg VARCHAR(50),
    phone VARCHAR(20),
    email VARCHAR(100),
    contact VARCHAR(100)
);

-- Equipment Table
CREATE TABLE Equipment (
    Equipment_ID INT PRIMARY KEY AUTO_INCREMENT,
    StatusEqui VARCHAR(50), -- Updated by Triggers
    purchase_date DATE,
    equip_type VARCHAR(100),
    Org_ID INT,
    FOREIGN KEY (Org_ID) REFERENCES Organization(Org_ID) ON DELETE RESTRICT
);

-- Uses Table (M:N Ranger ↔ Equipment)
CREATE TABLE Uses (
    Ranger_ID INT,
    Equipment_ID INT,
    Date_Issued DATE,
    PRIMARY KEY (Ranger_ID, Equipment_ID),
    FOREIGN KEY (Ranger_ID) REFERENCES Ranger(Ranger_ID) ON DELETE CASCADE,
    FOREIGN KEY (Equipment_ID) REFERENCES Equipment(Equipment_ID) ON DELETE CASCADE
);

-- Sighting Table
CREATE TABLE Sighting (
    Sighting_ID INT PRIMARY KEY AUTO_INCREMENT,
    Ranger_ID INT,
    Sighting_Date DATE,
    Sighting_Time TIME,
    Location VARCHAR(100),
    FOREIGN KEY (Ranger_ID) REFERENCES Ranger(Ranger_ID) ON DELETE CASCADE
);

-- Sighting_Details (Linking Table between Sighting, Animal, and Ranger)
CREATE TABLE Sighting_Details (
    sighting_ID INT,
    Animal_ID INT,
    Ranger_ID INT,
    PRIMARY KEY (sighting_ID, Animal_ID, Ranger_ID),
    FOREIGN KEY (sighting_ID) REFERENCES Sighting(Sighting_ID) ON DELETE CASCADE,
    FOREIGN KEY (Animal_ID) REFERENCES Animal(Animal_ID), -- References Animal_ID part of composite key
    FOREIGN KEY (Ranger_ID) REFERENCES Ranger(Ranger_ID) ON DELETE CASCADE
);

-- -------------------------------------------------------
-- 2. DML (INSERT STATEMENTS)
-- -------------------------------------------------------

-- Species
INSERT INTO Species (common_name, Scientific_name, conservation_status, Avg_lifespan)
VALUES
('Asian Elephant', 'Elephas maximus indicus', 'Endangered', 65),
('Indian Leopard', 'Panthera pardus fusca', 'Vulnerable', 15),
('Lion-tailed Macaque', 'Macaca silenus', 'Endangered', 20),
('Sloth Bear', 'Melursus ursinus', 'Vulnerable', 20),
('Malabar Civet', 'Viverra civettina', 'Critically Endangered', 12),
('Nilgiri Tahr', 'Nilgiritragus hylocrius', 'Endangered', 14),
('King Cobra', 'Ophiophagus hannah', 'Vulnerable', 18),
('Great Hornbill', 'Buceros bicornis', 'Vulnerable', 35),
('Indian Pangolin', 'Manis crassicaudata', 'Endangered', 13),
('Smooth-coated Otter', 'Lutrogale perspicillata', 'Vulnerable', 12);

-- Alternative Names
INSERT INTO Alt_Names (Alt_Name, Sp_ID)
VALUES
('Indian Elephant', 1),
('Panther', 2),
('Wanderoo', 3),
('Bearcat', 4),
('Malabar Civet Cat', 5),
('Ibex of Nilgiris', 6),
('Hamap Cobra', 7),
('Forest Hornbill', 8),
('Scaly Anteater', 9),
('River Otter', 10);

-- Habitats
INSERT INTO Habitat (habitat_type, climate, region, area_size)
VALUES
('Moist Deciduous Forest', 'Tropical', 'Bandipur, Karnataka', 874.00),
('Dry Deciduous Forest', 'Tropical', 'Nagarhole, Karnataka', 643.00),
('Evergreen Forest', 'Humid', 'Silent Valley, Kerala', 236.74),
('Shola Grasslands', 'Cool', 'Nilgiris, Tamil Nadu', 160.00),
('Tiger Reserve', 'Tropical', 'Periyar, Kerala', 925.00),
('Mangroves', 'Humid', 'Coringa, Andhra Pradesh', 235.70),
('Wildlife Sanctuary', 'Humid', 'Wayanad, Kerala', 344.44),
('Dry Forest', 'Tropical', 'Sathyamangalam, Tamil Nadu', 1410.00),
('Hill Forest', 'Cool', 'Papikonda, Andhra Pradesh', 1000.00),
('River Basin', 'Tropical', 'Nagarjuna Sagar, Telangana', 356.00);

-- Rangers
INSERT INTO Ranger (fname, raankOfRanger, date_joined, Phone, email)
VALUES
('Ravi Kumar', 'Senior Ranger', '2010-05-22', '9876501234', 'ravi.kumar@forest.gov.in'),
('Anitha Ramesh', 'Field Ranger', '2015-11-15', '9845123456', 'anitha.r@forest.gov.in'),
('Suresh Gopi', 'Wildlife Officer', '2012-06-10', '9898765432', 'suresh.g@forest.gov.in'),
('Lakshmi Priya', 'Junior Ranger', '2018-03-25', '9911223344', 'lakshmi.p@forest.gov.in'),
('Venkatesh Iyer', 'Senior Ranger', '2008-09-12', '9922334455', 'venkatesh.i@forest.gov.in'),
('Divya Menon', 'Field Ranger', '2017-07-18', '9933445566', 'divya.m@forest.gov.in'),
('Manoj Shetty', 'Junior Ranger', '2020-08-09', '9944556677', 'manoj.s@forest.gov.in'),
('Priya Nair', 'Wildlife Officer', '2016-02-11', '9955667788', 'priya.n@forest.gov.in'),
('Arun Karthik', 'Field Ranger', '2019-10-20', '9966778899', 'arun.k@forest.gov.in'),
('Meena Krishnan', 'Junior Ranger', '2021-04-05', '9977889900', 'meena.k@forest.gov.in');

-- Animals
INSERT INTO Animal (Animal_ID, Sp_ID, Tracking_ID, DOB, Gender, Health_status)
VALUES
(1, 1, 'ELE001', '2009-08-12', 'Female', 'Healthy'),
(2, 2, 'LEO002', '2015-02-18', 'Male', 'Injured'),
(3, 3, 'MAC003', '2017-04-05', 'Female', 'Healthy'),
(4, 4, 'SBE004', '2014-11-20', 'Male', 'Healthy'),
(5, 5, 'CIV005', '2010-06-15', 'Female', 'Sick'),
(6, 6, 'TAH006', '2018-12-01', 'Male', 'Healthy'),
(7, 7, 'COB007', '2016-09-25', 'Female', 'Healthy'),
(8, 8, 'HOR008', '2013-03-14', 'Male', 'Injured'),
(9, 9, 'PAN009', '2019-01-09', 'Female', 'Healthy'),
(10, 10, 'OTT010', '2020-05-22', 'Male', 'Healthy'),
(11, 1, 'ELE011', '2011-07-07', 'Female', 'Healthy'),
(12, 2, 'LEO012', '2016-10-30', 'Male', 'Sick'),
(13, 3, 'MAC013', '2018-08-18', 'Female', 'Healthy'),
(14, 6, 'TAH014', '2017-05-05', 'Male', 'Healthy'),
(15, 7, 'COB015', '2019-11-23', 'Female', 'Injured');


-- Organizations
INSERT INTO Organization (fi_name, typeOrg, phone, email, contact) VALUES
('Wildlife Trust India', 'NGO', '08012345678', 'contact@wti.org', 'Ramesh Sharma'),
('Forest Department Kerala', 'Government', '04712345678', 'info@keralaforest.gov.in', 'Anil Kumar'),
('WWF India', 'NGO', '01123456789', 'india@wwf.org', 'Priya Singh'),
('Save the Elephants', 'NGO', '08023456789', 'info@ste.org', 'Sunita Rao'),
('Green Peace India', 'NGO', '01134567890', 'india@greenpeace.org', 'Rahul Verma'),
('Tamil Nadu Forest Dept', 'Government', '04412345678', 'contact@tnforest.gov.in', 'Karthik R'),
('Kerala Wildlife Org', 'NGO', '04812345678', 'contact@kwo.org', 'Deepa Menon'),
('Andhra Pradesh Wildlife', 'Government', '08612345678', 'apwildlife@ap.gov.in', 'Vikram Singh'),
('Biodiversity Conservation India', 'NGO', '01156789012', 'bci@ngo.org', 'Meera Iyer'),
('National Wildlife Federation', 'NGO', '02212345678', 'nwf@ngo.org', 'Suresh Rao');

-- Equipment
INSERT INTO Equipment (StatusEqui, purchase_date, equip_type, Org_ID) VALUES
('Available', '2018-01-15', 'Binocular', 1),
('In Use', '2019-03-22', 'GPS Tracker', 2),
('Maintenance', '2020-07-10', 'Camera Trap', 1),
('Available', '2021-05-05', 'Vehicle', 3),
('In Use', '2017-11-11', 'First Aid Kit', 2),
('Available', '2019-09-01', 'Radio', 4),
('In Use', '2020-02-15', 'Drone', 5),
('Maintenance', '2018-12-20', 'Night Vision Scope', 6),
('Available', '2021-03-30', 'Protective Gear', 7),
('In Use', '2022-01-12', 'Tracking Collar', 8);

-- Inhabits (Species ↔ Habitat)
INSERT INTO Inhabits (Sp_ID, Habitat_ID) VALUES
(1, 1), (1, 2), (1, 5),
(2, 2), (2, 8), (3, 3), (3, 4), 
(4, 4), (4, 8), (5, 5), (6, 4), 
(6, 9), (7, 6), (7, 10), (8, 7),
(9, 8), (10, 9), (10, 1);

-- Assigned_To (Rangers ↔ Habitats)
INSERT INTO Assigned_To (Ranger_ID, Habitat_ID, Assigned_Date) VALUES
(1, 1, '2010-06-01'), (1, 5, '2011-01-15'),
(2, 2, '2015-12-01'), (2, 8, '2016-03-10'),
(3, 3, '2012-07-01'), (3, 4, '2013-05-12'),
(4, 4, '2018-04-01'), (4, 9, '2019-06-15'),
(5, 5, '2008-10-01'), (5, 10, '2009-08-20'),
(6, 6, '2017-08-01'), (7, 7, '2020-09-01'),
(8, 8, '2016-03-01'), (9, 9, '2019-11-01'), 
(10, 10, '2021-05-01');

-- Uses (Ranger ↔ Equipment)
INSERT INTO Uses (Ranger_ID, Equipment_ID, Date_Issued) VALUES
(1, 1, '2018-02-01'), (2, 2, '2019-04-01'), (3, 3, '2020-08-01'),
(4, 4, '2021-06-01'), (5, 5, '2017-12-01'), (6, 6, '2019-10-01'),
(7, 7, '2020-03-01'), (8, 8, '2019-01-01'), (9, 9, '2021-04-01'),
(10, 10, '2022-02-01');

-- Sighting
INSERT INTO Sighting (Ranger_ID, Sighting_Date, Sighting_Time, Location) VALUES
(1, '2023-07-12', '08:30:00', 'Bandipur Core Zone'),
(2, '2023-07-13', '10:15:00', 'Nagarhole Waterhole'),
(3, '2023-07-14', '14:45:00', 'Silent Valley Trail'),
(4, '2023-07-15', '09:00:00', 'Nilgiris Plateau'),
(5, '2023-07-16', '16:30:00', 'Periyar Tiger Reserve'),
(6, '2023-07-17', '07:45:00', 'Coringa Mangroves'),
(7, '2023-07-18', '11:20:00', 'Wayanad Sanctuary'),
(8, '2023-07-19', '13:55:00', 'Sathyamangalam Dry Forest'),
(9, '2023-07-20', '15:10:00', 'Papikonda Hills'),
(10, '2023-07-21', '09:40:00', 'Nagarjuna River Basin');

-- Sighting_Details (Sighting ↔ Animal ↔ Ranger)
INSERT INTO Sighting_Details (sighting_ID, Animal_ID, Ranger_ID) VALUES
(1, 1, 1), (2, 2, 2), (3, 3, 3), (4, 6, 4), (5, 7, 5),
(6, 8, 6), (7, 9, 7), (8, 10, 8), (9, 11, 9), (10, 1, 10); -- NOTE: Changed (10, 12, 10) to (10, 1, 10) to use existing sample Animal_ID

-- Threat_Report
INSERT INTO Threat_Report (Habitat_ID, Ranger_ID, Report_Date, Threat_Level, Description) VALUES
(1, 1, '2023-07-12', 'High', 'Illegal poaching detected near core zone'),
(2, 2, '2023-07-13', 'Medium', 'Signs of forest fire spotted near waterhole'),
(3, 3, '2023-07-14', 'Low', 'Minor habitat disturbance observed'),
(4, 4, '2023-07-15', 'High', 'Tree felling reported in Shola grasslands'),
(5, 5, '2023-07-16', 'Medium', 'Human intrusion near tiger reserve'),
(6, 6, '2023-07-17', 'High', 'Mangrove encroachment by locals'),
(7, 7, '2023-07-18', 'Medium', 'Illegal fishing reported'),
(8, 8, '2023-07-19', 'Low', 'Forest trail blockage observed'),
(9, 9, '2023-07-20', 'High', 'Hunting trap found in hill forest'),
(10, 10, '2023-07-21', 'Medium', 'Pollution in river basin');

-- -------------------------------------------------------
-- 3. STORED PROCEDURES
-- -------------------------------------------------------
DELIMITER //

-- Procedure 1: Updates the Health Status of an Animal by Tracking ID
CREATE PROCEDURE UpdateAnimalHealth(
    IN p_Tracking_ID VARCHAR(20),
    IN p_New_Status VARCHAR(50)
)
BEGIN
    UPDATE Animal
    SET Health_status = p_New_Status
    WHERE Tracking_ID = p_Tracking_ID;
END //

-- Procedure 2: Logs a new Threat Report using CURDATE() for the report date
CREATE PROCEDURE LogThreatReport(
    IN p_Habitat_ID INT,
    IN p_Ranger_ID INT,
    IN p_Threat_Level VARCHAR(20),
    IN p_Description TEXT
)
BEGIN
    INSERT INTO Threat_Report (Habitat_ID, Ranger_ID, Report_Date, Threat_Level, Description)
    VALUES (p_Habitat_ID, p_Ranger_ID, CURDATE(), p_Threat_Level, p_Description);
END //
DELIMITER ;


-- -------------------------------------------------------
-- 4. FUNCTIONS
-- -------------------------------------------------------
DELIMITER $$

-- Function 1: Calculates Animal Age in years
CREATE FUNCTION age_of_animal(p_animal_id INT, p_sp_id INT)
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE age INT;
    SELECT TIMESTAMPDIFF(YEAR, DOB, CURDATE())
    INTO age
    FROM Animal
    WHERE Animal_ID = p_animal_id AND Sp_ID = p_sp_id;
    RETURN age;
END$$

-- Function 2: Calculates Ranger Experience in years
CREATE FUNCTION ranger_experience(t_ranger_id INT) RETURNS int
    DETERMINISTIC
BEGIN
	DECLARE years INT;
    SELECT timestampdiff(YEAR, date_joined, curdate()) INTO years
    FROM Ranger WHERE Ranger_ID = t_ranger_id;
    
RETURN years;
END$$
    
-- Function 3: Assigns a numerical score based on Threat_Level (High=3, Medium=2, Low=1)
CREATE FUNCTION threat_severity_score(p_report_id INT) RETURNS int
    DETERMINISTIC
BEGIN
    DECLARE v_level VARCHAR(20);
    DECLARE v_score INT;

    SELECT Threat_Level INTO v_level
    FROM Threat_Report
    WHERE Report_ID = p_report_id;

    SET v_score = CASE v_level
        WHEN 'Low' THEN 1
        WHEN 'Medium' THEN 2
        WHEN 'High' THEN 3
        ELSE 0
	END;
	RETURN v_score;
END$$
DELIMITER ;


-- -------------------------------------------------------
-- 5. TRIGGERS
-- -------------------------------------------------------
DELIMITER $$

-- Trigger 1: Prevents recording a sighting for an animal marked as 'Sick'
CREATE TRIGGER trg_no_sick_sighting
BEFORE INSERT ON Sighting_Details
FOR EACH ROW
BEGIN
    DECLARE v_health VARCHAR(50);
    SELECT Health_status
    INTO v_health
    FROM Animal
    WHERE Animal_ID = NEW.Animal_ID;
    
    IF v_health = 'Sick' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Cannot insert sighting for sick animals.';
    END IF;
END$$

-- Trigger 2: Sets Equipment status to 'In Use' upon assignment to a Ranger (INSERT into Uses)
CREATE TRIGGER trg_equipment_inuse AFTER INSERT ON Uses 
FOR EACH ROW 
BEGIN
    UPDATE Equipment
    SET StatusEqui = 'In Use'
    WHERE Equipment_ID = NEW.Equipment_ID;
END $$

-- Trigger 3: Sets Equipment status to 'Available' upon return (DELETE from Uses)
CREATE TRIGGER trg_equipment_available AFTER DELETE ON Uses 
FOR EACH ROW 
BEGIN
    UPDATE Equipment
    SET StatusEqui = 'Available'
    WHERE Equipment_ID = OLD.Equipment_ID;
END$$
DELIMITER ;


-- -------------------------------------------------------
-- 6. COMPLEX QUERIES (Used for Analytics/Reporting)
-- -------------------------------------------------------

-- 6.1 JOIN Query: List all equipment provided by organizations of type 'NGO'.
SELECT
    e.equip_type,
    e.purchase_date,
    e.StatusEqui AS equipment_status,
    o.fi_name AS organization_name
FROM Equipment e 
JOIN Organization o ON e.Org_ID = o.Org_ID 
WHERE o.typeOrg = 'NGO' 
ORDER BY o.fi_name, e.purchase_date;

-- 6.2 Aggregate Query: Count the number of individual animals cataloged for each species.
SELECT
    s.common_name,
    s.conservation_status,
    COUNT(a.Animal_ID) AS number_of_animals
FROM Species s 
LEFT JOIN Animal a ON s.Sp_ID = a.Sp_ID 
GROUP BY s.common_name, s.conservation_status 
ORDER BY number_of_animals DESC;

-- 6.3 Nested Query: Find the names and join dates of Senior Rangers who have filed at least one High-level threat report.
SELECT
    fname,
    date_joined
FROM
    Ranger
WHERE
    Ranger_ID IN (
        SELECT Ranger_ID
        FROM Threat_Report
        WHERE Threat_Level = 'High'
    )
    AND raankOfRanger = 'Senior Ranger';
    
-- user privileges

CREATE USER 'tanisha'@'localhost' IDENTIFIED BY 'tanisha';

SHOW GRANTS FOR 'tanisha'@'localhost';
GRANT SELECT ON wildlife_conservation.* TO 'tanisha'@'localhost';
FLUSH PRIVILEGES;

GRANT EXECUTE ON FUNCTION wildlife_conservation.age_of_animal TO 'tanisha'@'localhost';
GRANT EXECUTE ON FUNCTION wildlife_conservation.ranger_experience TO 'tanisha'@'localhost';
FLUSH PRIVILEGES;



USE wildlife_conservation;

CREATE USER 'bhoomika'@'localhost' IDENTIFIED BY 'bhoomika';


GRANT SELECT ON wildlife_conservation.* TO 'bhoomika'@'localhost';


GRANT EXECUTE ON FUNCTION wildlife_conservation.age_of_animal TO 'bhoomika'@'localhost';
GRANT EXECUTE ON FUNCTION wildlife_conservation.ranger_experience TO 'bhoomika'@'localhost';
GRANT EXECUTE ON FUNCTION wildlife_conservation.threat_severity_score TO 'bhoomika'@'localhost';


FLUSH PRIVILEGES;

SELECT '*** Bhoomika User Created and Privileges Granted ***' AS Status;
SHOW GRANTS FOR 'bhoomika'@'localhost';

-- users



CREATE USER IF NOT EXISTS 'app_employee'@'localhost' IDENTIFIED BY 'employee123';

-- Employee privileges: Can view data, add new records, and update existing records
-- Cannot delete or modify database structure (except for Threat_Report which is vital for them)
GRANT SELECT, INSERT, UPDATE ON wildlife_conservation.* TO 'app_employee'@'localhost';

-- Explicitly remove DELETE permission on all tables for safety (optional but good practice)
REVOKE DELETE ON wildlife_conservation.* FROM 'app_employee'@'localhost';


CREATE USER IF NOT EXISTS 'app_supervisor'@'localhost' IDENTIFIED BY 'supervisor123';

-- Supervisor privileges: Full CRUD (SELECT, INSERT, UPDATE, DELETE) on all data tables
GRANT SELECT, INSERT, UPDATE, DELETE ON wildlife_conservation.* TO 'app_supervisor'@'localhost';

-- Grant execution of stored routines needed for logging/updating
GRANT EXECUTE ON wildlife_conservation.* TO 'app_supervisor'@'localhost';


FLUSH PRIVILEGES;

SELECT '*** Employee and Supervisor Users Created/Updated ***' AS Status;
SHOW GRANTS FOR 'app_employee'@'localhost';
SHOW GRANTS FOR 'app_supervisor'@'localhost';