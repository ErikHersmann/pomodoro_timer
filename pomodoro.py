import questionary, sys, os
from time import time_ns
from datetime import datetime, timedelta
from termcolor import cprint
style_1 = questionary.Style([('highlighted', 'fg:#FF00FF bold bg:#FFFFFF'), ('text', 'fg:#0000FF')])
LOG_PATH = "pom.log"
CONFIG_PATH = "pom.config"


def write_log(cycle_id, cycle_time):
    with open(LOG_PATH, "a") as f:
        f.write("\n")
        f.write(str(datetime.today()).split(".")[0].replace(" ", ",")+",")
        f.write(cycle_id +","+ cycle_time)
    return


def read_log(stats=False):
    """read out latest cycle id for today from log
    if arg is True also display some dashboard like view on data"""
    
    with open(LOG_PATH, "r") as f:
        lines = f.readlines()
    if str(datetime.today().date()) == lines[-1].split(",")[0]:
        cycle_id = int(lines[-1].split(",")[2])
    else:
        cycle_id = 0
        stats = True
    if stats:
        # also clean up log here
        previous_date = lines[0].split(",")[0]
        previous_cycle = lines[0].split(",")[2]
        previous_duration = 0
        week = {}
        for line in lines:
            cur_date, _, cur_cycle, cur_duration = line.split(",")

            if cur_date not in week.keys():
                week[cur_date] = {}


            if cur_cycle not in week[cur_date].keys():
                week[cur_date][cur_cycle] = 0


            if cur_date != previous_date:
                week[previous_date][previous_cycle] = previous_duration
                previous_date = cur_date


            elif cur_cycle != previous_cycle:
                week[cur_date][previous_cycle] = previous_duration
                previous_cycle = cur_cycle


            previous_duration = cur_duration.strip()
        week[cur_date][cur_cycle] = previous_duration

        cprint("Welcome the fuck back time to lock the fuck in unxdd", "light_blue")
        cprint("Summary of the last 7 days", "light_blue")
        # show nice graph of past week
        for date in week.keys():
            #print(datetime.strptime(date, '%Y-%m-%d'),"<", datetime.now() - timedelta(days=7))
            if datetime.strptime(date, '%Y-%m-%d') > datetime.now() - timedelta(days=7):
                cycle_count = max(int(x) for x in week[date].keys())
                total_time = sum(int(x) for x in week[date].values()) / (10**9)
                hours = int(total_time // 3600)
                if hours > 0: hours=str(hours) +"h "
                else: hours=""

                minutes = int((total_time % 3600) // 60)
                seconds = total_time % 60
                total_time = hours + str(minutes) +"m "  + str(seconds).split(".")[0] + "s"
                #print(week[date].values())
                #print(date, cycle_count, total_time)
                cprint(f"Date:{date:<10} {datetime.strptime(date, '%Y-%m-%d').strftime('%A'):<9} Total cycles:{cycle_count:<2} Total time:{total_time}", "magenta")

    return cycle_id


def format_timestamp(start):
    time = (time_ns()-start) / (10**9)
    minutes = int(time // 60)
    seconds = time % 60
    if minutes > 0:
        time_string = (str(minutes) + "m" + " " + str(seconds))
    else:
        time_string = str(seconds)
    return time_string[:9]



# on new day bootup display some cool message (like the stats from read_log or done time past days)
args = sys.argv
print()
match len(args):
    case 2:
        load_config = True
        config_id =  args[1]
    case _:
        load_config = questionary.confirm(default=True, style=style_1, auto_enter=True, message="Load config ?").ask()
        config_id = "not_numeric"
with open(CONFIG_PATH, "r") as f:
    if len(f.read()) < 5:
        load_config = False
        cprint("No configs available yet, creating a new one...","red")

if load_config:
    with open(CONFIG_PATH, "r") as f:
        configs = f.readlines()
        if config_id.isnumeric():
            # load the indexed config
            config = [int(x) for x in configs[int(config_id)].split(",")]
        else:
            # prompt user with config list
            config = [int(x) for x in questionary.select("", [x.replace(",", " ").strip() for x in configs], pointer="=>", style=style_1, instruction="").ask().split(" ")]

    auto_mode = bool(config[0])
    interval_length = config[1]
    break_length = config[2]


# config: auto_mode(0/1),interval,break
if not load_config:
    auto_mode = questionary.confirm(default=True, style=style_1, auto_enter=True, message="Automatically start cycles ?").ask()
    interval_length = questionary.select("interval length", ["25", "15", "20", "30", "35", "40", "50", "60"], pointer="=>", style=style_1).ask()
    break_length = questionary.select("break length", ["5", "0", "10", "15", "30", "45", "60"], pointer="=>", style=style_1).ask()
    # save config
    if questionary.confirm(default=True, style=style_1, auto_enter=True, message="Save configuration ?").ask():
        with open(CONFIG_PATH, "a") as f:
            f.write("\n"+",".join([str(int(auto_mode)), interval_length, break_length]))
    interval_length, break_length = [int(x) for x in [interval_length, break_length]]

cycle = read_log() + 1
quit = False



if auto_mode: cprint(f"Starting cycles automatically  Interval:{interval_length}  Break:{break_length}", "light_blue")
else: cprint(f"Starting cycles manually  Interval:{interval_length}  Break:{break_length}", "light_blue")
input("Ready ?")



while not quit:
    # cprint(f"New cycle started (cycle:{cycle})", "light_blue","on_white", attrs=["blink"])
    # main loop = 1 cycle
    # interval
    cycle_start = time_ns()
    intermediate_time = time_ns()
    while time_ns()-cycle_start < interval_length*60* 10**9:
        # log to file every _ seconds
        if time_ns()-intermediate_time > 49* 10**9:
            write_log(cycle_id=str(cycle), cycle_time=str(time_ns()-cycle_start))
            intermediate_time = time_ns()
        cprint(f"Cycle {cycle}: "+format_timestamp(cycle_start), end='\r', color="light_green")

    cprint(f"Cycle {cycle} finished in: "+ format_timestamp(cycle_start), color="light_green")
    write_log(cycle_id=str(cycle), cycle_time=str(interval_length*60* 10**9))


    # break
    break_start = time_ns()
    while time_ns()-break_start < break_length*60* 10**9:
        cprint(f"Break {cycle}: "+format_timestamp(break_start), end='\r', color="light_blue")

    cprint(f"Break {cycle} finished in: "+format_timestamp(break_start), color="light_blue")


    # exit loop here
    if not auto_mode:
        if questionary.confirm(default=True, style=style_1, auto_enter=True, message="Start next cycle ?").ask():
            quit = False
        else:
            print("Goodbye")
            quit = True
    cycle += 1
    cprint(f"New cycle started (cycle:{cycle})", "red", attrs=["bold"])