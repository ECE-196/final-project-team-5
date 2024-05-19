import express from 'express'; 
import bodyParser from 'body-parser';  
import mqtt from 'mqtt';
import { DataBase } from './module.js'; 
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { createRequire } from 'module';

// Create a require function to load CommonJS modules
const require = createRequire(import.meta.url);

// Get the directory path of the current script
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Use __dirname to construct the absolute path to the HTML file
const htmlFilePath = join(__dirname, 'dummy.html');

const app = express(); 
const PORT = 5000;

app.use(express.static(join(__dirname, 'public')));


//------------------------------------------ RESTFUL API ---------------------------------------------//

app.use(bodyParser.json());  

app.get('/', (req,res)=>{  
    const theDatabase=new DataBase('example.db'); 
    theDatabase.manageDB((db)=>{ 
        db.each("SELECT * FROM Risk_Table ORDER BY id DESC LIMIT 1", (err, row) => {
            if (err)    console.error('Error:', err);
            else { 
                res.json({ 
                    'risk_lvl_text':row.risk_lvl_text, 
                    'risk_lvl':row.risk_lvl,
                    'risk_lvl_timestamp':row.risk_lvl_timestamp,
                    'machine_id':row.machine_id
                }) 
                console.log(`ID: ${row.id}, risk_lvl_text: ${row.risk_lvl_text}, risk_lvl: ${row.risk_lvl}, risk_lvl_timestamp${row.risk_lvl_timestamp}, Machine ID: ${row.machine_id} `); 
            }       
        }); 
    });
});

app.get('/dummy', (req, res) => {
    res.sendFile(htmlFilePath);
  });

//------------------------------------------ MQTT CODE ---------------------------------------------//

var options = {
    host: 'a98bdda5eadc4d9db9ad2f32aceb4ae4.s1.eu.hivemq.cloud',
    port: 8883,
    protocol: 'mqtts',
    username: 'hivemq.webclient.1714355997131',
    password: 'D:k.0tg9@a53bJCB!uMO'
}

const topic = 'test/topic';
var client = mqtt.connect(options); // Public test broker


client.on('connect', () => {
    console.log('Connected to MQTT broker');
    client.subscribe(topic, (err) => {
        if (!err)   console.log(`Subscribed to topic: ${topic}`);
        else        console.error('Subscription error:', err);    
    });
});

client.on('error', (err) => {
    console.error('MQTT Connection Error:', err);
});

client.on('message', (topic, message) => {
    console.log(`Received message on topic "${topic}": ${message.toString()}`); 
    var theDict = JSON.parse(message);
    const theDatabase = new DataBase('example.db'); 

    theDatabase.manageDB((db)=>{ 
        db.run(`INSERT INTO Risk_Table (risk_lvl_text, risk_lvl, risk_lvl_timestamp, machine_id) VALUES ("${theDict['risk_lvl_text']}", ${theDict['risk_lvl']},${(Math.floor(Date.now() / 1000)).toString()} , 1)`, (err) => {
            if(err) console.error('Error inserting data:', err);
            else    console.log('Data inserted successfully');
        });
    });
    
});

app.listen(PORT, ()=>{console.log( `Server running on port: http://localhost:${PORT}`)});

