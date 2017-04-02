DELIMITER //

CREATE PROCEDURE `imgcollection`.`sp_uploadPhoto`(
    IN p_name VARCHAR(64),
    IN p_caption VARCHAR(1024),
    IN p_owner VARCHAR(64),
    IN p_timestamp BIGINT(20)
)
BEGIN
	INSERT INTO photo
	(
		name,
		caption,
        owner,
        timestamp
	)
	VALUES
	(
		p_name,
		p_caption,
        p_owner,
        p_timestamp
	);
END//