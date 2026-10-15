#import sys
import os
import subprocess
import readline
from app.shell_utils.input_parser import parse_input, parse_redirection
from app.shell_utils.path_checker import find_path
from app.shell_utils.output_handler import write_stdout, write_stderr
from app.shell_utils.autocompleter import completer, update_auto_complete_commands , AUTO_COMPLETE_COMMANDS, COMMAND_COMPLETION_SCRIPTS


BUILTINS_COMMANDS= {"exit", "echo", "type","pwd","cd","complete","jobs"}
BACKGROUND_JOBS={}

def main():
    # Update the auto-complete commands list with executables from the PATH directories
    update_auto_complete_commands()

    # Set up the readline completer
    readline.set_completer(completer)
    # Set the delimiters for word boundaries in the completer to include "-" as part of words and not to separate the word based on it. This allows for auto-completion of commands and filenames that contain hyphens.
    readline.set_completer_delims(readline.get_completer_delims().replace("-", ""))

    #print("DELIMS:", repr(readline.get_completer_delims()))
    # Make TAB triggers completion
    readline.parse_and_bind("tab: complete")
    while True:
        #sys.stdout.write("$ ")
        user_input = input("$ ")
        # parse the user input into command and arguments
        command,args=parse_input(user_input)
        
        # parse the arguments to check for output redirection
        args, output_file, redirect_symbol = parse_redirection(args)

        if command == "exit":
            break
        elif command == 'pwd':
            output=os.getcwd()
            write_stdout(output,redirect_symbol,output_file)

        elif command == 'cd':
            if not args or args[0] == "~":
                target_dir = os.getenv("HOME", "/")
            else:
                target_dir = args[0]
            try:
                os.chdir(target_dir)
            except (FileNotFoundError, NotADirectoryError, PermissionError):
                error=f"cd: {target_dir}: No such file or directory"
                write_stderr(error, redirect_symbol, output_file)

        elif command == 'echo':
            output=" ".join(args)
            write_stdout(output,redirect_symbol,output_file)
            
        elif command =="type":
            if args[0] in BUILTINS_COMMANDS:
                output=f"{args[0]} is a shell builtin"
                write_stdout(output, redirect_symbol, output_file)
            else:
                # if the command is not a built-in command, we will search for it in the PATH directories
                resulted_path=find_path(args[0])
                if resulted_path:
                    output=f"{args[0]} is {resulted_path}"
                    write_stdout(output, redirect_symbol, output_file)
                # if the command is not found in the PATH directories, we will print an error message
                else:
                    output=f'{args[0]}: not found'
                    write_stderr(output, redirect_symbol, output_file)

        elif command == "complete": # handling the "complete" command for auto-completion specifications
            # if the command is "complete", we will check if the arguments are valid and update the COMPLETE_DISPLAY_COMMANDS dictionary accordingly
            if len(args)>=3 and args[0]=='-C': 
                target_command=args[2]
                completer_path=args[1]
                COMMAND_COMPLETION_SCRIPTS[target_command]= completer_path

            elif len(args)>=2 and args[0]=='-r':
                target_command=args[1]
                COMMAND_COMPLETION_SCRIPTS.pop(target_command, None)

            # if the command is "complete -p", we will check if the target command has a completion specification and print it accordingly
            elif len(args)>=2 and args[0]=='-p':
                target_command=args[1]
                if target_command in COMMAND_COMPLETION_SCRIPTS:
                    completer_path=COMMAND_COMPLETION_SCRIPTS[target_command]
                    print(f"complete -C '{completer_path}' {target_command}")

                else:
                    print(f'complete: {target_command}: no completion specification')
        
        elif command=='jobs':
            if BACKGROUND_JOBS:
                list_keys = list(BACKGROUND_JOBS.keys())
                curr_job=list_keys[-1]
                prev_job=list_keys[-2] if len(list_keys)>1 else -1
                completed_jobs=[]

                for job_num,val in BACKGROUND_JOBS.items():

                    sign='+' if job_num==curr_job else '-' if job_num==prev_job else ' '
                    _,job_command,proc = val
                    
                    if proc.poll() is not None: # checking if the background job is still running or has completed
                        print(f"[{job_num}]{sign}  Done                 {job_command}  ")
                        completed_jobs.append(job_num) # Adding the completed job number to the list of completed jobs to be removed from BACKGROUND_JOBS later
                        continue

                    # if the background job is still running, we will print its status as "Running"
                    print(f"[{job_num}]{sign}  Running                 {job_command}  ") # & is optional

                for job in completed_jobs: # Removing the completed jobs from the BACKGROUND_JOBS dictionary
                    BACKGROUND_JOBS.pop(job,None)
                    
        # executing the command if it is not a built-in command (external command/program) or invalid command
        else:
            # finding the command in the PATH directories
            command_path = find_path(command)

            if command_path: # if the command is found in the PATH directories
                # inserting the command at the beginning of the arguments list
                args.insert(0, command)
                # executing the command using subprocess.run and redirecting the output to a file if specified
                if output_file and redirect_symbol == "2>":
                    with open(output_file, "w") as f:
                        subprocess.run(
                            args,
                            executable=command_path,
                            stderr=f
                        )
                elif output_file and redirect_symbol == "2>>":
                    with open(output_file, "a") as f:
                        subprocess.run(
                            args,
                            executable=command_path,
                            stderr=f
                        )
                elif output_file and redirect_symbol in {">", "1>"}:
                    with open(output_file, "w") as f:
                        subprocess.run(
                            args,
                            executable=command_path,
                            stdout=f
                        )
                elif output_file and redirect_symbol in {"1>>", ">>"}:
                    with open(output_file, "a") as f:
                        subprocess.run(
                            args,
                            executable=command_path,
                            stdout=f
                        )
                # Background jobs
                elif args[-1]=='&':
                    args.pop()
                    proc=subprocess.Popen(
                        args,
                        executable=command_path
                    )
                    child_process_id=proc.pid
                    if BACKGROUND_JOBS:
                        last_job_number=list(BACKGROUND_JOBS.keys())[-1]
                        next_job=last_job_number+1
                    else:
                        next_job=1
            
                    BACKGROUND_JOBS[next_job]=[child_process_id,' '.join(args),proc]#[0]child_process_id,[1]args,[2]proc  #child_process_id
                    print(f"[{next_job}] {child_process_id}")

                # executing the command without output redirection
                else:
                    subprocess.run(
                            args,
                            executable=command_path
                    )
                    

            # command not found (unidentified command)
            else:
                output=f"{user_input}: not found"
                write_stderr(output, redirect_symbol, output_file)

        if BACKGROUND_JOBS:
            list_keys = list(BACKGROUND_JOBS.keys())
            curr_job=list_keys[-1]
            prev_job=list_keys[-2] if len(list_keys)>1 else -1
            completed_jobs=[]
            for job_num,val in BACKGROUND_JOBS.items():
                sign='+' if job_num==curr_job else '-' if job_num==prev_job else ' '
                _,job_command,proc = val
                if proc.poll() is not None: # checking if the background job is still running or has completed
                    print(f"[{job_num}]{sign}  Done                 {job_command}  ")
                    completed_jobs.append(job_num) # Adding the completed job number to the list of completed jobs to be removed from BACKGROUND_JOBS later

            for job in completed_jobs: # Removing the completed jobs from the BACKGROUND_JOBS dictionary
                BACKGROUND_JOBS.pop(job,None)





if __name__ == "__main__":
    main()
