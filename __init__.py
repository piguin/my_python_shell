import atexit               # register an atexit func
import ast                  # check the input is executed by eval or exec
import builtins             # modify its functions and get the builtin-function list
import colorama             # initalize the terminal, needs to install it from pip
import ctypes               # Windows console api
import datetime             # only for an extension command
import json                 # saving for history
import logging              # log the init process
import os                   # use cmd for controling background colors
import pprint               # pretty display of the displayhook
import pygments             # replace the keywords and builtin-functions with the different colors, needs to install it from pip
import pygments.formatters  #
import pygments.lexers      #
import sys                  # 
import termcolor            # color of the terminal, needs to install it from pip
import time                 # for timing
import traceback            # capture the error info and color it
import unicodedata          # print unicode charactars
import webbrowser           # only for an extension command

# set the default vars

exec_flag = None
user_gbs = {}
frame_name = ""
In = []
Out = {}
prompt = ""
code = ""
_exit = sys.exit
_write = sys.stdout.write
exit_f = None
err_pattern = r""
interact_f = None
colors = {"black": [None, None, None, None, None, None, None, None]}
theme = "black"
banner = ""
logo = ""
user_data = [None, None, None, None]
user_storage = sys.stdin

# set the charactars
LIGHT_VERTICAL_AND_RIGHT = unicodedata.lookup("BOX DRAWINGS LIGHT VERTICAL AND RIGHT") # U+251C
LIGHT_UP_AND_RIGHT = unicodedata.lookup("BOX DRAWINGS LIGHT UP AND RIGHT") # U+2514
LIGHT_DOWN_AND_RIGHT = unicodedata.lookup("BOX DRAWINGS LIGHT DOWN AND RIGHT") # U+250C
LIGHT_HORIZONTAL = unicodedata.lookup("BOX DRAWINGS LIGHT HORIZONTAL") # U+2500
LIGHT_VERTICAL = unicodedata.lookup("BOX DRAWINGS LIGHT VERTICAL") # U+2502
LIGHT_ARC_DOWN_AND_RIGHT = unicodedata.lookup("BOX DRAWINGS LIGHT ARC DOWN AND RIGHT") # U+256D
LIGHT_ARC_UP_AND_RIGHT = unicodedata.lookup("BOX DRAWINGS LIGHT ARC UP AND RIGHT") # U+2570
RIGHTWARDS_ARROW = unicodedata.lookup("RIGHTWARDS ARROW") # U+2192

try:
    os.mkdir(".shell")
except FileExistsError:
    pass

user_storage_file = ".\\.shell\\user_storage.json"
log_file = ".\\.shell\\init_log.LOG"

logger = logging.getLogger(__name__)
if __debug__:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.CRITICAL)
file_handler = logging.FileHandler(log_file)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

class modules:
    pass


class Extensions_Commands:
    """
    Register a extension command.
    To list all the commands, please call the `help_commands` func
    """

    def __new__(cls, func=None):
        global user_gbs, logger, interact_f
        if func:
            def repr_func(self):
                return f"{func.__name__}({func()})"

            def call_func(self, *args, **kwargs):
                return f"{func.__name__}({func(*args, **kwargs)})"

            def init_func(self):
                self.f = func

            _cls = type(func.__name__, (), {"__repr__": repr_func, "__call__": call_func, "__init__": init_func, "__doc__": func.__doc__})
            user_gbs[func.__name__] = _cls()
            setattr(user_gbs["extend_commands"], func.__name__, _cls())
            if not interact_f:
                logger.info(f"Setting extension command {func.__name__} successful")
            return _cls()
        else:
            sys.stdout.write("Type `extend_commands.help_commands()` to see all the commands.\n")

    @staticmethod
    def help_commands(cmd=None):
        self = user_gbs["extend_commands"]
        if not cmd:
            cmds = ""
            for i in dir(self):
                if hasattr(getattr(self, i), "f"):
                    cmds += f"{(len(prompt) - 15) * ' '}{LIGHT_VERTICAL_AND_RIGHT}  {i}\n"
            sys.stdout.write(cmds)
            sys.stdout.write(f"{(len(prompt) - 15) * ' '}{LIGHT_UP_AND_RIGHT}  Please type `extend_commands.help_commands('[your command here]')` for a specific command.\n")
        else:
            for i in dir(self):
                attr = getattr(self, i)
                if hasattr(attr, "f"):
                    if i == cmd:
                        doc = attr.__doc__
                        _doc = ""
                        for i in doc.split("\n"):
                            _doc += f"{(len(prompt) - 15) * ' '}{LIGHT_VERTICAL_AND_RIGHT}\t  {i}\n"
                        if _doc:
                            sys.stdout.write(f"{(len(prompt) - 15) * ' '}{LIGHT_VERTICAL_AND_RIGHT}  Help for command `{cmd}`: \n")
                            sys.stdout.write(f"{_doc}")
                        else:
                            sys.stdout.write(f"{(len(prompt) - 15) * ' '}{LIGHT_VERTICAL_AND_RIGHT}  No documentation for command `{cmd}`\n")
                        return True
            sys.stdout.write(f"{(len(prompt) - 15) * ' '}{LIGHT_VERTICAL_AND_RIGHT}  Couldn't find command `{cmd}`\n")
            return False



def set_commands():
    @Extensions_Commands
    def Exit(*args, **kwargs): # although we didn't use it in this code, but we used it in the shell
        """A safe way to exit the shell."""
        global exit_f, In, Out, theme, user_storage, user_data, user_gbs
        if not args:
            while exit_f:
                anwser = input(f"{(len(prompt) - 15) * ' '}{LIGHT_VERTICAL_AND_RIGHT}  Are you sure you want to exit? [Y(yes)/N(no)]: ")
                if anwser == "Y":
                    exit_f = False
                    sys.stdout.write("Exiting ...\n")
                    user_data = (In, Out, theme)
                    json.dump(user_data, user_storage)
                    user_storage.close()
                    _exit()
                elif anwser == "N":
                    return repr(anwser)
            return ""
        if (args[0] == "Y") and exit_f:
            exit_f = False
            sys.stdout.write("Exiting ...\n")
            user_data = (In, Out, theme)
            json.dump(user_data, user_storage)
            user_storage.close()
            sys.stdout.close()
            sys.stdin.close()
            _exit()
        else:
            return repr(args[0])

    @Extensions_Commands
    def history(*args, **kwargs): # usage same as the Exit func
        """
        View the history of the shell. 

        Type `history` for the whole history
        Type `history([history id])` for a specific input 
        """
        global Out, In
        if not args:
            sys.stdout.write(f"{(len(prompt) - 15) * ' '}{LIGHT_VERTICAL_AND_RIGHT}  \n{(len(prompt) - 15) * ' '}{LIGHT_VERTICAL_AND_RIGHT}  History:\n")
            if Out:
                sys.stdout.write(f"{(len(prompt) - 15) * ' '}{LIGHT_VERTICAL_AND_RIGHT}  \tinputs\t\toutputs\n")
                for i, o in Out.items():
                    if len(i) > 20:
                        i = i[:20]
                        i += "..."
                    if len(o) > 20:
                        o = o[:20]
                        o += "..."
                    sys.stdout.write(f"{(len(prompt) - 15) * ' '}{LIGHT_VERTICAL_AND_RIGHT}  \t{color_code(i)}\t\t{o}\n")
                sys.stdout.write(f"{(len(prompt) - 15) * ' '}{LIGHT_VERTICAL_AND_RIGHT}  \n")
                return ""
            sys.stdout.write(f"{(len(prompt) - 15) * ' '}{LIGHT_VERTICAL_AND_RIGHT}  \tYou don't have any inputs yet! \n{(len(prompt) - 15) * ' '}{LIGHT_VERTICAL_AND_RIGHT}  \n")
            return ""
        try:
            sys.stdout.write(f"{(len(prompt) - 15) * ' '}{LIGHT_VERTICAL_AND_RIGHT}  History number {args[0]}:\n")
            inp_code = In[args[0] - 1]
            sys.stdout.write(f"{(len(prompt) - 15) * ' '}{LIGHT_VERTICAL_AND_RIGHT}  \t{color_code(inp_code)}\t{Out[inp_code]}\n")
        except IndexError:
            sys.stdout.write(f"{(len(prompt) - 15) * ' '}{LIGHT_VERTICAL_AND_RIGHT}  \nHistory number {args[0]} doesn't exists.")
        else:
            return args[0]

    @Extensions_Commands
    def change_theme(*args, **kwargs): # usage same as the history func
        """Change the theme of the shell."""
        global theme, colors
        themes = list(colors)
        theme = themes[(themes.index(theme) + 1) % len(themes)]
        os.system(f"color {get_color(8)[0]}")
        return ""
    
    @Extensions_Commands
    def open_browser(*args, **kwargs): # usage same as the change_theme func
        """Open a URL in the browser"""
        if not args:
            url = input("      {LIGHT_VERTICAL_AND_RIGHT}  Please enter your URL: ")
            webbrowser.open(url)
            return repr(url)
        webbrowser.open(args[0])
        return args[0]
    
    @Extensions_Commands
    def open_terminal(*args, **kwargs): # usage same as the open_browser func
        """Execute a CMD command"""
        if not args:
            cmd = input("      {LIGHT_VERTICAL_AND_RIGHT}  Please enter your command: ")
            res = os.popen(cmd).read().split("\n")
            for i in res:
                sys.stdout.write(f"      {LIGHT_VERTICAL_AND_RIGHT}  {i}\n")
            return repr(cmd)
        os.system(args[0])

    @Extensions_Commands
    def clear_data(*args, **kwargs): # usage same as the open_terminal func
        """Clear all the history of the shell."""
        global In, Out, theme, user_gbs
        if not args:
            while True:
                anwser = input(f"{(len(prompt) - 15) * ' '}{LIGHT_VERTICAL_AND_RIGHT}  Are you sure you want to clear all the data? [Y(yes)/N(no)]: ")
                if anwser == "Y":
                    In = []
                    Out = {}
                    theme = "black"
                    user_gbs = {"__name__": "__main__",
                                "__doc__": "my first virtual python environment!",
                                "__package__": None,
                                "__spec__": None,
                                "__annotations__": {},
                                "__builtins__": builtins,
                                "__loader__": None,
                                "In": In,
                                "Out": Out,
                                "__dict__": user_gbs,
                                "_": None,
                                "extend_commands": Extensions_Commands,
                                "modules": modules}
                    set_commands()
                    break
                elif anwser == "N":
                    break
            return repr(anwser)
        else:
            if args[0] == "Y":
                In = []
                Out = {}
                theme = "black"
                user_gbs = {"__name__": "__main__",
                            "__doc__": "my first virtual python environment!",
                            "__package__": None,
                            "__spec__": None,
                            "__annotations__": {},
                            "__loader__": None,
                            "In": In,
                            "Out": Out,
                            "_": None,
                            "extend_commands": Extensions_Commands,
                            "modules": modules}
                set_commands()
            return repr(args[0])

    @Extensions_Commands
    def load_data(*args, **kwargs): # usage same as the clear_data func
        """Load a history"""
        if repr(clear_data) == "clear_data('Y')":
            load_user_data(input(f"{(len(prompt) - 15) * ' '}{LIGHT_VERTICAL_AND_RIGHT}  Please enter your storage file's path: "))
        return ""

    @Extensions_Commands
    def get_time(*args, **kwargs): # usage same as the load_data func
        """Get the current time."""
        sys.stdout.write(f"{(len(prompt) - 15) * ' '}{LIGHT_VERTICAL_AND_RIGHT}  Current time: {datetime.datetime.now()}\n")
        return ""


def load_user_data(storage_file=user_storage_file):
    global In, Out, theme, user_storage, user_data, logger, user_storage_file, user_gbs
    logger.info(f"Loading user storage `{storage_file}`")
    try:
        user_storage = open(storage_file, "r")
        user_data = json.loads(user_storage.read())
        In, Out, theme = user_data
        user_storage.close()
        logger.info("Loading user storage successful")
    except FileNotFoundError:
        In = []
        Out = {}
        theme = "black"
        logger.warning("Couldn't find user storage file")
    except Exception as e:
        logger.error(f'Error opening {storage_file}')
        error_str = traceback.format_exc()
        sys.stderr.write(f"Error ocurred when opening {storage_file}:\n")
        result = modified_traceback(e)
        sys.stdout.write(result)
        sys.stdout.write("\nPlease clear your data\n")
        sys.stdout.flush()
        time.sleep(1)
    os.system("cls")
    user_storage = open(user_storage_file, "w")


def load_user_modules():
    global user_gbs, logger
    for m, imp in sys.modules.items():
        if not m.startswith("_"):
            logger.info(f"Loading module {m}")
            try:
                setattr(user_gbs["modules"], m, imp)
            except Exception as e:
                logger.error(f"Couldn't load module {m} due to error `{e}`")


def get_color(idx):
    """
    Get the colors of the current theme.
    """
    global colors, theme
    return (colors[theme][idx], "on_" + theme)


def on_exit():
    """
    Ask user to exit
    """
    global exit_f
    exit_f = True
    return repr(builtins.exit)


def modified_displayhook(obj):
    """
    The modified version of sys.displayhook
    """
    global Out, In, user_gbs, user_storage
    try:
        if obj is not None:
            repr_obj = pprint.pformat(obj, indent=4) if hasattr(obj, "__iter__") else repr(obj)
            Out[In[-1]] = repr_obj
            user_gbs["_"] = obj
            if "\n" in repr_obj:
                sys.stdout.write(f"{' ' * (len(prompt) - 15)}{LIGHT_ARC_UP_AND_RIGHT}  " + termcolor.colored(f"Out[{len(In)}]", *get_color(0)) + f": \n\n{repr_obj}\n")
            else:
                sys.stdout.write(f"{' ' * (len(prompt) - 15)}{LIGHT_ARC_UP_AND_RIGHT}  " + termcolor.colored(f"Out[{len(In)}]", *get_color(0)) + f": {repr_obj}\n")
            sys.stdout.write(f"\x1b]0;My python shell - {repr_obj}\x07\r\n")
    except IndexError: # if encounters a bug
        sys.__displayhook__(obj)


def modified_traceback(exc):
    global code

    line = f'{LIGHT_HORIZONTAL}' * 50
    traceback_list = traceback.extract_tb(exc.__traceback__)
    result = f"{line}\nTraceback (most recent call last):\n"
    cont = False
    for tb in traceback_list:
        filename, line_num, func_name, error_code = tb
        for fpath in sys.path:
            if fpath in filename:
                cont = True
            if "<shell-" in filename:
                cont = False
        if cont:
            continue
        if func_name == "<module>":
            error_code = code
        if error_code:
            result += f'  {LIGHT_VERTICAL_AND_RIGHT}  File "{termcolor.colored(filename, *get_color(4))}", ' \
                      f'line {termcolor.colored(line_num, *get_color(5))}, ' \
                      f'in {termcolor.colored(func_name, *get_color(6))}: \n' \
                      f'  {LIGHT_VERTICAL}\t{color_code(error_code)}\n'
        else:
            result += f'  {LIGHT_VERTICAL_AND_RIGHT}  File "{termcolor.colored(filename, *get_color(4))}", ' \
                      f'line {termcolor.colored(line_num, *get_color(5))}, ' \
                      f'in {termcolor.colored(func_name, *get_color(6))}\n'
    result += f"  {LIGHT_UP_AND_RIGHT}  {termcolor.colored(type(exc).__name__, *get_color(7))}: {exc}\n"
    result += line + "\n"
    return result


def parse_code(inp_code):
    """
    Parse the code
    """
    global frame_name, user_gbs, Out
    mod = ast.parse(inp_code, filename=frame_name)
    if len(mod.body) == 0:
        return

    if isinstance(mod.body[-1], ast.Expr):
        expr = ast.Expression(mod.body[-1].value)
        del mod.body[-1]
    else:
        expr = None

    if len(mod.body):
        exec(compile(mod, frame_name, mode='exec'), user_gbs, user_gbs)
        Out[inp_code] = ""
    if expr is not None:
        sys.displayhook(eval(compile(expr, frame_name, mode='eval'), user_gbs, user_gbs))


def code_is_complete(inp_code):
    try:
        ast.parse(inp_code, mode='exec')
        return True
    except SyntaxError:
        return False


def input_code(pmt=None):
    global In, exec_flag, frame_name, prompt
    try:
        if not pmt:
            prompt = pmt = termcolor.colored(f"\nIn [{len(In) + 1}]", *get_color(3))
        sys.ps1 = f"{pmt}{LIGHT_ARC_DOWN_AND_RIGHT}{RIGHTWARDS_ARROW} "
        inp_code = input(sys.ps1)
        In.append(inp_code)
    except EOFError:
        In.append(on_exit())
        inp_code = In[-1]
    except RuntimeError:
        exit_f = False
        _exit()
    frame_name = f"<shell-{len(In)}>"
    if not code_is_complete(inp_code):
        if not exec_flag:
            block = ""
            exec_flag = False
            while True:
                if not exec_flag:
                    try:
                        sys.ps2 = f"{' ' * (len(prompt) - 15)}{LIGHT_VERTICAL_AND_RIGHT}   "
                        line = input(sys.ps2)
                    except EOFError:
                        raise IndentationError("expected an indented block")
                    except RuntimeError:
                        exit_f = False
                        _exit()
                    block += line + "\n"
                else:
                    exec_flag = False
                    break
                if not line.strip():
                    exec_flag = True
                    continue
            inp_code += "\n" + block
        else:
            exc = SyntaxError("invalid syntax")
            exc.lineno = 1
            raise exc
    return inp_code


def color_code(code_string):
    """
    colors the code.
    """
    return pygments.highlight(code_string, pygments.lexers.PythonLexer(), pygments.formatters.TerminalFormatter(bg="dark")).split("\n")[0]


def init():
    """
    Initalize the whole shell:
        Set up the environment vars
        Initalize the console
        Modify builtin-funcs, including builtins and sys
        Write the banner
        ...

    """
    global exec_flag, \
           user_gbs, \
           frame_name, \
           In, \
           Out, \
           _exit, \
           exit_f, \
           prompt, \
           err_pattern, \
           interact_f, \
           colors, \
           theme, \
           banner, \
           user_data, \
           logger, \
           logo
    
    run_from_console = False
    if sys.platform == "win32":
        kernel32 = ctypes.windll.kernel32
        console = kernel32.GetConsoleWindow()
        if console or os.getenv('PROMPT'):
            run_from_console = True
    else:
        if sys.__stdin__:
            run_from_console = True
    if not run_from_console:
        sys.stderr.write("\nCouldn't detect console window, you need to run this program in a terminal.\n")
        sys.exit()
    logger.info(f"This is my_python_shell on {sys.platform} terminal")
    logger.info(f"Current time: {datetime.datetime.now()}")
    logger.info("Initializing terminal")
    colorama.init()
    logger.info("Initializing terminal complete")

    err_pattern = r'File "(.*?)", line (\d+), in (.*?)\n(.*?)\n'

    load_user_data()
    user_gbs = {"__name__": "__main__",
                "__doc__": banner,
                "__package__": None,
                "__spec__": None,
                "__annotations__": {},
                "__loader__": None,
                "In": In,
                "Out": Out,
                "__dict__": user_gbs,
                "_": None,
                "extend_commands": Extensions_Commands,
                "modules": modules}
    load_user_modules()
    user_gbs["modules"] = user_gbs["modules"]()
    interact_f = False
    exec_flag = False
    exit_f = True
    frame_name = f"<shell-{len(In)}>"
    colors = {"black": ["light_red", "light_yellow", "light_magenta", "light_green", "magenta", "yellow", "light_cyan", "red", "0f"],
              "white": ["light_green", "light_blue", "light_green", "light_magenta", "green", "blue", "red", "green", "f0"]}

    def modified_write(string, color=None, on_color=theme):
        global _write
        _write(termcolor.colored(string, color, "on_" + on_color))

    sys.stdout.write = modified_write
    
    os.system(f"color {get_color(8)[0]}")
    logger.info("Setting theme successful")

    sys.stdout.write(f"\x1b]0;My python shell\x07\r")

    _exit = sys.exit

    set_commands()

    builtins.exit = user_gbs["Exit"]
    builtins.quit = user_gbs["Exit"]

    def on_exit():
        return repr(user_gbs["Exit"])


    atexit.register(on_exit)
    logger.info("Registering exit-func successful")

    sys.displayhook = modified_displayhook
    
    prompt = termcolor.colored(f"\nIn [0]", *get_color(3))
    sys.ps1 = f"{prompt}{LIGHT_ARC_DOWN_AND_RIGHT}{RIGHTWARDS_ARROW} "
    sys.ps2 = f"{(len(prompt) - 15) * ' '}{LIGHT_VERTICAL_AND_RIGHT}   "
    logger.info("Setting prompt successful")
    
    logo = r"""
  __  __         _____       _   _                    _____ _          _ _
 |  \/  |       |  __ \     | | | |                  / ____| |        | | |
 | \  / |_   _  | |__) |   _| |_| |__   ___  _ __   | (___ | |__   ___| | |
 | |\/| | | | | |  ___/ | | | __| '_ \ / _ \| '_ \   \___ \| '_ \ / _ \ | |
 | |  | | |_| | | |   | |_| | |_| | | | (_) | | | |  ____) | | | |  __/ | |
 |_|  |_|\__, | |_|    \__, |\__|_| |_|\___/|_| |_| |_____/|_| |_|\___|_|_|
          __/ |         __/ |
         |___/         |___/
    """

    banner = f"\n{termcolor.colored(logo, *get_color(6))}\n\n{81 * chr(9472)}\n\n " \
             f"Features:\n" \
             f"    {LIGHT_DOWN_AND_RIGHT}{LIGHT_HORIZONTAL}  Runs the code in a sandbox (User namespace)\n" \
             f"    {LIGHT_VERTICAL_AND_RIGHT}{LIGHT_HORIZONTAL}  Supports indented code\n" \
             f"    {LIGHT_VERTICAL_AND_RIGHT}{LIGHT_HORIZONTAL}  Uses the terminal control sequences for better TUI appearance\n" \
             f"    {LIGHT_VERTICAL_AND_RIGHT}{LIGHT_HORIZONTAL}  Record the history of the inputs\n" \
             f"    {LIGHT_VERTICAL_AND_RIGHT}{LIGHT_HORIZONTAL}  Show the latest output on the title of the terminal\n" \
             f"    {LIGHT_VERTICAL_AND_RIGHT}{LIGHT_HORIZONTAL}  Uses Unicode characters for better TUI appearance\n" \
             f"    {LIGHT_VERTICAL_AND_RIGHT}{LIGHT_HORIZONTAL}  Coloring the traceback\n" \
             f"    {LIGHT_VERTICAL_AND_RIGHT}{LIGHT_HORIZONTAL}  Change the theme\n" \
             f"    {LIGHT_UP_AND_RIGHT}{LIGHT_HORIZONTAL}  Can extend using the extend_commands decorator. (Type `extend_commands.help_commands()` to see all the commands.)\n\n{81 * chr(9472)}\n\n" \
             f"\t\t\t\tHappy Using!\n\n\n"

    logger.info("Initializing shell successful.")
    
    sys.stdout.write(banner)


def main():
    """
    Main part of the shell
    """
    global exec_flag, user_gbs, frame_name, prompt, err_pattern, interact_f, code
    interact_f = True
    try:
        while True:
            try:
                code = input_code()
                parse_code(code)
                user_gbs["__dict__"] = user_gbs
                sys.stdout.write("")
            except Exception as e:
                Out[code] = str(e)
                error_str = traceback.format_exc()
                result = modified_traceback(e)
                sys.stdout.write(result)

    except KeyboardInterrupt as e:
        sys.stderr.write(termcolor.colored(f"\n{traceback.format_exc(limit=0)}\n", *get_color(7)))
        main()


if not (__name__ == "__main__"):
    init()
    __all__ = ["main", "init", "Extensions_Commands"]
else:
    sys.stderr.write("Please run this script by __main__.py\n")
    sys.stderr.flush()
    os.system("PAUSE")
    
    if os.system(".\__main__.py"):
        raise Exception("`__main__.py` not found")