CREATE TABLE `imgcollection`.`user` (
  `userid` BIGINT(20) NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(64) NULL,
  `password` VARCHAR(256) NULL,
  PRIMARY KEY (`userid`));

CREATE TABLE `imgcollection`.`photo` (
  `photoid` BIGINT(20) NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(64) NULL,
  `caption` VARCHAR(1024) NULL,
  `owner` VARCHAR(64) NULL,
  `timestamp` BIGINT(20) NULL,
  PRIMARY KEY (`photoid`));