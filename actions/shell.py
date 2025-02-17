import os, shlex, traceback, rich

def action_data():
    return {
    "name": "shell",
    "author": "Kaiser",
    "version": "0.9",
    "features": [],
    "group": "utility",
}

def on_help(ctx):
    pass

def on_load(ctx): 
    ctx.set_config("shell.active", True)
    ctx.touch_config("cwd", os.getcwd()+"/")
    
    print(f"Active in {os.getcwd()}")
    
    subctx = ctx.clone()
    subctx.exit_code(100)
    subctx.load_config()
    subctx.plaintext_output = ctx.touch_config("plaintext", False)

    def reps(s):
        if "$cwd" in s:
            s = s.replace("$cwd", os.getcwd())
            home = os.environ['HOME']
            s = s.replace(home, "~")

        if "$fcwd" in s:
            s = s.replace("$fcwd", os.getcwd())

        return s

    ctx.writeln(" ----------- ")
    ctx.writeln(" AOS SHELL MODE ")
    ctx.writeln(" (`q` to quit, `help` for command list) ")
    ctx.writeln(" (line starting with `:` is evaluated python code) ")
    ctx.writeln(" (line starting with `sh` is executed in system terminal) ")
    ctx.writeln(" ----------- ")
    while subctx.exit_code() == 100:
        prompt = ctx.touch_config("shell.prompt", "> ")
        above_prompt = ctx.touch_config("shell.above_prompt", " [ $cwd ]")

        if above_prompt != "":
            ctx.writeln(reps(above_prompt))

        usr = ctx.console.input(prompt=reps(prompt))

        if usr == "q" or usr == "quit" or usr == "exit":
            subctx.exit_code(1)
            break
        
        if usr == "help":
            usr = "actions list"

        if usr.startswith(":"):
            line = usr[1:]
            try:
                eval(line, {"ctx": ctx, "sv": ctx.set_config, "console": ctx.console})
            except:
                print(traceback.format_exc())
            continue

        if usr.startswith("sh "):
            line = usr[3:]
            try:
                os.system(line)
            except:
                print(traceback.format_exc())
            continue

        usr = shlex.split(usr)

        if len(usr) == 0: usr = ['actions', "list"]

        cmd = usr[0]
        lines = usr[1:]
        subctx.update(command = cmd, lines = lines)
            
        subctx.execute()
        if subctx.response["data"].get("tts"):
            subctx.say(subctx.response["data"]["tts"])

        
    ctx.exit_code(0)
    return ctx

def on_exit(ctx):
    ctx.set_config("shell.active", False)
    print(ctx.exit_code())
