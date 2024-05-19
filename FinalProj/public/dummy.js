document.addEventListener("DOMContentLoaded", () => { 
    
    var riskDiv=document.getElementById("risk_id"); 

    setInterval(()=>{ 
        fetch('/').then(response=>response.json()) 
            .then(function(response) {    
                const theDate=new Date() 
                var theHours=theDate.getHours()%12; 
                var theAMPM='AM'; 
                if(theHours==0)theHours= 12; 
                if((theDate.getHours()/12)>=1) theAMPM='PM';
                riskDiv.innerHTML=`${response.risk_lvl_text} at ${theHours}:${theDate.getMinutes()}:${theDate.getSeconds()}${theAMPM}`; 
            });
    },1000);
    


});