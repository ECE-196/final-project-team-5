import express from 'express'; 
import bodyParser from 'body-parser';  
import mqtt from 'mqtt'; 
import { DataBase } from './module.js'; 
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { createRequire } from 'module'; 
import { exec } from 'child_process';

// Create a require function to load CommonJS modules
const require = createRequire(import.meta.url);

// Get the directory path of the current script
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Use __dirname to construct the absolute path to the HTML file
const htmlFilePath = join(__dirname, 'dummy.html');  
const htmlFilePath2 = join(__dirname, 'website.html'); 
const htmlFilePath3 = join(__dirname, 'about.html'); 
const pythonScript1 = join(__dirname, '[V1.0]-Bike_Theft_Data_Analysis.py'); 
const pythonScript2 = join(__dirname, '[TEST]-Web_Scraper.py');

const app = express(); 
const PORT = 5000;

app.use(express.static(join(__dirname, 'public')));


//------------------------------------------ RESTFUL API ---------------------------------------------//

app.use(bodyParser.json());  

app.get('/recent/:location', (req,res)=>{  
    const theDatabase=new DataBase('example.db'); 
    theDatabase.manageDB((db)=>{ 
        db.each(`SELECT * FROM Risk_Table WHERE location="${req.params.location.replace(/_/g," ")}" ORDER BY id DESC LIMIT 1`, (err, row) => {
            if (err)    console.error('Error:', err);
            else { 
                res.json({ 
                    'risk_lvl_text':row.risk_lvl_text, 
                    'risk_lvl':row.risk_lvl,
                    'risk_lvl_timestamp':row.risk_lvl_timestamp,
                    'location':row.location
                }) 
                console.log(`ID: ${row.id}, risk_lvl_text: ${row.risk_lvl_text}, risk_lvl: ${row.risk_lvl}, risk_lvl_timestamp: ${row.risk_lvl_timestamp}, location: ${row.location} `); 
            }       
        }); 
    });
});

app.get(`/all/:location`, (req,res)=>{   
    const theDatabase=new DataBase('example.db'); 
    theDatabase.manageDB((db)=>{ 
        db.all(`SELECT * FROM Risk_Table WHERE location="${req.params.location.replace(/_/g," ")}" ORDER BY id DESC`, (err, rows) => {
            if (err)    console.error('Error:', err);
            else {    
                let json_array=[];
                rows.forEach((row)=>{ 
                    json_array.push({ 
                        'risk_lvl_text':row.risk_lvl_text, 
                        'risk_lvl':row.risk_lvl,
                        'risk_lvl_timestamp':row.risk_lvl_timestamp,
                        'location':row.location
                    });
                    console.log(`ID: ${row.id}, risk_lvl_text: ${row.risk_lvl_text}, risk_lvl: ${row.risk_lvl}, risk_lvl_timestamp: ${row.risk_lvl_timestamp}, location: ${row.location} `);  
                }); 
                res.json(json_array);
            }       
        }); 
    });
});

app.get(`/police_data_location`, (req,res)=>{   
    const theDatabase=new DataBase('police_data.db'); 
    theDatabase.manageDB((db)=>{ 
        db.all('SELECT location, COUNT(*) AS location_count FROM users GROUP BY location', (err, rows) => {
            if (err)    console.error('Error:', err);
            else {     
                let json_object={};
                rows.forEach((row)=>{  
                    //console.log(`row:${JSON.stringify(row)}`)
                    json_object [row.Location] =row.location_count
                    console.log(`location: ${row.location}, time_counts: ${row.location_count} `);  
                }); 
                res.json(json_object);
            }       
        }); 
    });
});

app.get(`/police_data_time`, (req,res)=>{   
    const theDatabase=new DataBase('police_data.db'); 
    theDatabase.manageDB((db)=>{ 
        db.all('SELECT "Time Occurred", COUNT(*) AS time_count FROM users GROUP BY "Time Occurred"', (err, rows) => {
            if (err)    console.error('Error:', err);
            else {     
                let json_object={};
                rows.forEach((row)=>{  
                    //console.log(`row:${JSON.stringify(row)}`)
                    json_object [row["Time Occurred"]] =row.time_count
                    console.log(`Time Occurred: ${row["Time Occurred"]}, time_counts: ${row.time_count} `);  
                }); 
                res.json(json_object);
            }       
        }); 
    });
});

app.get('/update_pd_data',(req, res)=>{  
    console.log(res);
    exec(`python ${pythonScript1}`,(error, stdout, stderr)=>{ 
        if(error){res.json({"output":"BAD_ERROR"})} 
        else if(stderr){res.json({"output":"BAD_STDERR"})} 
        else {res.json({"output":"SUCCESS"})};
    });
});

app.get('/update_pdfs',(req, res)=>{ 
    exec(`python ${pythonScript2}`,(error, stdout, stderr)=>{ 
        if(error){res.json({"output":"BAD_ERROR"})} 
        else if(stderr){res.json({"output":"BAD_STDERR"})} 
        else {res.json({"output":"SUCCESS"})}; 
    });
});  




app.get('/dummy', (req, res) => {
    res.sendFile(htmlFilePath);
  }); 

app.get('/main',(req, res)=>{ 
    res.sendFile(htmlFilePath2)
}); 

app.get('/about',(req, res)=>{ 
    res.sendFile(htmlFilePath3);
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
    var theDict  
    try{theDict = JSON.parse(message);}  
    catch(error){return;}
    const theDatabase = new DataBase('example.db'); 

    theDatabase.manageDB((db)=>{ 
        db.run(`INSERT INTO Risk_Table (risk_lvl_text, risk_lvl, risk_lvl_timestamp, location) VALUES ("${theDict['risk_lvl_text']}", ${theDict['risk_lvl']},${(Math.floor(Date.now() / 1000)).toString()} ,"${theDict['location']}" )`, (err) => {
            if(err) console.error('Error inserting data:', err);
            else    console.log('Data inserted successfully');
        });
    });
});

app.listen(PORT, ()=>{console.log( `Server running on port: http://localhost:${PORT}`)});

