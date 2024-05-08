import sqlite3 from 'sqlite3'

const db = new sqlite3.Database('example.db', (err) => {
    if (err) {
        console.error('Error opening database:', err);
    } else {
        console.log('Database opened successfully');
    }
});

db.serialize(() => { 
    db.run("CREATE TABLE IF NOT EXISTS FaceCounts (id INTEGER AUTO INCREMENT PRIMARY KEY, face_count TEXT, face_count_timestamp TIMESTAMP, machine_id INTEGER)");
});

db.close((err) => {
    if (err) {
        console.error('Error closing the database:', err);
    } else {
        console.log('Database closed successfully');
    }
});