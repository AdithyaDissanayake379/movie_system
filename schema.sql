CREATE DATABASE IF NOT EXISTS movie_rental CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE movie_rental;
CREATE TABLE IF NOT EXISTS employees (
 employee_id INT AUTO_INCREMENT PRIMARY KEY,
 username VARCHAR(80) NOT NULL UNIQUE,
 password_hash VARCHAR(100) NOT NULL
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS movies (
 movie_id INT AUTO_INCREMENT PRIMARY KEY,
 title VARCHAR(200) NOT NULL,
 genre VARCHAR(100) NOT NULL,
 release_year SMALLINT UNSIGNED NOT NULL,
 rental_price DECIMAL(10,2) NOT NULL,
 producer VARCHAR(150) NOT NULL,
 INDEX idx_movies_title (title), INDEX idx_movies_genre (genre),
 INDEX idx_movies_producer (producer)
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS customers (
 customer_id INT AUTO_INCREMENT PRIMARY KEY,
 name VARCHAR(150) NOT NULL,
 contact VARCHAR(200) NOT NULL,
 INDEX idx_customers_name (name)
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS rentals (
 rental_id INT AUTO_INCREMENT PRIMARY KEY,
 movie_id INT NOT NULL,
 customer_id INT NOT NULL,
 rental_date DATE NOT NULL,
 due_date DATE NOT NULL,
 return_date DATE NULL,
 late_fee DECIMAL(10,2) NOT NULL DEFAULT 0,
 CONSTRAINT fk_rental_movie FOREIGN KEY (movie_id) REFERENCES movies(movie_id) ON DELETE RESTRICT,
 CONSTRAINT fk_rental_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE RESTRICT,
 CONSTRAINT ck_due_date CHECK (due_date >= rental_date),
 INDEX idx_rentals_customer (customer_id),
 INDEX idx_rentals_dates (due_date,return_date)
) ENGINE=InnoDB;
