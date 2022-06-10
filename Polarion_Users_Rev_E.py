#-------------------------------------------------------------------------------
# Name:        polarion_users
# Purpose:
#
# Author:      jeffc
#
# Created:     01/04/2019
# Copyright:   (c) jeffc 2019
# Licence:     <your licence>
#
# Revision notes:  This revision of the script writes to a html file and runs on
#                   Linux OS.
#-------------------------------------------------------------------------------
import os
import glob
import logging
import time
import datetime
import webbrowser

#  * * *  Subroutine Definitions  * * *

# --- Update User Array ---
#   This routine will chck the user array for a user.  If it exists
#   then it will exit the routine and if it doesn't then it will
#   insert it in the array.

def update_user_array(user_array, user_id):
    ret_cd = 0

    if not(user_id in user_array):
        user_array.insert(0, user_id)

    return ret_cd
# --- End Update User Array routine ---

def update_concurrent_array(ln, concurrent_array, c_hr, p_hr):
    ret_cd = 0

    use =  ln.index("concurrentALMUser")
    log_type = "stat"
    x = ln[use+26:]
    x_pos = x.index(',')
    no_of_users = x[0:x_pos]
    fmt_tm = tm[0:2]+":00"
    concur_info = [dt,fmt_tm,no_of_users]

    peak_use = get_peak_use(ln)

    if c_hr != p_hr:
        p_hr = c_hr
        concurrent_array.append(concur_info)

    return peak_use, c_hr, p_hr
# --- End Update Concurrent Array routine ---

# --- Get User Id ---
#
def get_peak_use(ln):
    peak_st_pos = ln.index("peak:") + 5
    temp_peak = ln[peak_st_pos:]
    peak_end_pos = temp_peak.index(",")
    peak_use = temp_peak[:peak_end_pos]

    return peak_use

# --- Get User Id ---
#
def get_user_id(ln, user_id):
    user_st_pos = ln.index("User ")+6
    temp_user = ln[user_st_pos:]
    user_end_pos = temp_user.index("'")
    user_id = temp_user[:user_end_pos]

    return user_id

# --- End Get User Id routine ---

# --- Setup Logging ---
# Set minimum log level to display in output file
int_loglevel = getattr(logging, 'DEBUG', None)
if int_loglevel is None:
    raise ValueError('Invalid log level specified: %s' % int_loglevel)

# Basic configuration for loggers
logging.basicConfig(
    filename=r'/home/polarion/scripts/logs/Polarion_Users_Rev_E.log',
    filemode='w',
    format='%(asctime)s [%(levelname)s] [%(name)s|%(funcName)s|%(lineno)d] %(message)s',
    datefmt='%m/%d/%Y %H:%M:%S',
    level=int_loglevel
    )
    # --- End Logging setup ---


# Variable initialization

log_path = '/opt/polarion/data/logs/main'
now = time.time()
yesterday = now - (60*60*24*2)
today_date = datetime.date.today()
display_dt = datetime.datetime.today().strftime('%Y-%m-%d')
concurrent_array = []
user_array = []
log_array = []
header = ("<p><tr><td>%s</td></tr>" % "Date") + ("<tr><td>%s</td></tr>" % "No. of Users") + ("<tr><td>%s</td></tr></p>" % "Users")
output_fname = r'/var/www/html/polarion_usage.htm'
prev_hr = 99
peak_use = 0

#  Main Routine
#
files = glob.glob(os.path.join(log_path,"log4j-licensing*"))
files.sort(key=os.path.getmtime)

for fn in files:
    if  os.path.getmtime(fn) > yesterday:
#        print fn, os.path.getmtime(fn), yesterday

#        testVar = raw_input("Hit <CR> to continue.")
        try:
            f = open(fn, 'r')
        except IOError:
            print('cannot open', fn)
        except:
            print('some undefined error for ', fn)
        else:
            contents = f.readlines()
            for ln in contents:
                dt = str(ln[0:10])
                tm = ln[11:19]
                hr = tm[0:2]

                if dt == str(datetime.date.today()):
                    if "logged in" in ln:
                        user_id = ''
                        user_id = get_user_id(ln, user_id)

                        if user_id:
                            ret_cd1=update_user_array(user_array, user_id)

                    elif "concurrentALMUser" in ln:
                        peak_use, hr, prev_hr= update_concurrent_array(ln, concurrent_array, hr, prev_hr)

            f.close()

pos = 0
cnt = 0
output_list = ""

if os.path.isfile(output_fname):
    fn = open(output_fname, 'ab')
else:
    fn = open(output_fname, 'wb')
    fn.write("<html>")
    fn.write("<head>")
    fn.write("<style>")
    fn.write("table, th, td {border: 1px solid black;}")
    fn.write("</style>")
    fn.write("</head>")
    fn.write("<p></p>")
    fn.write("<body>")
    fn.write("<h2>Polarion License Usage</h2>")
    fn.write("<p>Hourly license consumption throughout the day and users who had logged on that day.</p>")
    fn.write("<p></p>")

fn.write('<table style="width:100%">')
fn.write("  <tr>")
fn.write("    <th>Date</th>")
fn.write("    <th>Peak Usage</th>")
fn.write("    <th>Users</th>")
fn.write("  </tr>")

while pos < len(user_array):

    if user_array[pos] not in output_list:
        if cnt == 0:
            output_list = user_array[pos]
        else:
            output_list = output_list +", "+ user_array[pos]
        cnt += 1
    pos += 1

fn.write("  <tr>")
fn.write("    <th>" + display_dt + "</th>")
fn.write("    <th>" + str(peak_use) + "</th>")
fn.write("    <th>" + output_list + "</th>")
fn.write("  </tr>")
fn.write("<p></p>")
fn.write("<p></p>")

fn.write('<table style="width:100%">')
fn.write("  <tr>")
fn.write("    <th>Date</th>")
fn.write("    <th>Hour</th>")
fn.write("    <th>No. of Users</th>")
fn.write("  </tr>")

pos = 0
while pos < len(concurrent_array):
    fn.write("  <tr>")
    fn.write("    <th>" + concurrent_array[pos][0] + "</th>")
    fn.write("    <th>" + concurrent_array[pos][1] + "</th>")
    fn.write("    <th>" + concurrent_array[pos][2] + "</th>")
    fn.write("  </tr>")
    pos += 1

fn.write("</table>")
fn.write("</body>")
fn.write("</html>")

fn.close()
