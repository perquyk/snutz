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
        
def speedtest_test():
    """
    Runs a speedtest to measure internet speed
    Returns: dict w/ result
    """
    
    print("Running speedtest..")
    
    try:
        import speedtest
        
        # Create speedtest object
        st = speedtest.Speedtest()
        
        # Find best server
        print("Finding best server..")
        st.get_best_server()
        
        #Get server info
        server = st.results.server
        
        #test download speed
        print("Testing DOWNLOAD speed...")
        download_bps = st.download()
        download_mbps = download_bps / 1_000_000
        
        #Test upload speed
        print("Testing UPLOAD speed...")
        upload_bps = st.upload()
        upload_mbps = upload_bps / 1_000_000
        
        #Get Ping
        ping = st.results.ping
        
        return{
            "success": True,
            "download_mbps": round(download_mbps, 2),
            "upload_mbps": round(upload_mbps, 2),
            "ping_ms": round(ping, 2),
            "server_name": server.get("sponsor", "Unkown"),
            "server_location": f"{server.get('name', "Unknown")}, {server.get("country", "Unkown")}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
        