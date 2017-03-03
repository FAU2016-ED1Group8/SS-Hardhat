CREATE TABLE unit_location_log (
    unit_id VARCHAR,
    lat DOUBLE(32),
    lon DOUBLE,
    location_time DATETIME,
    receipt_time DATETIME
);
CREATE TABLE registered_units (
  rec_no INT AUTO_INCREMENT,
  unit_id VARCHAR(32)
);
