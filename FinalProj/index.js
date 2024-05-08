import express from 'express'; 
import bodyParser from 'body-parser';  
import mqtt from 'mqtt';
import sqlite3 from 'sqlite3'

sqlite3.verbose();

const app = express(); 
const PORT = 5000;

app.use(bodyParser.json());  

app.get('/', (req,res)=>{ 
    const db = new sqlite3.Database('example.db', (err) => {
        if (err) {
            console.error('Error opening database:', err);
        } else {
            console.log('Database opened successfully');
        }
    });
    db.serialize(() => { 
        db.each("SELECT * FROM FaceCounts", (err, row) => {
            if (err) {
            console.error('Error:', err);
            } else {
            console.log(`ID: ${row.id}, Face Count: ${row.face_count}, Face Count Timestamp: ${row.face_count_timestamp}, Machine ID: ${row.machine_id} `); 
            }
        });
    });
    db.close((err) => {
        if (err) {
            console.error('Error closing the database:', err);
        } else {
            console.log('Database closed successfully');
        }
    });

});



var options = {
    host: 'a98bdda5eadc4d9db9ad2f32aceb4ae4.s1.eu.hivemq.cloud',
    port: 8883,
    protocol: 'mqtts',
    username: 'hivemq.webclient.1714355997131',
    password: 'D:k.0tg9@a53bJCB!uMO'
}

var client = mqtt.connect(options); // Public test broker

const topic = 'test/topic';

client.on('connect', () => {
    console.log('Connected to MQTT broker');
    client.subscribe(topic, (err) => {
        if (!err) console.log(`Subscribed to topic: ${topic}`);
        else console.error('Subscription error:', err);    
    });
});

client.on('error', (err) => {
    console.error('MQTT Connection Error:', err);
});

client.on('message', (topic, message) => {
    console.log(`Received message on topic "${topic}": ${message.toString()}`);
    const db = new sqlite3.Database('example.db', (err) => {
        if (err) {
            console.error('Error opening database:', err);
        } else {
            console.log('Database opened successfully');
        }
    });
    db.serialize(() => { 
        db.run(`INSERT INTO FaceCounts (face_count, face_count_timestamp, machine_id) VALUES (${message.toString()},${(Math.floor(Date.now() / 1000)).toString()} , 1)`, (err) => {
            if (err) {
                console.error('Error inserting data:', err);
            } else {
                console.log('Data inserted successfully');
            }
        });
    });
    db.close((err) => {
        if (err) {
            console.error('Error closing the database:', err);
        } else {
            console.log('Database closed successfully');
        }
    });
});

app.listen(PORT, ()=>{console.log( `Server running on port: http://localhost:${PORT}`)});

