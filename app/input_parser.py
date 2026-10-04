

def parse_input(user_input):
    '''
    Args:
        user_input: str: the input string from the user
    Returns:
        tuple: (command, args) where command is the command to execute and args is a list of arguments
    '''
    #     command, _, args_str = user_input.partition(" ")

    res = []
    temp = ''
    active_quote = None  # Can be None, "'", or '"'
    is_first_space = True
    back_slash_active = False  # To handle escaped characters

    for char in user_input:
        # Handle Single Quotes
        if char == '\\':
            # Handle backslash logic for escaping characters in quotes and outside quotes
            if (back_slash_active and active_quote == '"') or active_quote=="'" or (back_slash_active and active_quote is None):
                temp += '\\'  # Treat as a literal backslash
                back_slash_active = False
            else:
                back_slash_active = True
        # Handle Single Quotes        
        elif char == "'" and active_quote != '"':
            if back_slash_active:
                temp += char  # Treat as a literal single quote
                back_slash_active = False

            elif active_quote == "'":
                active_quote = None  # Closing single quote
            else:
                active_quote = "'"   # Opening single quote
                
        # Handle Double Quotes
        elif char == '"' and active_quote != "'":
            if back_slash_active:
                temp += char  # Treat as a literal double quote
                back_slash_active = False

            elif active_quote == '"':
                active_quote = None  # Closing double quote
            else:
                active_quote = '"'   # Opening double quote
                
        # Handle Spaces
        elif char == ' ':
            if back_slash_active:
                temp += char  # Treat as a literal space
                back_slash_active = False
            elif active_quote is not None:
                temp += ' '
            elif is_first_space:
                res.append(temp)
                #res.append(' ')
                temp = ''
                is_first_space = False
                
        # Handle Regular Characters (and nested quotes)
        else:
            if back_slash_active:
                temp += char  # Treat as a literal space
                back_slash_active = False
            else:
                temp += char
                is_first_space = True

    if temp:
        res.append(temp)
    command = res[0] if res else ''
    args = res[1:]
    return command, args

def parse_redirection(args):
    """
    Args:
        args: list of command arguments
    Returns:
        cleaned_args: arguments without redirection
        output_file: filename or None
        redirect_symbol: redirection symbol or None
    """
    redirections = {">", "1>", ">>", "1>>", "2>", "2>>"}

    for i, rediriction in enumerate(args):
        if rediriction in redirections:
            return args[:i], args[i + 1], rediriction # return the arguments before the redirection symbol, the filename after the redirection symbol, and the redirection symbol itself

    return args, None, None # No redirection found
