/*
Navicat MySQL Data Transfer

Source Server         : database
Source Server Version : 50553
Source Host           : localhost:3306
Source Database       : flask_crawler

Target Server Type    : MYSQL
Target Server Version : 50553
File Encoding         : 65001

Date: 2017-06-12 16:50:03
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for admin
-- ----------------------------
DROP TABLE IF EXISTS `admin`;
CREATE TABLE `admin` (
  `userid` varchar(20) NOT NULL,
  `password` varchar(40) DEFAULT NULL,
  `username` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`userid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of admin
-- ----------------------------
INSERT INTO `admin` VALUES ('1111', '1223333', 'hanyuehui');
INSERT INTO `admin` VALUES ('123', 'c20ad4d76fe97759aa27a0c99bff6710', '韩月辉');
INSERT INTO `admin` VALUES ('1327406021', '111', '沈涛');

-- ----------------------------
-- Table structure for task
-- ----------------------------
DROP TABLE IF EXISTS `task`;
CREATE TABLE `task` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `task_name` varchar(100) DEFAULT NULL,
  `userid` varchar(30) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `finished_at` datetime DEFAULT NULL,
  `search_name` varchar(30) DEFAULT NULL,
  `search_type` varchar(5) DEFAULT NULL,
  `remark` varchar(300) DEFAULT NULL,
  `thread_num` tinyint(1) DEFAULT NULL,
  `deepth` tinyint(1) DEFAULT NULL,
  `style` tinyint(1) DEFAULT NULL,
  `extension` tinyint(1) DEFAULT NULL,
  `tweet_num` int(11) DEFAULT NULL,
  `friends_num` int(11) DEFAULT NULL,
  `followers_num` int(11) DEFAULT NULL,
  `basicinfo_num` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of task
-- ----------------------------

-- ----------------------------
-- Table structure for user_task
-- ----------------------------
DROP TABLE IF EXISTS `user_task`;
CREATE TABLE `user_task` (
  `user_id` varchar(30) NOT NULL,
  `screen_name` varchar(50) NOT NULL,
  `name` varchar(50) DEFAULT NULL,
  `location` varchar(100) DEFAULT NULL,
  `created_at` varchar(50) DEFAULT NULL,
  `description` text,
  `statuses_count` int(11) DEFAULT NULL,
  `friends_count` int(11) DEFAULT NULL,
  `followers_count` int(11) DEFAULT NULL,
  `favourites_count` int(11) DEFAULT NULL,
  `lang` varchar(20) DEFAULT NULL,
  `protected` tinyint(1) DEFAULT NULL,
  `time_zone` varchar(50) DEFAULT NULL,
  `verified` tinyint(1) DEFAULT NULL,
  `utc_offset` varchar(20) DEFAULT NULL,
  `geo_enabled` tinyint(1) DEFAULT NULL,
  `listed_count` int(11) DEFAULT NULL,
  `is_translator` tinyint(1) DEFAULT NULL,
  `default_profile_image` tinyint(1) DEFAULT NULL,
  `profile_background_color` varchar(10) DEFAULT NULL,
  `profile_sidebar_fill_color` varchar(10) DEFAULT NULL,
  `profile_image_url` varchar(250) DEFAULT NULL,
  `crawler_date` date DEFAULT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of user_task
-- ----------------------------
