CREATE TABLE IF NOT EXISTS build_runs (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    job_name     VARCHAR(100) NOT NULL,
    build_number INT NOT NULL,
    branch       VARCHAR(100),
    status       VARCHAR(20),
    duration_ms  INT,
    started_at   DATETIME NOT NULL,
    triggered_by VARCHAR(100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS test_runs (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    build_id      INT,
    suite_name    VARCHAR(100),
    test_name     VARCHAR(200) NOT NULL,
    status        VARCHAR(20),
    duration_ms   INT,
    run_at        DATETIME NOT NULL,
    error_message TEXT,
    KEY (build_id),
    CONSTRAINT test_runs_ibfk_1 FOREIGN KEY (build_id) REFERENCES build_runs(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
