--schema.sql

CREATE DATABASE IF NOT EXISTS HikeReview;

USE HikeReview;

--table to store user info
CREATE TABLE Users {
    user_id INT AUTO_INCREMENT PRIMARY KEY, --create unique id
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
};

--table to store hike info
CREATE TABLE Hikes{
    trail_id INT AUTO_INCREMENT PRIMARY KEY,    --create unique id
    trail_name VARCHAR(100) NOT NULL,
    location VARCHAR(255),
    difficulty ENUM('Easy', 'Moderate', 'Hard') NOT NULL,
    distance FLOAT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
};

--table for reviews
CREATE TABLE Reviews (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    trail_id INT NOT NULL,
    user_id INT NOT NULL,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    review_text TEXT,
    review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trail_id) REFERENCES Trails(trail_id) ON DELETE CASCADE,   --check for valid id
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE       --check for valid id
);
--if trail/user id is deleted, corresponding reviews are deleted