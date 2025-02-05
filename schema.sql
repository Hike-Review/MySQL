-- schema.sql

CREATE DATABASE IF NOT EXISTS hikereviewdb;

USE hikereviewdb;

-- table to store user info
CREATE TABLE IF NOT EXISTS Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,     -- create unique id
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- table to store hike info
CREATE TABLE IF NOT EXISTS Hikes(
    trail_id INT AUTO_INCREMENT PRIMARY KEY,    -- create unique id
    trail_name VARCHAR(100) NOT NULL,
    difficulty ENUM('Easy', 'Moderate', 'Hard') NOT NULL,
    rating FLOAT,
    distance FLOAT,
    duration FLOAT,
    start_lat DECIMAL(9,6) NOT NULL,
    start_lng DECIMAL(9,6) NOT NULL,
    end_lat DECIMAL(9,6) NOT NULL,
    end_lng DECIMAL(9,6) NOT NULL,
    tags VARCHAR (100),
    description TEXT,
    creator_id INT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- table to store route points for hikes
CREATE TABLE IF NOT EXISTS RoutePoints (
    point_id INT AUTO_INCREMENT PRIMARY KEY,
    trail_id INT NOT NULL,
    latitude DECIMAL(9,6) NOT NULL,
    longitude DECIMAL(9,6) NOT NULL,
    point_order INT NOT NULL,                   -- to keep track of the sequence
    FOREIGN KEY (trail_id) REFERENCES Hikes(trail_id) ON DELETE CASCADE
);
-- table for reviews
CREATE TABLE IF NOT EXISTS Reviews (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    trail_id INT NOT NULL,
    user_id INT NOT NULL,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    review_text TEXT,
    review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trail_id) REFERENCES Hikes(trail_id) ON DELETE CASCADE,    -- check for valid id
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE       -- check for valid id
);
-- if trail/user id is deleted, corresponding reviews are deleted

-- table for group info
CREATE TABLE IF NOT EXISTS UserGroups (
    group_id INT AUTO_INCREMENT PRIMARY KEY,      -- create unique id
    group_name VARCHAR (255) NOT NULL,              
    group_description TEXT,                        
    created_by INT NOT NULL,                      
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- table for storing user favorite hikes
CREATE TABLE IF NOT EXISTS FavoriteHikes (
    user_id INT NOT NULL,
    trail_id INT NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, trail_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (trail_id) REFERENCES Hikes(trail_id) ON DELETE CASCADE
);