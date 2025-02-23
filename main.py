class File:
    def __init__(self, name, value=""):
        self.name = name
        self.value = value
    def get_value(self):
        return str(self.value)
    def set_value(self, value):
        self.value = value

class Folder:
    def __init__(self, name):
        self.name = name
        self.contents = {}

class FileSystem:
    def __init__(self):
        self.root = Folder("/")
        self.current_folder = self.root
        self.path = "/"

    def execute(self, command):
        parts = command.strip().split()
        if not parts:
            return
        cmd = parts[0]
        args = parts[1:]
        if cmd == "mkdir" and args:
            self.mkdir([args[0], " ".join(args[1:])])
        elif cmd == "cd" and args:
            self.cd(args[0])
        elif cmd == "ls":
            self.ls()
        elif cmd == "cat" and args:
            self.cat(args[0])
        elif cmd == "rm" and args:
            self.rm(args[0])
        else:
            print("Command not found")

    def mkdir(self, data):
        name = data[0]
        value = " ".join(data[1:])
        if ".txt" in name:
            self.current_folder.contents[name] = File(name, value)
        else:
            self.current_folder.contents[name] = Folder(name)

    def cat(self, filename):
        if filename in self.current_folder.contents:
            item = self.current_folder.contents[filename]
            if isinstance(item, File):
                print(item.get_value())
            else:
                print(f"{filename} is not a file")
        else:
            print("File not found")

    def cd(self, folder_name):
        if folder_name == "..":
            if self.path == "/":
                print("Already at the root directory")
            else:
                self.path = "/".join(self.path.strip("/").split("/")[:-1]) + "/"
                self.current_folder = self.navigate_to_folder(self.path)
        else:
            if folder_name in self.current_folder.contents:
                if isinstance(self.current_folder.contents[folder_name], Folder):
                    self.current_folder = self.current_folder.contents[folder_name]
                    self.path += folder_name + "/"
                else:
                    print(f"{folder_name} is not a folder")
            else:
                print(f"No such folder: {folder_name}")

    def navigate_to_folder(self, path):
        parts = path.strip("/").split("/")
        current = self.root
        for part in parts:
            if part:
                current = current.contents.get(part, current)
        return current

    def ls(self):
        print(" | ".join(self.current_folder.contents.keys()))
    def rm(self, name):
        if name in self.current_folder.contents:
            del self.current_folder.contents[name]
        else:
            print("File or folder not found")

fs = FileSystem()
while True:
    command = input(f"{fs.path} >>> ")
    if command.lower() == "exit":
        break
    fs.execute(command)
