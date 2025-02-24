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
        path_elements = name.split("/")
        value = " ".join(data[1:])
        
        temp = self.current_folder
        if name.startswith("/"):
            self.current_folder = self.root

        for i in range(len(path_elements)-1):
            if path_elements[i] not in self.current_folder.contents:
                self.current_folder.contents[path_elements[i]] = Folder(path_elements[i])
            self.current_folder = self.current_folder.contents[path_elements[i]]
        
        if "." in path_elements[-1]:
            self.current_folder.contents[path_elements[-1]] = File(path_elements[-1], value)
        else:
            self.current_folder.contents[path_elements[-1]] = Folder(path_elements[-1])

        self.current_folder = temp
    def cat(self, filename):
        path = filename.strip().split("/")
        temp = self.current_folder

        if filename.startswith("/"):
            current = self.root
            path = filename[1:].split("/")
        else:
            current = self.current_folder
            
        for part in path[:-1]:
            if part in current.contents and isinstance(current.contents[part], Folder):
                current = current.contents[part]
            else:
                print(f"Invalid path: {filename}")
                return

        final_name = path[-1]
        if final_name in current.contents and isinstance(current.contents[final_name], File):
            print(current.contents[final_name].get_value())
        else:
            print(f"{filename} is not a file or does not exist")
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
    def rm(self, filename):
        path = filename.strip().split("/")
        temp = self.current_folder

        if filename.startswith("/"):
            current = self.root
            path = filename[1:].split("/")
        else:
            current = self.current_folder
            
        for part in path[:-1]:
            if part in current.contents and isinstance(current.contents[part], Folder):
                current = current.contents[part]
            else:
                print(f"Invalid path: {filename}")
                return

        final_name = path[-1]
        if final_name in current.contents:
            del current.contents[final_name]
        else:
            print("File or folder not found")

fs = FileSystem()
while True:
    command = input(f"{fs.path} >>> ")
    if command.lower() == "exit":
        break
    fs.execute(command)
