import sys
import os

BUILTINS_COMMANDS= {"exit", "echo", "type"}
def main():
    while True:
        sys.stdout.write("$ ")
        user_input = input()
        # splitting the user input into command and arguments
        parts=user_input.split()
        command=parts[0]
        # getting the arguments
        args=parts[1:]

        if command == "exit":
            break
        elif command == 'echo':
            print(' '.join(args))

        elif user_input.startswith("type"):
            if args[0] in BUILTINS_COMMANDS:
                print(f"{args[0]} is a shell builtin")
            else:
                # splitting the directories
                path_var=os.getenv('PATH','')
                path_dirs=path_var.split(os.pathsep)
                
                # Loop over the given directories
                for path_dir in path_dirs:
                    full_path = path_dir+'/'+args[0]

                    # check if both the directory and file exist
                    if os.path.isdir(path_dir) and os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                        print(f"{args[0]} is {full_path}")
                        break
                    else:
                        continue
                else:
                    print(f'{args[0]}: not found')

            
        # Invalid input
        else:
            e=path_var=os.getenv('PATH','')
            print(e)
            
            #print(f"{user_input}: not found")


if __name__ == "__main__":
    main()
