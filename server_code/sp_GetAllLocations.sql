USE `smarthat_data`;
DROP procedure IF EXISTS `GetAllLocations`;

DELIMITER $$
USE `smarthat_data`$$
CREATE PROCEDURE `GetAllLocations` (
in p_name varchar(45)
)
BEGIN
    select id, unit_name, lat, lon, time_setn, time_received WHERE unit_name = p_name;
END$$

DELIMITER ;
