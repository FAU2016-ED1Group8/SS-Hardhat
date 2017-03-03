DELIMITER $$
USE `ItemListDb`$$
CREATE PROCEDURE `spCreateUser` (
IN p_Username varchar(50),
IN p_Password varchar(50)
)
BEGIN

if ( select exists (select 1 from tblUser where UserName = p_username) ) THEN

    select 'Username Exists !!';

ELSE

insert into tblUser
(
    UserName,
    Password
)
values
(
    p_Username,
    p_Password
);

END IF;

END$$

DELIMITER ;
