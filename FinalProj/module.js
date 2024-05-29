import sqlite3 from 'sqlite3'

export function DataBase(aDbName){ 
    sqlite3.verbose()

    this.dbName = aDbName; 
    
    this.manageDB=function(callback, ...args ){
        const db = new sqlite3.Database(this.dbName, (err) => {
            if (err)  console.error('Error opening database:', err);
            else console.log('Database opened successfully');
        });

        db.serialize(() => { 
           callback(db, ...args);
        });

        db.close((err) => {
            if (err)console.error('Error closing the database:', err);
            else console.log('Database closed successfully');
        }); 
    } 
}

