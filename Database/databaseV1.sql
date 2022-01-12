prosumer_infoUserUser-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema M7011e
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema M7011e
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `M7011e` DEFAULT CHARACTER SET utf8 ;
USE `M7011e` ;

-- -----------------------------------------------------
-- Table `M7011e`.`station`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `M7011e`.`station` (
  `wind_speed` INT NOT NULL,
  `temperature` INT NOT NULL,
  `station_id` INT NOT NULL AUTO_INCREMENT,
  `lon` VARCHAR(45) NOT NULL,
  `lat` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`station_id`),
  UNIQUE INDEX `station_id_UNIQUE` (`station_id` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `M7011e`.`house_hold`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `M7011e`.`house_hold` (
  `house_hold_id` INT NOT NULL AUTO_INCREMENT,
  `closest_station_id` INT NOT NULL,
  `user_name` VARCHAR(45) NOT NULL,
  `password` VARCHAR(45) NOT NULL,
  `email` VARCHAR(45) NOT NULL,
  `address` VARCHAR(45) NOT NULL,
  `zipcode` VARCHAR(45) NOT NULL,
  `prosumer` TINYINT NOT NULL,
  `lon` VARCHAR(45) NOT NULL,
  `lat` VARCHAR(45) NOT NULL,
  `usage` VARCHAR(45) NOT NULL,
  `distans_to_station` INT NOT NULL,
  UNIQUE INDEX `house_hold_id_UNIQUE` (`house_hold_id` ASC) VISIBLE,
  PRIMARY KEY (`house_hold_id`),
  INDEX `station_id_index` (`closest_station_id` ASC) VISIBLE,
  INDEX `prosumer_index` (`zipcode` ASC) VISIBLE,
  CONSTRAINT `fk_house_hold_station1`
    FOREIGN KEY (`closest_station_id`)
    REFERENCES `M7011e`.`station` (`station_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `M7011e`.`prosumer_info`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `M7011e`.`prosumer_info` (
  `house_hold_id` INT NOT NULL,
  `buffert` INT NULL,
  `ratio` INT NULL,
  `production` INT NULL,
  PRIMARY KEY (`house_hold_id`),
  UNIQUE INDEX `house_hold_id_UNIQUE` (`house_hold_id` ASC) VISIBLE,
  CONSTRAINT `fk_prosumer_info_house_hold1`
    FOREIGN KEY (`house_hold_id`)
    REFERENCES `M7011e`.`house_hold` (`house_hold_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
