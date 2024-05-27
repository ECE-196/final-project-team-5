import datetime 
import statistics 
import numpy as np
def time_parser(time_string, truncate=False): 
    ''' 
    use .split() by "-" to split up the timestring 
    
    iterate through the timestring and convert to military time

    take the average regardless of how many entries 

    once thats done truncate the time and only leave the hour  

    then convert back to normal time and return the value
    '''  
    delimiter= "-" if "-" in time_string else "‐"
    time_string.replace(" ","")
    times=time_string.split(delimiter)  

    print(times)
    minutes=[]
    
    for time in times:  
        try: parsed_time = datetime.datetime.strptime(time.replace(" ",""), '%I:%M%p')
        except: return np.nan
        minutes.append(parsed_time.hour * 60 + parsed_time.minute) 
    
    average_minutes=int(statistics.mean(minutes)) 

    hours, minutes = divmod(average_minutes, 60)

    time_obj = datetime.datetime(1, 1, 1, hours, minutes) if truncate == False else datetime.datetime(1, 1, 1, hours, 0) 

    return time_obj.strftime('%I:%M%p')     


print(time_parser("11:50 PM ‐ 8:00 AM", True))