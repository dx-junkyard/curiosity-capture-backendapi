CREATE TABLE curiosity_log (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id VARCHAR(255) NOT NULL,
    speaker_type  INT(8) UNSIGNED,
    message TEXT,
    msg_cate INT(8) UNSIGNED,
    msg_type INT(8) UNSIGNED,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
