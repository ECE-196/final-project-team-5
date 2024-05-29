document.addEventListener("DOMContentLoaded", () => { 
    
    var riskDiv = document.getElementById("risk_id");  
    var errorDiv = document.getElementById("error_bar"); 
    var scrapeButton = document.getElementById("scrape_pd_data_button");
    var updateDataButton = document.getElementById("update_pd_data_button");

    function disable_button(button){
        button.disabled=true;
        button.style.opacity = '0.5'; // You can adjust the opacity value as needed
        button.style.cursor = 'not-allowed';
    } 
    function enable_button(button){
        button.disabled=false;
        button.style.opacity = '1'; // You can adjust the opacity value as needed
        button.style.cursor = 'pointer'; // Change cursor to indicate that the button is disabled
    }
    function button_fetch(errorDiv, button, route){ 
        errorDiv.innerHTML="Waiting for response, hold tight."; 
        disable_button(button);
        fetch(route).then(response=>response.json()) 
        .then(function(response) { 
            if (response.output=="BAD_ERROR") errorDiv.innerHTML="Error Running Python Script";
            else if(response.output=="BAD_STDERR") errorDiv.innerHTML="Error Running Python Script";
            else if (response.output=="SUCCESS") errorDiv.innerHTML="Success! Script Uploaded";
            enable_button(button);
            console.log("command complete")
        });
    }
    scrapeButton.addEventListener("click",()=>{  
        errorDiv.innerHTML="Waiting for response, hold tight."; 
        button_fetch(errorDiv,scrapeButton,'/update_pdfs');
    })

    updateDataButton.addEventListener("click",()=>{  
        errorDiv.innerHTML="Waiting for response, hold tight."; 
        button_fetch(errorDiv,updateDataButton,'/update_pd_data');
    })

    setInterval(()=>{ 
        fetch('/recent/Geisel_Library').then(response=>response.json()) 
            .then(function(response) {    
                const theDate=new Date() 
                var theHours=theDate.getHours()%12; 
                var theAMPM='AM'; 
                if(theHours==0)theHours= 12; 
                if((theDate.getHours()/12)>=1) theAMPM='PM';
                riskDiv.innerHTML=`${response.risk_lvl_text} at ${theHours}:${theDate.getMinutes()}:${theDate.getSeconds()}${theAMPM} at ${response.location}`; 
            });
    },1000);  


});