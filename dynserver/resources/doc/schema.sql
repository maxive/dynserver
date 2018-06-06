-- Copyright 2013 Dustin Frisch <fooker@lab.sh>
-- 
-- This file is part of dynserver.
-- 
-- dynserver is free software: you can redistribute it and/or modify
-- it under the terms of the GNU Affero General Public License as 
-- published by the Free Software Foundation, either version 3 of the 
-- License, or (at your option) any later version.
-- 
-- dynserver is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU Affero General Public License for more details.
-- 
-- You should have received a copy of the GNU Affero General Public License
-- along with dynserver.  If not, see <http://www.gnu.org/licenses/>.


DROP TABLE IF EXISTS `users`;
DROP TABLE IF EXISTS `suffixes`;
DROP TABLE IF EXISTS `hosts`;


--
-- table users
--
CREATE TABLE `users` (
  `id`          INT            NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `username`    VARCHAR(255)   NOT NULL UNIQUE,
  `password`    VARCHAR(255)   NULL DEFAULT NULL,
  `email`       VARCHAR(255)   NOT NULL,
  `admin`       BOOLEAN        NOT NULL DEFAULT FALSE,
  `active`      BOOLEAN        NOT NULL DEFAULT FALSE,
  `created`     TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `authcode`    VARCHAR(36)    NULL DEFAULT NULL,
  `maxhosts`    INT            NULL DEFAULT NULL

) ENGINE=InnoDB DEFAULT CHARACTER SET utf8;


-- 
-- table suffixes
-- 
CREATE TABLE `suffixes` (
  `id`          INT             NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `name`        VARCHAR(255)    NOT NULL UNIQUE

) ENGINE=InnoDB DEFAULT CHARACTER SET utf8;


--
-- table hosts
--
CREATE TABLE `hosts` (
  `id`          INT             NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `user_id`     INT             NOT NULL,
  `suffix_id`   INT             NOT NULL,
  `hostname`    VARCHAR(255)    NOT NULL,
  `address`     VARCHAR(15)     NULL DEFAULT NULL,
  `address_v6`  VARCHAR(39)     NULL DEFAULT NULL,
  `description` VARCHAR(255)    NULL DEFAULT NULL,
  `password`    VARCHAR(255)    NOT NULL,
  `updated`     TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (`user_id`)       REFERENCES `users` (`id`) ON DELETE CASCADE ,
  FOREIGN KEY (`suffix_id`)     REFERENCES `suffixes` (`id`) ON DELETE CASCADE ,
  
  UNIQUE (`hostname`, `suffix_id`),

  INDEX (`address`),
  INDEX (`user_id`, `hostname`)

) ENGINE=InnoDB DEFAULT CHARACTER SET utf8;


--
-- default user admin with password admin
--
INSERT INTO `users` (
  `id`,
  `username`,
  `password`,
  `email`,
  `admin`,
  `active`
) VALUES (
  1,
  'admin',
  '$6$rounds=65488$jZYVZUGK9mNdQeTj$2MTmn67qFtmg.xKbonwE4OcwCe9z64duk0vgh3nCP6yIBiERxk3t4hFYuytxZF0jmwbpSyq.B3DKtb6CyQ2tG.',
  'admin@example.com',
  1,
  1
);
