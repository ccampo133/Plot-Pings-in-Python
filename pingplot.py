import datetime
import os
import re
import sys
import time
from optparse import OptionParser

import numpy as np

# software version
__version__ = "1.1.0"

ping_flag = 'n'
if sys.platform != 'win32':
    ping_flag = 'c'


# ping
def pinger(host, n):
    """Executes the PCs ping command"""
    if sys.platform != 'win32':
        proc = os.popen(f"ping -{ping_flag} {n} {host}")
    else:
        proc = os.popen(f"chcp 437 & ping -{ping_flag} {n} {host}")
    result = ''.join(proc.readlines())
    proc.close()
    return result


# wrapper for ping
def call_pinger(host, n, ping, loss, t):
    """Calls the pinger function and returns results as arrays"""
    out = pinger(host, n)
    try:
        if sys.platform == 'win32':
            loss_idx = float(re.search("\d+(?=% loss)", out).group(0))
            ping_idx = float(re.search("(?<=Average =) \d+", out).group(0))
        else:
            # the next two lines assume this format:
            # 4 packets transmitted, 4 received, 0% packet loss, time 3002ms
            # rtt min/avg/max/mdev = 24.146/63.155/128.436/42.823 ms
            loss_idx = float(re.search("\d+\.\d+(?=% packet loss)", out).group(0))
            ping_idx = float(out.split('/')[-3])
    except:
        ping_idx = np.nan  # bad connection
        loss_idx = 100.

    # append data
    ping = np.append(ping, ping_idx)
    loss = np.append(loss, loss_idx)
    t = np.append(t, time.time())
    return ping, loss, t, out


# writes out to the log file
def write_log(log_file, log_body):
    """Writes results to a log file"""
    log_file.write(f"TIME: {datetime.datetime.now().ctime()}\n{log_body}\n\n")


# produces ping vs time plot
def plot_gen(ping, now, nans, host, interactive=False, size="1280x640"):
    """Generates ping vs time plot"""
    if not interactive:
        import matplotlib
        matplotlib.use("Agg")  # no need to load gui toolkit, can run headless
    import matplotlib.pyplot as plt

    size = [int(dim) for dim in size.split('x')]
    datestr = now[0].ctime().split()
    datestr = datestr[0] + " " + datestr[1] + " " + datestr[2] + " " + datestr[-1]
    plt.figure(figsize=(size[0] / 80., size[1] / 80.))  # dpi is 80
    plt.plot(now[~nans], ping[~nans], drawstyle='steps')
    plt.title(f"Ping Results for {host}")
    plt.ylabel("Latency [ms]")
    plt.xlabel(f"Time, {datestr} [GMT-{time.timezone // 3600}]")
    plt.xticks(size=10)
    plt.yticks(size=10)
    plt.ylim(ping[~nans].min() - 5, ping[~nans].max() + 5)

    # plot packet losses
    start = []
    finish = []
    for i in range(len(nans)):
        if nans[i]:
            if i == 0 or nans[i] != nans[i - 1]:
                start.append(i)
            if i == len(nans) - 1 or nans[i + 1] != nans[i]:
                finish.append(i)

    # add the red bars for bad pings
    for i in range(len(start)):
        plt.axvspan(now[start[i]], now[finish[i]], color='red')
    return plt


# main
def main(argv=None):
    # for interactive mode
    if not argv:
        argv = sys.argv[1:]

    # handle cmd line arguments
    parser = OptionParser()
    parser.add_option("-p", "--plot", dest="plot", action="store_true",
                      help="generates plot after data collection is finished")
    parser.add_option("-f", "--file", dest="fsave", action="store_true",
                      help="save plot to file in the current directory")
    parser.add_option("-H", "--host", dest="host", default="google.com",
                      help="the url or ip address to ping [default: %default]")
    parser.add_option("-n", "--num", dest="n", default=1, type="int",
                      help="the number of packets to send on each ping iteration [default: %default]")
    parser.add_option("-t", "--dt", dest="dt", default=0.5, type="float",
                      help="the time interval (seconds) in which successive pings are sent [default: %default s]")
    parser.add_option("-l", "--log", dest="log", action="store_true",
                      help="save a log file of the event in the current directory")
    parser.add_option("-s", "--size", dest="size", default="1280x640",
                      help="If plotting/saving a plot, this is the plot's dimensions" \
                           "in pixels (at 80 DPI) in the format XxY [default: 1280x640]")

    # unpack and initialize data
    opts, args = parser.parse_args(argv)
    ping = np.array([])
    loss = np.array([])
    t = np.array([])
    now = np.array([])
    cnt = 0

    # write log if specified
    if opts.log or opts.fsave:
        now_time = datetime.datetime.now()
        date_str = now_time.isoformat()[:-7][:10]
        time_str = f"{now_time.hour}h{now_time.minute}m{now_time.second}s"
        stamp = date_str + "_" + time_str
        log_name = f"pingplot_v{__version__}_{opts.host}_{stamp}.log"
        plot_name = f"pingplot_v{__version__}_{opts.host}_{stamp}.png"
        if opts.log:
            log_file = open(log_name, 'w')
            log_file.write(f"PingPlot Version {__version__} - Log File\n\n\n")

    # start the main loop
    print(f"PingPlot Version {__version__} -- by ccampo\n")
    print("{0:^23}\n=======================".format("Run Parameters"))
    print("{0:>17} {1}".format("Hostname:", opts.host))
    print("{0:>17} {1}".format("Ping interval:", str(opts.dt) + " s"))
    print("{0:>17} {1}".format("Packets per ping:", opts.n))
    print("\n\nPress CTRL+C to quit...\n")
    print("{0:^15} {1:^15} {2:^15} {3:^15} {4:^15}\n".format("AVG. PING", "PACKET LOSS", "NUM. PINGS", "NUM. TIMEOUTS",
                                                             "TIME ELAPSED"))

    while True:
        # quit on ctrl+c
        try:
            ping, loss, t, out = call_pinger(opts.host, opts.n, ping, loss, t)
            now = np.append(now, datetime.datetime.now())
            cnt += 1

            # get ping data
            mean_loss = loss.mean()
            nans = np.isnan(ping)
            if len(ping[~nans]) > 0:
                mean_ping = ping[~np.isnan(ping)].mean()
            else:
                mean_ping = np.nan

            if opts.log:
                write_log(log_file, out)

            # only ping after time dt
            time.sleep(opts.dt)

            delta_t = datetime.timedelta(seconds=(round(time.time() - t[0], 0)))
            sys.stdout.write("\r{0:^15.8} {1:^15.10} {2:^15} {3:^15} {4:^15}".format(str(round(mean_ping, 2)) + " ms",
                                                                                     str(round(mean_loss, 2)) + " %",
                                                                                     cnt * opts.n, len(ping[nans]),
                                                                                     str(delta_t)))
            sys.stdout.flush()
        except KeyboardInterrupt:
            break

    print("\n")

    # close log file
    if opts.log:
        print(f"Saved log file {log_name}")
        log_file.close()

    # make plot to save
    if opts.fsave or opts.plot:
        # check if any data was collected
        if len(ping[~nans]) == 0:
            print("Error: cannot generate plot; no data collected. Please check your connection.")
            return 2
        plt = plot_gen(ping, now, nans, opts.host, opts.plot, opts.size)

        # save if applicable
        if opts.fsave:
            print(f"Saved plot {plot_name}")
            plt.savefig(plot_name)

        # show plot if specified
        if opts.plot:
            plt.show()

    return 2  # exit


if __name__ == "__main__":
    sys.exit(main())
