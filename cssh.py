import applescript
import math
import argparse


#applescript example
'''
tell application "iTerm2"
    create window with profile "smaller"
        tell current session of current window
            split horizontally with profile "smaller"
            split horizontally with profile "smaller"
        end tell
        tell session 1 of current tab of current window
            split vertically with profile "smaller"
            split vertically with profile "smaller"
            split vertically with profile "smaller"
        end tell
        tell session 5 of current tab of current window
            split vertically with profile "smaller"
            split vertically with profile "smaller"
            split vertically with profile "smaller"
        end tell
        tell session 9 of current tab of current window
            split vertically with profile "smaller"
            split vertically with profile "smaller"
            split vertically with profile "smaller"
        end tell
        tell session 12 of current tab of current window
            close
        end tell
        set commands to { "ssh 10.191.102.11","ssh 10.191.102.12","ssh 10.191.102.13","ssh 10.191.102.14","ssh 10.191.102.15","ssh 10.191.102.16","ssh 10.191.102.17","ssh 10.191.102.18","ssh 10.191.102.19","ssh 10.191.102.20","ssh 10.191.102.21"}
        repeat with i from 1 to count of commands
            tell session i of current tab of current window
                write text (item i of commands)
            end tell
        end repeat
        tell application "System Events" to keystroke "I" using {shift down, command down}
end tell
'''


class ITERM2():
    def __init__(self):
        self.indent = ' '*4
        self.profile = 'Default'
        self.broacast = (self.indent*2) + 'tell application "System Events" to keystroke "I" using {shift down, command down}\n'
        self.split_part = []
        self.cmd_part = []


    def run(self, ips):
        self.split(ips)
        self.send_cmd(ips)
        run_start = 'tell application \"iTerm2\"\n'
        run_end = 'end tell\n'
        split_string = ''.join(self.split_part)
        cmd_string = ''.join(self.cmd_part) 
        ascript = run_start + split_string + cmd_string + self.broacast + run_end
        return ascript
        

    def split(self, ips):
        nnodes = len(ips)
        if nnodes > 10:
            self.profile = 'smaller'
        open_window = (self.indent*1) + 'create window with profile "%s"\n'%(self.profile)
        self.split_part.append(open_window)

        # Compute geometry
        nrows = round(math.sqrt(nnodes))
        ncols = math.ceil(nnodes/nrows)

        nrows = int(nrows)
        ncols = int(ncols)

        #nrows = max(nrows,2)
        #ncols = max(ncols,2)
        sum_nodes = nrows * ncols
        
        #part of split rows

        split_h = (self.indent*3) + 'split horizontally with profile "%s"\n'%(self.profile)
        rows_split = \
        (self.indent*2) + 'tell current session of current window\n' + \
        split_h * (nrows - 1) + \
        (self.indent*2) + 'end tell\n'
        self.split_part.append(rows_split)

        #part of split colums
        split_v = (self.indent*3) + 'split vertically with profile "%s"\n'%(self.profile)
        for i in range(0, nrows):
            cols_split = \
            (self.indent*2) + 'tell session %s of current tab of current window\n'%str(ncols * i + 1) + \
            split_v * (ncols - 1) + \
            (self.indent*2) + 'end tell\n'
            self.split_part.append(cols_split)

        #part of close redundant session

        for j in range(sum_nodes, 0, -1):
            if j <= nnodes:
                close_split = ''
            elif j > nnodes:
                close_split = \
                (self.indent*2) + 'tell session %s of current tab of current window\n'%(str(j)) + \
                (self.indent*3) + 'close\n' + \
                (self.indent*2) + 'end tell\n'
                self.split_part.append(close_split)

    def send_cmd(self, ips):
        #make ips list
        ips_list_start = (self.indent*2) + 'set commands to { '
        list_content = []
        for i, j in enumerate(ips):
            if i == len(ips)-1:
                content = '\"ssh %s\"'%(j.strip('\n'))
                list_content.append(content) 
            else:          
                content = '\"ssh %s\",'%(j.strip('\n'))
                list_content.append(content)
        ips_content = ''.join(list_content)
        ips_list_end = '}\n'
        ips_list = ips_list_start + ips_content + ips_list_end
        self.cmd_part.append(ips_list)

        #make cmd send
        cmd_send = \
'''        repeat with i from 1 to count of commands
            tell session i of current tab of current window
                write text (item i of commands)
            end tell
        end repeat
'''           
        self.cmd_part.append(cmd_send)

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--file', '-f', type=str, default='/Users/yohoc/i2_hosts', help="Cluster file (one hostname per line)")
parser.add_argument('--debug', '-d', default=False, help="switch on debug mode, print ascript.", action="store_true")
args = parser.parse_args()

def cluster_run(args):
    host_file = args.file
    with open(host_file, 'r') as fopen:
        ips = fopen.readlines()
    iterm_run = ITERM2()
    as_run = iterm_run.run(ips)
    if args.debug:
        print as_run
    scpt = applescript.AppleScript(as_run)
    scpt.run()

if __name__ == '__main__':
    cluster_run(args)
