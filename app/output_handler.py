import sys

def write_stdout(output, redirect_symbol=None, output_file=None):
    '''
    Args:
        output: str: the output to write
        redirect_symbol: str or None: the redirection symbol (">", "1>", "2>","2>>") or None
        output_file: str or None: the file to write to, or None to print to stdout
    '''
    if redirect_symbol in {">", "1>"}:
        with open(output_file, "w") as f:
            f.write(output + "\n")
    elif redirect_symbol in {">>", "1>>"}:
        with open(output_file, "a") as f:
            f.write(output + "\n")
    elif redirect_symbol in {"2>", "2>>"}:
        # stderr is redirected, stdout remains unchanged
        if redirect_symbol == "2>":
            open(output_file, "w").close()
        else:
            open(output_file, "a").close()
        print(output)
    else:
        print(output)

def write_stderr(error, redirect_symbol=None, error_file=None):
    '''
    Args:
        error: str: the error message to write
        redirect_symbol: str or None: the redirection symbol (">", "1>", "2>","2>>") or None
        error_file: str or None: the file to write to, or None to print to stderr
    '''
    if redirect_symbol == "2>":
        with open(error_file, "w") as f:
            f.write(error + "\n")
    elif redirect_symbol == "2>>":
        with open(error_file, "a") as f:
            f.write(error + "\n")
    else:
        print(error, file=sys.stderr)