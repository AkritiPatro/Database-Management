-- Create Database
CREATE DATABASE IF NOT EXISTS user_management;
USE user_management;

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

-- Check All Users
SELECT * FROM users;

-- Documents Table (Linked to Users)
CREATE TABLE IF NOT EXISTS documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    filename VARCHAR(255) NOT NULL,
    filepath VARCHAR(255) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Check All Documents
SELECT * FROM documents;

-- Grades Table
DROP TABLE grades;
CREATE TABLE IF NOT EXISTS grades (
    grade_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    subject VARCHAR(100) NOT NULL,
    grade VARCHAR(5) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

INSERT INTO grades (user_id, subject, grade) VALUES
(1, 'Mathematics', 'A'),
(1, 'Physics', 'B'),
(1, 'Computer Science', 'A'),
(2, 'Mathematics', 'B'),
(2, 'Physics', 'A'),
(2, 'Computer Science', 'B');

-- Check All Grades
SELECT * FROM grades;

-- Check All Tables
SHOW TABLES;