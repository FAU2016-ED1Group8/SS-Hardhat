DELIMITER $$
USE `smarthat_data`$$
CREATE PROCEDURE `spAddGPSLog` (
IN p_name varchar(45),
IN p_lat float,
IN p_lon float,
IN p_time_tx datetime(6),
IN p_time_rx datetime(6)
)
BEGIN

insert into location_log
(
    name,
    lat,
    lon,
    time_sent,
    time_received


)
values
(
    p_name,
    p_lat,
    p_lon,
    p_time_tx,
    p_time_rx
);

END$$

DELIMITER ;
