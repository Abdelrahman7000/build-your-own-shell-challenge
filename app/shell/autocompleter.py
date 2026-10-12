import os
import readline
import subprocess
import sys
AUTO_COMPLETE_COMMANDS=["exit","echo","cd","type"]
COMPLETE_DISPLAY_COMMANDS = {}

TAB_HITS=0
MATCHES_CACHE=[]

def longest_common_prefix(strs):
    if "" in strs:
            return ""
    elif len(strs)==1:
        return strs[0]
    else:
        e=list(zip(*strs))
        res=''
        for i in e:
            if len(set(i))==1:
                res+=i[0]
            else:
                break
        return res

def handle_command_completion(text,state):
    '''
    Args:
        text: str: the current argument being completed
        state: int: the current state of the completion (0 for the first match, 1 for the second match, etc.)
    '''
    matches = [cmd for cmd in AUTO_COMPLETE_COMMANDS if cmd.startswith(text)]
    if state < len(matches):
        return matches[state] + " "
    return None

def handle_path_completion(current_argument, state):
    '''
    Args:
        current_argument: str: the current argument being completed
        state: int: the current state of the completion (0 for the first match, 1 for the second match, etc.)
    '''
    directory_path=""
    # if the current argument contains a path. So we need to separate the directory path from the prefix being completed.
    if '/' in current_argument: 

        directory_path = current_argument.rsplit("/", 1)[0] + '/'
        file_prefix = current_argument.rsplit("/", 1)[1]
        matches = [filename for filename in os.listdir(directory_path) if filename.startswith(file_prefix)]

    # if the current argument does not contain a path, So search in the current working directory.
    else: 
        file_prefix = current_argument
        matches = [filename for filename in os.listdir(".") if filename.startswith(file_prefix)]

    if state < len(matches):
        if os.path.isdir(directory_path + matches[state]):
            return matches[state] + "/"
        else:
            return matches[state] + " "
    return None


def handle_custom_script_completion(command, text, buffer, state):
    '''
    Args:
        command: str: the command for which we are handling completion
        text: str: the current argument being completed
        buffer: str: the entire command line buffer
        state: int: the current state of the completion (0 for the first match, 1 for the second match, etc.)
    '''
    COMP_LINE=buffer # The entire command line buffer
    COMP_POINT=len(buffer) # The current cursor position in the buffer
    global MATCHES_CACHE
    if state==0:
        global TAB_HITS
        TAB_HITS+=1
        command_path=COMPLETE_DISPLAY_COMMANDS[command]
        second_argument=text # The current argument being completed
        # Determine the preceding argument based on whether there's a trailing space in the buffer
        if buffer.endswith(' '):
            # If there's a trailing space, the last word in the buffer is the preceding word
            third_argument = buffer.split()[-1] if len(buffer.split()) >= 1 else ''
        else:
            # If no trailing space, the second-to-last word is the preceding word
            third_argument = buffer.split()[-2] if len(buffer.split()) >= 2 else ''
        result = subprocess.run(
                [command_path,command,second_argument,third_argument],
                capture_output=True,
                text=True,
                check=True,
                env={
                    "COMP_LINE": COMP_LINE,
                    "COMP_POINT":str(COMP_POINT) ,
                    }
                )

        MATCHES_CACHE=sorted(result.stdout.splitlines())
    if len(MATCHES_CACHE)>1: # There are multiple candidates
        if TAB_HITS==1: # First TAB hit
            lcp=longest_common_prefix(MATCHES_CACHE)
            if lcp and len(lcp)> len(text):
                return lcp
            return None
        else:
            res=''
            for i in MATCHES_CACHE:
                res+=i
                res+='  '
            print()
            print(res)
            sys.stdout.write("$ " + buffer)
            TAB_HITS=0
            return None
    
    if state < len(MATCHES_CACHE):
        return MATCHES_CACHE[state] + " "
    return None
    
def completer(text,state):
    '''
    Args:
        text: str: the current argument being completed
        state: int: the current state of the completion (0 for the first match, 1 for the second match, etc.)
    '''
    buffer = readline.get_line_buffer()

    if ' ' in buffer:
        command=buffer.split(" ")[0] 
        current_argument = buffer.rsplit(" ", 1)[1]
        if command in COMPLETE_DISPLAY_COMMANDS:
            return handle_custom_script_completion(command,text,buffer,state)
        else:
            return handle_path_completion(current_argument,state)
    else:
        return handle_command_completion(text,state)


def update_auto_complete_commands():
    '''
    Args:
        new_command: str: the new command to add to the auto-complete list
    '''
    path_var=os.getenv('PATH','')
    path_dirs=path_var.split(os.pathsep)
    for path_dir in path_dirs:
        try:
            files=os.listdir(path_dir)
        except:
            continue 
        for file in files:
            full_path=os.path.join(path_dir, file)
            if os.access(full_path,os.X_OK):
                AUTO_COMPLETE_COMMANDS.append(file)