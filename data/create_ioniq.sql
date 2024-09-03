DROP TABLE IF EXISTS ioniq;
CREATE TABLE IF NOT EXISTS ioniq (
    post_id serial PRIMARY KEY,
    upload_date TIMESTAMP,
    upload_time TIME,
    title TEXT,
    num_view INT,
    num_like INT,
    body TEXT,
    comments TEXT,
    car_name VARCHAR(255),
    community VARCHAR(255),
    comm_url VARCHAR(500)
);
