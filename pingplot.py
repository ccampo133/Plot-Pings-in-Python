import numpy as np
import matplotlib
matplotlib.use("WXAgg")
import matplotlib.pyplot as plt

import os
import sys
import msvcrt
import time
import re
import datetime
from optparse import OptionParser

# software version
version = 1.0

# ping
def pinger(host, n):
    ''' Executes the PCs ping command. '''
    proc = os.popen("ping -n {0} {1}".format(n, host))
    lns  = proc.readlines()
    out  = ""
    for line in lns: out += line
    return out

# driver for ping
def call_pinger(host, n, ping, loss, t):
    ''' Calls the pinger function and returns results as arrays. '''
    out   = pinger(host, n)
    try:    
        lossi = float(re.search("\d+(?=% loss)", out).group(0))
        pingi = float(re.search("(?<=Average =) \d+", out).group(0))
    except:
        pingi = np.nan # bad connection
        lossi = 100.
    # append data
    ping = np.append(ping, pingi)
    loss = np.append(loss, lossi)
    t    = np.append(t, time.time())
    return ping, loss, t, out

# writes out to the log file
def write_log(logfile, outstr):
    ''' Writes results to a log file '''
    timestr = "TIME: {0}".format(datetime.datetime.now().ctime())
    logfile.write(timestr + outstr + "\n\n")
    return
    
# produces ping vs time plot
def plot_gen(ping, now, t, nans, host):
    datestr   = now[0].ctime().split()
    datestr   = datestr[0] + " " + datestr[1] + " " + datestr[2] + " " + datestr[-1]
    startdate = time.ctime(t[0])
    plt.figure(figsize=(25,8))
    plt.plot(now[~nans], ping[~nans], drawstyle='steps')
    plt.title("Ping Results for {0}".format(host))
    plt.ylabel("Latency [ms]")
    plt.xlabel("Time, {0} [GMT -{1} hrs]".format(datestr, time.timezone/3600))
    plt.xticks(size=10)
    plt.yticks(size=10)
    plt.ylim(ping[~nans].min()-5, ping[~nans].max()+5)
    
    # plot packet losses
    start  = []
    finish = []
    for i in range(len(nans)):
        if nans[i] == True:
            if i == 0:
                start.append(i)
            elif nans[i] != nans[i-1]:
                start.append(i)
            if i != len(nans) and nans[i+1] != nans[i]:
                finish.append(i)
                
    # add the red bars for bad pings
    for i in range(len(start)):
        plt.axvspan(now[start[i]], now[finish[i]+1], color='red')
    return
        
# main
def main(argv=None):
    # for interactive mode
    if not argv:
        argv = sys.argv[1:]
    
    # handle cmd line arguments
    parser = OptionParser()
    parser.add_option("-p", "--plot", dest="plot", action="store_true",
                      help="generates plot after data collection is finished")
    parser.add_option("-f", "--file", dest="fname", metavar="FILE", 
                      help="save plot to FILE")	  
    parser.add_option("-H", "--host", dest="host", default="google.com", 
                      help="the url or ip address to ping [default: %default]")
    parser.add_option("-n", "--num", dest="n", default=1, 
                      help="the number of packets to send on each ping iteration [default: %default]")
    parser.add_option("-t", "--dt", dest="dt", default=0.5, 
                      help="the time interval (seconds) in which successive pings are sent [default: %default s]")
    parser.add_option("-l", "--log", dest="log", action="store_true",
                      help="save a logfile of the event in the current directory.")
        
    # unpack and initialize data
    opts, args = parser.parse_args(argv)
    host = opts.host
    n    = opts.n
    dt   = opts.dt
    ping = np.array([])
    loss = np.array([])
    t    = np.array([])
    now  = np.array([])
    cnt  = 0
    
    # write log if specified
    if opts.log:
        # get timestamp
        nowtime = datetime.datetime.now()
        datestr = nowtime.isoformat()[:-7][:10]
        timestr = "{0}h{1}m{2}s".format(nowtime.hour, nowtime.minute, nowtime.second)
        stamp   = datestr + "_" + timestr
        logname = "pingplot_v{vers:0.1}_{0}_{1}.log".format(host, stamp, vers=version)  # remove all '.'
        logfile = file(logname, 'w')
        logfile.write("PingPlot Version {0:0.1} - Log File\n\n\n".format(version))
    
    # start the main loop
    print("PingPlot Version {0} -- by ccampo\n".format(version))
    print("{0:^23}\n=======================".format("Run Parameters"))
    print("{0:>17} {1}".format("Hostname:", host))
    print("{0:>17} {1}".format("Ping interval:", str(dt) + " s"))
    print("{0:>17} {1}".format("Packets per ping:", n))
    print("\n\nPress ESC to quit...\n")
    print("{0:^15} {1:^15} {2:^15} {3:^15} {4:^15}\n"
            .format(
            "AVG. PING", 
            "PACKET LOSS", 
            "NUM. PINGS", 
            "NUM. TIMEOUTS", 
            "TIME ELAPSED"
            ))
            
    while True:
        # quit on escape
        if msvcrt.kbhit() and ord(msvcrt.getch()) == 27: break	
            
        # ping and parse; print results
        ping, loss, t, out = call_pinger(host, n, ping, loss, t)
        now  = np.append(now, datetime.datetime.now())
        cnt += 1
        
        # get ping data
        mloss = loss.mean()
        nans  = np.isnan(ping)
        if len(ping[~nans]) > 0:
            mping = ping[~np.isnan(ping)].mean()
        else:
            mping = np.nan
        
        # write log if specified
        if opts.log:
            write_log(logfile, out)
        
        # only ping after time dt
        time.sleep(float(dt))
        
        # print results
        deltat = datetime.timedelta(seconds=(round(time.time() - t[0], 0)))
        sys.stdout.write("\r{0:^15.8} {1:^15.10} {2:^15} {3:^15} {4:^15}"
                        .format(
                        str(round(mping, 2))+" ms", 
                        str(round(mloss, 2))+" %",
                        cnt*n, 
                        len(ping[nans]), 
                        str(deltat)
                        ))
    
    print("\n")
    # close log file
    if opts.log:
        print("Saved log file %s" % logname)
        logfile.close()
        
    # make plot to save
    if opts.fname or opts.plot:
        # check if any data was collected
        if len(ping[~nans]) == 0:
            print("Error: cannot generate plot; no data collected. Please check your connection.")
            return 2
        else:
            plot_gen(ping, now, t, nans, host)
    
    # save if applicable
    if opts.fname:
        print("Saved plot %s" % opts.fname)
        plt.savefig(opts.fname)
    
    # show plot if specified
    if opts.plot:
        plt.show()
        
    return 2	# exit
        
if __name__ == "__main__":
    sys.exit(main())