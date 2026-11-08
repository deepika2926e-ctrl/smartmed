-- =====================================================================
-- SMARTMED DATABASE SCHEMA (MySQL 8.0+ / MariaDB)
-- Production-Ready DDL and Educational Sample Data
-- =====================================================================

CREATE DATABASE IF NOT EXISTS `smartmed` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `smartmed`;

-- Drop existing tables in reverse dependency order
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS `user_settings`;
DROP TABLE IF EXISTS `prescriptions`;
DROP TABLE IF EXISTS `notifications`;
DROP TABLE IF EXISTS `medicine_logs`;
DROP TABLE IF EXISTS `medicine_schedules`;
DROP TABLE IF EXISTS `medicines`;
DROP TABLE IF EXISTS `educational_medicines`;
DROP TABLE IF EXISTS `users`;
SET FOREIGN_KEY_CHECKS = 1;

-- ---------------------------------------------------------------------
-- 1. USERS TABLE
-- ---------------------------------------------------------------------
CREATE TABLE `users` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `full_name` VARCHAR(100) NOT NULL,
  `email` VARCHAR(150) NOT NULL UNIQUE,
  `hashed_password` VARCHAR(255) NOT NULL,
  `phone` VARCHAR(30) DEFAULT NULL,
  `emergency_contact` VARCHAR(150) DEFAULT NULL,
  `avatar_url` VARCHAR(255) DEFAULT NULL,
  `role` VARCHAR(20) DEFAULT 'patient',
  `is_active` BOOLEAN DEFAULT TRUE,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX `idx_users_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- 2. MEDICINES TABLE
-- ---------------------------------------------------------------------
CREATE TABLE `medicines` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `name` VARCHAR(150) NOT NULL,
  `generic_name` VARCHAR(150) DEFAULT NULL,
  `category` VARCHAR(100) DEFAULT 'General',
  `dosage` VARCHAR(100) NOT NULL,
  `form` VARCHAR(50) DEFAULT 'Tablet',
  `frequency` VARCHAR(100) DEFAULT 'Once daily',
  `instructions` VARCHAR(255) DEFAULT NULL,
  `start_date` DATE NOT NULL,
  `end_date` DATE DEFAULT NULL,
  `doctor_name` VARCHAR(150) DEFAULT NULL,
  `notes` TEXT DEFAULT NULL,
  `status` VARCHAR(20) DEFAULT 'active',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  INDEX `idx_med_user` (`user_id`),
  INDEX `idx_med_status` (`status`),
  INDEX `idx_med_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- 3. MEDICINE_SCHEDULES TABLE
-- ---------------------------------------------------------------------
CREATE TABLE `medicine_schedules` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `medicine_id` INT NOT NULL,
  `reminder_time` VARCHAR(10) NOT NULL,
  `time_of_day` VARCHAR(30) DEFAULT 'morning',
  `days_of_week` VARCHAR(100) DEFAULT 'Mon,Tue,Wed,Thu,Fri,Sat,Sun',
  `dosage_quantity` VARCHAR(50) DEFAULT '1 tablet',
  `is_active` BOOLEAN DEFAULT TRUE,
  `start_date` DATE DEFAULT NULL,
  `end_date` DATE DEFAULT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`medicine_id`) REFERENCES `medicines` (`id`) ON DELETE CASCADE,
  INDEX `idx_sched_user` (`user_id`),
  INDEX `idx_sched_medicine` (`medicine_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- 4. MEDICINE_LOGS TABLE
-- ---------------------------------------------------------------------
CREATE TABLE `medicine_logs` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `medicine_id` INT NOT NULL,
  `schedule_id` INT DEFAULT NULL,
  `scheduled_time` DATETIME NOT NULL,
  `logged_time` DATETIME DEFAULT NULL,
  `status` VARCHAR(20) DEFAULT 'pending',
  `notes` TEXT DEFAULT NULL,
  `snooze_until` DATETIME DEFAULT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`medicine_id`) REFERENCES `medicines` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`schedule_id`) REFERENCES `medicine_schedules` (`id`) ON DELETE SET NULL,
  INDEX `idx_logs_user` (`user_id`),
  INDEX `idx_logs_scheduled` (`scheduled_time`),
  INDEX `idx_logs_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- 5. NOTIFICATIONS TABLE
-- ---------------------------------------------------------------------
CREATE TABLE `notifications` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `medicine_id` INT DEFAULT NULL,
  `title` VARCHAR(200) NOT NULL,
  `message` TEXT NOT NULL,
  `notification_type` VARCHAR(50) DEFAULT 'reminder',
  `is_read` BOOLEAN DEFAULT FALSE,
  `scheduled_for` DATETIME DEFAULT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`medicine_id`) REFERENCES `medicines` (`id`) ON DELETE SET NULL,
  INDEX `idx_notif_user` (`user_id`),
  INDEX `idx_notif_read` (`is_read`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- 6. PRESCRIPTIONS TABLE
-- ---------------------------------------------------------------------
CREATE TABLE `prescriptions` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `medicine_id` INT DEFAULT NULL,
  `doctor_name` VARCHAR(150) DEFAULT NULL,
  `hospital_clinic` VARCHAR(200) DEFAULT NULL,
  `prescription_date` DATE DEFAULT NULL,
  `file_path` VARCHAR(255) NOT NULL,
  `file_name` VARCHAR(255) NOT NULL,
  `file_type` VARCHAR(50) DEFAULT NULL,
  `notes` TEXT DEFAULT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`medicine_id`) REFERENCES `medicines` (`id`) ON DELETE SET NULL,
  INDEX `idx_presc_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- 7. USER_SETTINGS TABLE
-- ---------------------------------------------------------------------
CREATE TABLE `user_settings` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL UNIQUE,
  `email_notifications` BOOLEAN DEFAULT TRUE,
  `browser_notifications` BOOLEAN DEFAULT TRUE,
  `sound_alerts` BOOLEAN DEFAULT TRUE,
  `reminder_advance_minutes` INT DEFAULT 0,
  `theme` VARCHAR(20) DEFAULT 'light',
  `timezone` VARCHAR(50) DEFAULT 'UTC',
  `language` VARCHAR(20) DEFAULT 'en',
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  INDEX `idx_settings_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- 8. EDUCATIONAL_MEDICINES TABLE (Reference Library)
-- ---------------------------------------------------------------------
CREATE TABLE `educational_medicines` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(150) NOT NULL,
  `generic_name` VARCHAR(150) NOT NULL,
  `brand_names` VARCHAR(255) DEFAULT NULL,
  `category` VARCHAR(100) NOT NULL,
  `description` TEXT NOT NULL,
  `common_uses` TEXT NOT NULL,
  `mechanism_of_action` TEXT NOT NULL,
  `available_forms` VARCHAR(255) NOT NULL,
  `common_side_effects` TEXT NOT NULL,
  `serious_side_effects` TEXT NOT NULL,
  `precautions` TEXT NOT NULL,
  `drug_interactions` TEXT NOT NULL,
  `storage_instructions` TEXT NOT NULL,
  `general_usage_info` TEXT NOT NULL,
  `reference_sources` TEXT NOT NULL,
  `disclaimer` TEXT NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX `idx_edu_name` (`name`),
  INDEX `idx_edu_category` (`category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================================
-- SAMPLE EDUCATIONAL MEDICINE DATA (FOR DEMONSTRATION & REFERENCE)
-- Sourced from MedlinePlus, NHS UK, and FDA official prescribing labels
-- =====================================================================

INSERT INTO `educational_medicines` 
(`name`, `generic_name`, `brand_names`, `category`, `description`, `common_uses`, `mechanism_of_action`, `available_forms`, `common_side_effects`, `serious_side_effects`, `precautions`, `drug_interactions`, `storage_instructions`, `general_usage_info`, `reference_sources`, `disclaimer`)
VALUES
(
  'Amoxicillin',
  'Amoxicillin',
  'Amoxil, Trimox, Moxatag',
  'Antibiotic',
  'Amoxicillin is a moderate-spectrum, bactericidal beta-lactam penicillin-class antibiotic used to treat bacterial infections.',
  'Used for bacterial chest infections (pneumonia, bronchitis), ear infections (otitis media), tonsillitis, sinusitis, urinary tract infections, and dental abscesses.',
  'Inhibits bacterial cell wall synthesis by binding to penicillin-binding proteins (PBPs), leading to lysis and destruction of bacteria.',
  'Oral capsules (250mg, 500mg), tablets (875mg), oral suspension (125mg/5ml, 250mg/5ml), chewable tablets.',
  'Mild diarrhea, nausea, vomiting, mild skin rash, headache, changes in taste.',
  'Severe watery diarrhea with blood (C. difficile), anaphylaxis (hives, tongue swelling, difficulty breathing), jaundice, high fever.',
  'Inform physician of penicillin allergy, mononucleosis, kidney disease, or asthma. Complete the full course.',
  'Methotrexate, probenecid, allopurinol, warfarin, oral typhoid vaccine.',
  'Store capsules at room temperature (20°C to 25°C). Reconstituted liquid suspension must be kept refrigerated and discarded after 14 days.',
  'Typically taken every 8 to 12 hours with a full glass of water. Can be taken with or without food.',
  'NHS UK Medicines A-Z (Amoxicillin); U.S. National Library of Medicine (MedlinePlus #685001); DailyMed FDA Labels.',
  'Educational Information Only: Sourced from official public health monographs. Never start, discontinue, or alter medications without professional guidance.'
),
(
  'Paracetamol (Acetaminophen)',
  'Paracetamol / Acetaminophen',
  'Tylenol, Panadol, Calpol, Mapap',
  'Analgesic & Antipyretic',
  'A widely used non-opioid pain reliever and fever reducer for mild-to-moderate pain and febrile conditions.',
  'Headaches, migraines, muscle aches, toothache, back pain, osteoarthritis discomfort, menstrual cramps, cold/flu fever.',
  'Acts primarily in the central nervous system to inhibit prostaglandin synthesis; reduces fever via action on the hypothalamic heat-regulating center.',
  'Tablets (325mg, 500mg, 650mg ER), oral liquid/syrup (160mg/5ml), suppositories, IV infusion.',
  'Generally well tolerated at therapeutic doses. Mild nausea or dyspepsia may occur rarely.',
  'Severe liver toxicity (hepatotoxicity) especially with overdose, Stevens-Johnson syndrome, dark urine, jaundice.',
  'Never exceed 4,000 mg in 24 hours for adults. Check all OTC cold products to prevent accidental doubling.',
  'Chronic alcohol consumption, warfarin, isoniazid.',
  'Store at controlled room temperature (15°C to 30°C) protected from moisture and light.',
  'Adult dose is usually 500mg to 1000mg every 4 to 6 hours as needed, with minimum 4-hour interval.',
  'MedlinePlus (Acetaminophen); NHS Health A to Z (Paracetamol); British National Formulary.',
  'Educational Information Only: Consult your doctor if fever or pain persists. Avoid alcohol while taking acetaminophen.'
),
(
  'Metformin',
  'Metformin Hydrochloride',
  'Glucophage, Fortamet, Glumetza, Riomet',
  'Antidiabetic (Biguanide)',
  'First-line oral medication for the management of type 2 diabetes mellitus and polycystic ovary syndrome (PCOS).',
  'Lowers blood glucose levels in type 2 diabetes; improves insulin sensitivity; adjunctive treatment in PCOS.',
  'Decreases hepatic glucose production, decreases intestinal absorption of glucose, and improves insulin sensitivity.',
  'Immediate-release tablets (500mg, 850mg, 1000mg), extended-release (XR/ER) tablets (500mg, 750mg, 1000mg).',
  'Abdominal discomfort, diarrhea, bloating, nausea, metallic taste in mouth, flatulence.',
  'Lactic acidosis (rare: rapid breathing, severe fatigue, muscle aches, abdominal pain), vitamin B12 deficiency with prolonged use.',
  'Contraindicated in severe renal impairment (eGFR < 30 mL/min). Withhold before iodinated radiocontrast procedures.',
  'Alcohol (increases lactic acidosis risk), cimetidine, furosemide.',
  'Store at 20°C to 25°C (68°F to 77°F). Keep bottle tightly closed.',
  'Take with meals to minimize gastrointestinal upset. Swallow extended-release tablets whole.',
  'American Diabetes Association Standards of Care; MedlinePlus (Metformin); NHS UK.',
  'Educational Information Only: Regular monitoring of kidney function (eGFR) and blood glucose is required.'
),
(
  'Amlodipine',
  'Amlodipine Besylate',
  'Norvasc, Katerzia, Amvaz',
  'Antihypertensive',
  'A long-acting dihydropyridine calcium channel blocker used to treat high blood pressure and angina.',
  'Hypertension (high blood pressure), chronic stable angina, vasospastic angina.',
  'Inhibits transmembrane influx of extracellular calcium ions into vascular smooth muscle, causing vasodilation.',
  'Oral tablets (2.5mg, 5mg, 10mg), oral suspension (1mg/ml).',
  'Peripheral edema (swelling of ankles/feet), dizziness, flushing, palpitations, fatigue, headache.',
  'Severe hypotension, worsening of angina upon initial dose titration in severe coronary disease.',
  'Caution in patients with severe hepatic impairment or severe aortic stenosis. Do not discontinue abruptly.',
  'Simvastatin (limit to 20mg daily), tacrolimus, cyclosporine, CYP3A4 inhibitors (ketoconazole, diltiazem).',
  'Store between 15°C and 30°C in a light-resistant container.',
  'Usually taken once daily at the same time every day, with or without food.',
  'MedlinePlus (Amlodipine); NHS UK (Amlodipine); FDA Approved Prescribing Information.',
  'Educational Information Only: Continue taking your blood pressure medication even if you feel completely well.'
);
