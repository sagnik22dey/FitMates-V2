-- Drop existing tables if they exist (clean database)
DROP TABLE IF EXISTS reports CASCADE;
DROP TABLE IF EXISTS submissions CASCADE;
DROP TABLE IF EXISTS forms CASCADE;
DROP TABLE IF EXISTS clients CASCADE;
DROP TABLE IF EXISTS admins CASCADE;

-- Admins Table
CREATE TABLE admins (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Clients Table
CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    dob DATE,
    height DECIMAL(5,2),
    weight DECIMAL(5,2),
    mobile VARCHAR(20),
    medical_history VARCHAR(1000),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Forms Table
CREATE TABLE forms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    data JSONB NOT NULL,
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'published')),
    is_template BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- History/Submissions Table
CREATE TABLE submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
    form_id UUID REFERENCES forms(id) ON DELETE CASCADE,
    data JSONB NOT NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reports Table
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
    submission_id UUID REFERENCES submissions(id) ON DELETE CASCADE,
    generated_report_data JSONB NOT NULL,
    period VARCHAR(20) CHECK (period IN ('weekly', 'monthly')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_forms_client_id ON forms(client_id);
CREATE INDEX idx_forms_status ON forms(status);
CREATE INDEX idx_forms_client_status ON forms(client_id, status);
CREATE INDEX idx_forms_is_template ON forms(is_template) WHERE is_template = true;

CREATE INDEX idx_submissions_client_id ON submissions(client_id);
CREATE INDEX idx_submissions_form_id ON submissions(form_id);
CREATE INDEX idx_submissions_client_form ON submissions(client_id, form_id);
CREATE INDEX idx_submissions_submitted_at ON submissions(submitted_at DESC);

CREATE INDEX idx_reports_client_id ON reports(client_id);
CREATE INDEX idx_reports_submission_id ON reports(submission_id);
CREATE INDEX idx_reports_created_at ON reports(created_at DESC);

CREATE INDEX idx_clients_email ON clients(email);

-- Insert a default admin account (password: admin123)
-- Password hash for 'admin123' using bcrypt
INSERT INTO admins (email, password) VALUES 
('admin@fitmates.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvQu6');

-- Insert sample client for testing (password: client123)
INSERT INTO clients (name, email, password, dob, height, weight, mobile, medical_history) VALUES 
('John Doe', 'john@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvQu6', '1990-05-15', 175.5, 75.0, '+1234567890', 'No known allergies');
