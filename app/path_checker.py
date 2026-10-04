import os

def find_path(target_command):
    '''
    Args:
        target_command: str: the command to find in the PATH directories
    Returns:
        str: the full path of the command if found, None otherwise
    '''
    path_var=os.getenv('PATH','')
    path_dirs=path_var.split(os.pathsep)

    for path_dir in path_dirs:
        #full_path = path_dir+'/'+target_command
        full_path = os.path.join(path_dir, target_command)
        # check if both the directory and file exist
        if os.path.isdir(path_dir) and os.path.isfile(full_path) and os.access(full_path, os.X_OK):
            return full_path
        else:
            continue
    else:
        return None
