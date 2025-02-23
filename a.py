class File:
    def __init__(self, name, value=""):
        self.name = name
        self.value = value  # محتویات فایل

class Folder:
    def __init__(self, name):
        self.name = name
        self.contents = {}  # شامل فایل‌ها و پوشه‌ها

class FileSystem:
    def __init__(self):
        self.root = Folder("/")  # ریشه‌ی فایل سیستم
        self.current_folder = self.root
        self.path = "/"

    def cd(self, path):
        if path == "..":
            if self.path != "/":
                self.path = "/".join(self.path.split("/")[:-1]) or "/"
        elif path in self.current_folder.contents and isinstance(self.current_folder.contents[path], Folder):
            self.current_folder = self.current_folder.contents[path]
            self.path += f"/{path}" if self.path != "/" else path
        else:
            print("Folder not found")

    def ls(self):
        print(" ".join(self.current_folder.contents.keys()))

    def cat(self, filename):
        if filename in self.current_folder.contents and isinstance(self.current_folder.contents[filename], File):
            print(self.current_folder.contents[filename].value)
        else:
            print("File not found")

    def mv(self, src, dest):
        if src in self.current_folder.contents:
            self.current_folder.contents[dest] = self.current_folder.contents.pop(src)
        else:
            print("File or folder not found")

    def rm(self, name):
        if name in self.current_folder.contents:
            del self.current_folder.contents[name]
        else:
            print("File or folder not found")

    def mkdir(self, name):
        if "." in name:
            self.current_folder.contents[name] = File(name)
        else:
            self.current_folder.contents[name] = Folder(name)

    def execute(self, command):
        parts = command.strip().split()
        if not parts:
            return
        cmd, args = parts[0], parts[1:]
        
        if cmd == "cd" and args:
            self.cd(args[0])
        elif cmd == "ls":
            self.ls()
        elif cmd == "cat" and args:
            self.cat(args[0])
        elif cmd == "mv" and len(args) == 2:
            self.mv(args[0], args[1])
        elif cmd == "rm" and args:
            self.rm(args[0])
        elif cmd == "mkdir" and args:
            self.mkdir(args[0])
        else:
            print("Command not found")

# اجرای فایل سیستم
fs = FileSystem()
while True:
    command = input(f"{fs.path} >>> ")
    if command.lower() == "exit":
        break
    fs.execute(command)
