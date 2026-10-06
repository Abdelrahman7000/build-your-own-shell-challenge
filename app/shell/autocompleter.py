import os
import readline

AUTO_COMPLETE_COMMANDS=["exit","echo","cd","type"]

def completer(text, state):
    '''
    Args:
        text: str: the current input text to complete
        state: int: the state of the completion (0 for the first match, 1 for the second, etc.)
    Returns:
        str or None: the next possible completion for the input text, or None if no more completions are available
    '''
    # Get the current line buffer to determine if we are completing a command or a filename
    buffer = readline.get_line_buffer()

    if ' ' in buffer: # filename completion
        if '/' in buffer:
            directory_path=buffer.split()[1].rsplit("/", 1)[0]+'/'
            file_prefix=buffer.split()[1].rsplit("/", 1)[1]
            matches=[filename for filename in os.listdir(directory_path) if filename.startswith(file_prefix)]
        else:
            matches = [filename for filename in os.listdir(".") if filename.startswith(text)]
        if state <len(matches):
            return matches[state] + " "
        return None
    
    else:# command completion
        matches = [cmd for cmd in AUTO_COMPLETE_COMMANDS if cmd.startswith(text)]
        if state < len(matches):
            return matches[state] + " "
        return None

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