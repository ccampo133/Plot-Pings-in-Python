import pingplot
import numpy as np
import datetime as dt
import re

filename = "example/example_logfile_macos_nix.log"
filename = "example/example_logfile_windows.log"

TIME_FORMAT = "%a %b %d %H:%M:%S %Y"
TIME_MARKER = "TIME:"
file_format = "windows"

ping = np.array([])
loss = np.array([])
t = np.array([])
hostname = ""


def extract_hostname(content, format):
    if format == "nix":
        return re.search("(?i)PING (.*) \(", content).group(1)
    return re.search("(?i)Pinging (.*) \[", content).group(1)


with open(filename) as file_in:
    # Skip the header lines
    line = file_in.readline()
    while not line.startswith(TIME_MARKER):
        line = file_in.readline()

    while line:
        if line.con
        if line.startswith(TIME_MARKER):
            cur_time = dt.datetime.strptime(line[6:].strip(), TIME_FORMAT)
            line = file_in.readline()
        else:
            out = []
            while line and not line.startswith(TIME_MARKER):
                out.append(line.strip())
                line = file_in.readline()
            raw_output = "\n".join(out)
            if not hostname:
                hostname = extract_hostname(raw_output, file_format)
            ping, loss, t = pingplot.extract_ping_data(raw_output, ping, loss, t, cur_time=cur_time)

nans = np.isnan(ping)

plt = pingplot.plot_gen(ping, t, nans, hostname)

plt.savefig("foo.png")

if __name__ == '__main__':
    print("Done")
