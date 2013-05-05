
##### Examine user traces #####
# "facebook"
# "gmailgchat"
# "gcalgdocs"
# "websearch"
# "irc"
# "bittorrent"

tracefile = 'in/traces.pickle'
tracename = 'bittorrent'

#streams =   get_user_model(start_time, end_time, 'in/traces.pickle', tracename)

f = open(tracefile)
obj = pickle.load(f)
f.close()

streams = obj.trace[tracename]

# ips and ports
ips = set()
ports = set()
for stream in streams:
    ips.add(stream[1])
    ports.add(stream[2])
    
# streams to .exit
exit_ip_streams = []
for stream in streams:
    if ('.exit' in stream[1]):
        exit_ip_streams.append(stream)

# ips to .exit
exit_ips = []
for ip in ips:
    if ('.exit' in ip):
        exit_ips.append(ip)
        
# streams to 9001
or_port_streams = []
for stream in streams:
    if (9001 == stream[2]):
        or_port_streams.append(stream)
# streams to 9001 but not to a .exit
or_port_nonexit_streams = []
for stream in streams:
    if (9001 == stream[2]) and\
        ('.exit' not in stream[1]):
        or_port_nonexit_streams.append(stream)
        
# print streams
for stream in streams:
    print('[{0:.1f}]\t{1}:{2}'.format(stream[0], stream[1], stream[2]))

# remove streams that duplicate an ip/24:port seen 10 minutes ago
max_circuit_dirtiness = 10*60
cover_time = float(max_circuit_dirtiness)/2
ip_port_seen = {}
streams_reduced = []
for stream in streams:
    ip_split = stream[1].split('.')
    ip_24 = '.'.join(ip_split[0:3])
    ip_port = ip_24 + ':' + str(stream[2])
    if (ip_port in ip_port_seen) and\
        (stream[0] - ip_port_seen[ip_port] < cover_time):
        continue
    else:
        ip_port_seen[ip_port] = stream[0]
        streams_reduced.append(stream)

### Results ###
#start_time: 1330646400
#end_time: 1335830399

#facebook
# num streams 3/12-4/12: 107081=1755.4/day
# num streams reduced (5 min. window, /24): 47
# num streams in trace: 637
# num streams to .exit: 4
# num streams to 9001 but not .exit: 0
# ips
  # num: 91
  # num w/ .exit: 4
# ports
  # num: 3
  # [80, 9001, 443]
  # to non-exit: [80, 443]
  
#gmailgchat
# num streams in trace: 516
# num streams to .exit: 0
# num streams reduced (5 min. window, /24): 40
# ips
    # num: 70
# ports
  # num: 2
  # [80, 443]
  
#gcalgdocs
# num streams in trace: 370
# num streams to .exit: 0
# num streams reduced (5 min. window, /24): 17
# ips
    # num: 42
# ports
  # num: 2
  # [80, 443]  
  
#websearch
# num streams in trace: 1343
# num streams to .exit: 0
# num streams reduced (5 min. window, /24): 138
# ips
    # num: 170
# ports
  # num: 2
  # [80, 443] 
  
#irc
# num streams in trace: 1
# num streams to .exit: 0
# ips
    # num: 1
# ports
  # num: 1
  # [6697]  
     
#bittorrent
# num streams in trace: 355
# num streams to .exit: 4
# num streams to 9001 but not .exit: 0
# num streams reduced (5 min. window, /24): 321
# ips
    # num: 285
# ports
  # num: 164  
  
  
# Model streams / week
# simple: 1008
# irc: 1 * 27 * 5 = 135
# fb: 47*4*5 = 940
# websearch: 138*4*5 = 2760
# bittorrent: 321*18*7 = 40446
#  OR 321*18*2 = 11556  
# typical (fb*7+gmail*7+gcalgdocs*7+websearch*14) = 7(47 + 40 + 17 + 2*138) = 2660
###### 

##### Finding and plotting the probabilities of compromise for the
# bandwidth-allocation experiments.
import pathsim_analysis
import os

# guard bw : exit bw
#1:1                                                      
#5:1                                    
#10:1                                    
#50:1                                   
guard_bws = [52428800, 69905067, 87381333, 95325091, 102801568]
exit_bws = [52428800, 34952533, 17476267, 9532509, 2056031]

# using regression from 3-month consensuses (1/13-3/13)
# guard_cons_bws = [171394, 229755, 288115, 314643, 339610]
# exit_cons_bws = [238205, 157244, 76282, 39481, 4845]
# date_range = '2013-01--03'

# using regression from 6-month consensuses (10/12-3/13)
guard_cons_bws = [266016, 357064, 448112, 489497, 528558]
exit_cons_bws = [256368, 169200, 82033, 42411, 5120]
date_range = '2012-10--2013-03'

guard_compromise_probs = []
exit_compromise_probs = []
guard_exit_compromise_probs = []
for guard_cons_bw, exit_cons_bw in zip(guard_cons_bws, exit_cons_bws):
    in_dir = 'out/analyze/typical.' + date_range + '.' + str(guard_cons_bw) +\
        '-' + str(exit_cons_bw) + '-0-adv/data/'
    print('Calculating compromise probs for {0}'.format(in_dir))
    pathnames = []
    for dirpath, dirnames, fnames in os.walk(in_dir):
        for fname in fnames:
            pathnames.append(os.path.join(dirpath,fname))
    pathnames.sort()
    (guard_comp_prob, exit_comp_prob, guard_exit_comp_prob) =\
        pathsim_analysis.compromised_set_get_compromise_probs(pathnames)
    guard_compromise_probs.append(guard_comp_prob)
    exit_compromise_probs.append(exit_comp_prob)
    guard_exit_compromise_probs.append(guard_exit_comp_prob)
    
# Output for 1/13 - 3/13
#>>> guard_compromise_probs
#[0.3759, 0.46332, 0.54293, 0.57084, 0.59832]
#>>> exit_compromise_probs
#[1.0, 1.0, 1.0, 1.0, 0.78898]
#>>> guard_exit_compromise_probs
#[0.37018, 0.45306, 0.51329, 0.48526, 0.14866]

# Output for 10/12 - 3/13
#>>> guard_compromise_probs
#[0.72073, 0.81337, 0.8724, 0.89328, 0.91033]
#>>> exit_compromise_probs
#[1.0, 1.0, 1.0, 1.0, 0.967]
#>>> guard_exit_compromise_probs
#[0.71705, 0.8086, 0.85816, 0.84255, 0.36203]


guard_compromise_rates = []
exit_compromise_rates = []
guard_exit_compromise_rates = []
for guard_cons_bw, exit_cons_bw in zip(guard_cons_bws, exit_cons_bws):
    in_dir = 'out/analyze/typical.' + date_range + '.' + str(guard_cons_bw) +\
        '-' + str(exit_cons_bw) + '-0-adv/data/'
    print('Calculating compromise rates for {0}'.format(in_dir))
    pathnames = []
    for dirpath, dirnames, fnames in os.walk(in_dir):
        for fname in fnames:
            pathnames.append(os.path.join(dirpath,fname))
    pathnames.sort()
    (guard_comp_rate, exit_comp_rate, guard_exit_comp_rate) =\
        pathsim_analysis.compromised_set_get_compromise_rates(pathnames)
    guard_compromise_rates.append(guard_comp_rate)
    exit_compromise_rates.append(exit_comp_rate)
    guard_exit_compromise_rates.append(guard_exit_comp_rate)

# Output for 10/12 - 3/13
#>>> guard_compromise_rates
#[0.08862985766892682, 0.11062274842179097, 0.12933955561725508, 0.1376146406651859, 0.1444471478255787]
#>>> exit_compromise_rates
#[0.06573084390343699, 0.044700403904606036, 0.022366468757306524, 0.011749066080196399, 0.0014427535363572598]
#>>> guard_exit_compromise_rates
#[0.005790726999064765, 0.004911905395136778, 0.00288130231470657, 0.0016003154956745382, 0.00020887114215571663]



# Plot output
import numpy
import matplotlib
matplotlib.use('PDF')
import matplotlib.pyplot
fig = matplotlib.pyplot.figure()

# fraction of bandwidth allocated to guard
x = [1.0/2.0, 2.0/3.0, 5.0/6.0, 10.0/11.0, 50.0/51.0]
matplotlib.pyplot.plot(x, guard_exit_compromise_probs, '-v',
    label = 'Prob. of guard & exit compromise', linewidth = 2,
    markersize = 8)
matplotlib.pyplot.plot(x, guard_compromise_probs, '-o',
    label = 'Prob. of guard compromise', linewidth = 2,
    markersize = 8)
matplotlib.pyplot.plot(x, exit_compromise_probs, '-s',
    label = 'Prob. of exit compromise', linewidth = 2,
    markersize = 8)
#guard_compromise_rates = []
#exit_compromise_rates = []
#guard_exit_compromise_rates = []
matplotlib.pyplot.plot(x, guard_compromise_rates, '-*',
    label = 'Avg. guard compromise rate', linewidth = 2,
    markersize = 8)
matplotlib.pyplot.plot(x, exit_compromise_rates, '-x',
    label = 'Avg. exit compromise rate', linewidth = 2,
    markersize = 8)
matplotlib.pyplot.legend(loc='center left')
matplotlib.pyplot.ylim(ymin=0.0)
matplotlib.pyplot.yticks(numpy.arange(0, 1.1, 0.1))
matplotlib.pyplot.xlabel('Fraction of 100MiBps total bandwidth allocated to guard')
matplotlib.pyplot.ylabel('Probability')
matplotlib.pyplot.title('Compromise probability and rates, 10/12 - 3/13')

# output
matplotlib.pyplot.savefig('out/analyze/vary_allocation.2012-10--2013-03/vary_allocation.2013-01--03.compromise_probs_rates.pdf')

##### Working out parallelization of network analysis #####
import os
import math
import multiprocessing
import cPickle as pickle
def get_num_relays(ns_file):
    with open(ns_file, 'r') as nsf:
        consensus = pickle.load(nsf)
        descriptors = pickle.load(nsf)
    num_relays = 0    
    for relay in consensus.routers:
        if (relay in descriptors):
            num_relays += 1
    return num_relays


base_dir = '/mnt/ram/'
in_dir = base_dir + 'out/network-state/fat/network-state-2013-01'

network_state_files = []
for dirpath, dirnames, filenames in os.walk(in_dir, followlinks=True):
    for filename in filenames:
        if (filename[0] != '.'):
            network_state_files.append(os.path.join(dirpath,filename))

num_processors = 20
chunksize = int(math.floor(float(len(network_state_files)) / num_processors))
pool = multiprocessing.Pool(num_processors)
nums = pool.map(get_num_relays, network_state_files, chunksize)
pool.close()
print('max relays: {0}'.format(max(nums)))
print('min relays: {1}'.format(min(nums)))
print('tot num relays: {2}'.format(sum(nums)))
##########

##### Create graphs with lines from multiple experiments #####
# varying user models
out_dir = 'out/analyze/user_models.2013-01--03'
out_name = 'user-models.2013-01--03.288115-76282-0-adv'
in_dirs = ['out/analyze/typical.2013-01--03.288115-76282-0-adv/data',
    'out/analyze/bittorrent.2013-01--03.288115-76282-0-adv/data',
    'out/analyze/irc.2013-01--03.288115-76282-0-adv/data']
line_labels = ['typical', 'bittorent', 'irc']
pathnames_list = []
for in_dir in in_dirs:
    pathnames = []
    for dirpath, dirnames, filenames in os.walk(in_dir, followlinks=True):
        for filename in filenames:
            if (filename[0] != '.'):
                pathnames.append(os.path.join(dirpath,filename))
    pathnames_list.append(pathnames)
pathsim_plot.compromised_set_plot(pathnames_list, line_labels, out_dir, out_name)

# varying total bandwidth
# 	200: 174762666.0 / 34952533; 579920 / 157244
#	100: 87381333 / 17476266; 288115 / 76282
#	50: 43690666 / 8738133; 142213 / 35801
#	25: 21845333 / 4369066; 69262 / 15560
#	10: 8738133 / 1747626; 25492 / 3416
out_dir = 'out/analyze/total_bandwidth.2013-01--03'
out_name = 'total-bandwidth.2013-01--03'
in_dirs = ['out/analyze/typical.2013-01--03.579920-157244-0-adv/data',
    'out/analyze/typical.2013-01--03.288115-76282-0-adv/data',
    'out/analyze/typical.2013-01--03.142213-35801-0-adv/data',
    'out/analyze/typical.2013-01--03.69262-15560-0-adv/data',
    'out/analyze/typical.2013-01--03.25492-3416-0-adv/data']
line_labels = ['200 MBps', '100 MBps', '50 MBps', '25 MBps', '10 MBps']
pathnames_list = []
for in_dir in in_dirs:
    pathnames = []
    for dirpath, dirnames, filenames in os.walk(in_dir, followlinks=True):
        for filename in filenames:
            if (filename[0] != '.'):
                pathnames.append(os.path.join(dirpath,filename))
    pathnames_list.append(pathnames)
pathsim_plot.compromised_set_plot(pathnames_list, line_labels, out_dir, out_name)

##########

##### Getting all destination IPs from any trace #####
from models import *
tracefilename = 'in/users2-processed.traces.pickle'
ut = UserTraces.from_pickle(tracefilename)

trace_dest_ips = {}
for tracename in ["facebook", "gmailgchat", "gcalgdocs", "websearch", "irc",
    "bittorrent"]:
    trace_dest_ips[tracename] = set()    
    for seconds, ip, port in ut.trace[tracename]:
        trace_dest_ips[tracename].add(ip)
trace_dest_ips['typical'] = set()
for tracename in ["facebook", "gmailgchat", "gcalgdocs", "websearch"]:
    trace_dest_ips['typical'].update(trace_dest_ips[tracename])

for tracename in ['typical', 'irc', 'bittorrent']:
    out_file = '{0}_dest_ips.txt'.format(tracename)
    with open(out_file, 'w') as f:
        for ip in trace_dest_ips[tracename]:
            f.write('{0}\n'.format(ip))