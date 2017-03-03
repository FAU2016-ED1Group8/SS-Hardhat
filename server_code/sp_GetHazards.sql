USE `smarthat_data`;
DROP procedure IF EXISTS `GetAllHazards`;

DELIMITER $$
USE `smarthat_data`$$
CREATE PROCEDURE `GetAllHazards` (
in p_name varchar(50)
)
BEGIN
    select id, hat_name, rec_time, lat, lon, description WHERE hat_name = p_name;
END$$

DELIMITER ;
