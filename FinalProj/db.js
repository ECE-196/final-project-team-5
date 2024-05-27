import { DataBase } from './module.js';

const theDatabase = new DataBase('example.db'); 

theDatabase.manageDB((db)=>{
    db.run("CREATE TABLE IF NOT EXISTS Risk_Table (id INTEGER AUTO INCREMENT PRIMARY KEY, risk_lvl_text VARCHAR(50), risk_lvl FLOAT, risk_lvl_timestamp TIMESTAMP, location VARCHAR(50))");
});

