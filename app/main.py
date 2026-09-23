import sys
import os

BUILTINS_COMMANDS= {"exit", "echo", "type"}
def main():
    while True:
        sys.stdout.write("$ ")
        user_input = input()
        # command=user_input[0]
        # parts = user_input[1:] if len(user_input) > 1 else ''

        if user_input == "exit":
            break
        elif user_input.startswith("echo"):
            print(user_input[5:])

        elif user_input.startswith("type"):
            if user_input.split()[1] in BUILTINS_COMMANDS:
                print(f"{user_input.split()[1]} is a shell builtin")
            else:
                # splitting the directories
                path_var=os.getenv('PATH','')
                path_dirs=path_var.split(os.pathsep)
            
                # checking if the each directoy and file exist
                for path_dir in path_dirs:
                    full_path = path_dir+'/'+user_input.split()[1]
                    print(full_path)
                

                #     if os.path.isdir(path_dir) and os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                #         print(f"{user_input.split()[1]} is {full_path}")
                #         break
                #     else:
                #         continue
                # else:
                #     print(f'{user_input.split()[1]}: not found')

                break
        # Invalid input
        else:
            print(f"{user_input}: not found")


if __name__ == "__main__":
    main()
