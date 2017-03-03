DELIMITER $$
USE `smarthat_data`$$
CREATE PROCEDURE `spAddDevice` (
IN p_name varchar(45),
IN p_key varchar(100)
)
BEGIN

if ( select exists (select 1 from authorized_devices where name = p_name) ) THEN

    select 'Device Already Registered !!';

ELSE

insert into authorized_devices
(
    name,
    secret
)
values
(
    p_name,
    p_key
);

END IF;

END$$

DELIMITER ;
