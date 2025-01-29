-- Patients Table
CREATE TABLE patients (
    patient_id UUID PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_updated TIMESTAMPTZ,
    demographics JSONB        -- Age, gender, etc.
);

-- Documents Table
CREATE TABLE documents (
    doc_id UUID PRIMARY KEY,
    patient_id UUID REFERENCES patients(patient_id),
    doc_type VARCHAR(20),     -- 'transcript' or 'history'
    raw_path VARCHAR(255),    -- Pointer to raw file
    processed_path VARCHAR(255),
    checksum VARCHAR(64),     -- File integrity check
    version INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    encryption_status BOOLEAN DEFAULT FALSE
);

-- Vector Chunks Table
CREATE TABLE vector_chunks (
    chunk_id UUID PRIMARY KEY,
    doc_id UUID REFERENCES documents(doc_id),
    vector_path VARCHAR(255), # Path in vector DB
    start_offset INTEGER,     # Character position
    end_offset INTEGER,
    embedding_model VARCHAR(50),  # e.g., 'text-embedding-3-small'
    created_at TIMESTAMPTZ DEFAULT NOW()
);