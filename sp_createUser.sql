DELIMITER //

CREATE PROCEDURE `imgcollection`.`sp_createUser`(
    IN p_username VARCHAR(64),
    IN p_password VARCHAR(256)
)
BEGIN
    IF (SELECT EXISTS (SELECT 1 FROM user WHERE username = p_username) ) THEN
        SELECT 'This username already exists. Please select another one.';
     
    ELSE
        INSERT INTO user
        (
            username,
            password
        )
        VALUES
        (
            p_username,
            p_password
        );
     
    END IF;
END//