"""
test.py - Network Testing Functions

This file contains all the different network tests
"""

import subprocess
import platform

def ping_test(target:str, count: int=4):
    """
    Runs a ping test to a target
    
    Params:
    - target: What to ping (e.f. "google.com", "8.8.8.8")
    - count: how many pings to send (default 4)
    
    Returns: Dict w/ result
    """
    
    ## Different OS use different ping commands
    # Windows uses -n, Unix (linux/macos) use -c
    param = "-n" if platform.system().lower() == "windows" else "-c"

    #Build command
    command = ["ping", param, str(count), target]
    
    print(f"Running: {' '.join(command)}")
    
    try:
        #run ping command
        result = subprocess.run(
            command,
            capture_output=True,    # Capture the output
            text=True,              # Return as string (not bytes)
            timeout=30              # Max 30 Seconds
        )
        
        #Parse output to extract useful info
        output = result.stdout
        
        #check if successful
        success = result.returncode == 0
        
        #extract some stats
        if success:
            lines = output.split('\n')
            summary = lines[-3:] #last 3 lines usualy have the summary
        else:
            summary = ["Ping Failed"]
            
        return {
            "success": success,
            "target": target,
            "packets_sent": count,
            "output": output,
            "summary": summary
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "target": target,
            "error": "Ping timed out (30s)"
        }
    except Exception as e:
        return{
            "success": False,
            "target": target,
            "error": str(e)
        }