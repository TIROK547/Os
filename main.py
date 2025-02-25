import json
import os

class File:
    def __init__(self, name, value="", password=None):
        self.name = name
        self.value = value
        self.password = password

    def get_value(self):
        return str(self.value)

    def set_value(self, value):
        self.value = value

    def to_dict(self):
        return {"name": self.name, "value": self.value, "type": "file", "password": self.password}

class Folder:
    def __init__(self, name, password=None):
        self.name = name
        self.contents = {}
        self.password = password

    def to_dict(self):
        return {
            "name": self.name,
            "type": "folder",
            "password": self.password,
            "contents": {key: value.to_dict() for key, value in self.contents.items()},
        }

class FileSystem:
    def __init__(self, save_file="filesystem.json"):
        self.root = Folder("/")
        self.current_folder = self.root
        self.path = "/"
        self.save_file = save_file
        self.load()

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
            if len(args) != 0:
                self.ls(args[0])
            else:
                self.ls()
        elif command == "clear":
            self.clear()
            print("data cleared")
            self.load()
        elif cmd == "cat" and args:
            self.cat(args[0])
        elif cmd == "rm" and args:
            self.rm(args[0])
        elif cmd == "cp" and args:
            self.mkdir([args[1]])
            self.rm(args[0])
        elif cmd == "mv":
            pass
        elif cmd == "save":
            self.save()
            print("File system saved.")
        else:
            print("Command not found")

    def mkdir(self, data):
        name = data[0]
        path_elements = name.split("/")
        file_password = None
        value = " ".join(data[2:])
        
        temp = self.current_folder
        
        if path_elements[-1].startswith("."):
            file_password = data[1].split(" ")[0]
            print(f"Password for {name}: '{file_password}'")
            
        if name.startswith("/"):
            self.current_folder = self.root 

        for i in range(len(path_elements) - 1):
            if path_elements[i] not in self.current_folder.contents:
                self.current_folder.contents[path_elements[i]] = Folder(path_elements[i])
            self.current_folder = self.current_folder.contents[path_elements[i]]
            
        if path_elements[-1].startswith('.') and '.' in path_elements[-1][1:]:  # Password-protected file
            print("pass file")
            self.current_folder.contents[path_elements[-1]] = File(path_elements[-1], value, file_password)
        elif not path_elements[-1].startswith('.') and '.' in path_elements[-1]:  # Non-password-protected file
            print("no pass file")
            self.current_folder.contents[path_elements[-1]] = File(path_elements[-1], value)
        elif path_elements[-1].startswith('.') and '.' not in path_elements[-1][1:]:  # Password-protected folder
            print("pass folder")
            self.current_folder.contents[path_elements[-1]] = Folder(path_elements[-1], file_password)
        else:  # Non-password-protected folder
            print("no pass folder")
            self.current_folder.contents[path_elements[-1]] = Folder(path_elements[-1])

        self.current_folder = temp
        self.save()

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
        if folder_name == "/":
            self.path = "/"
            self.current_folder = self.navigate_to_folder(self.path)
        elif folder_name == "..":
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

    def ls(self, filename: str = None):
        if filename is None:
            print(" | ".join(self.current_folder.contents.keys()))
        else:
            path = filename.strip().split("/")

            if filename.startswith("/"):
                current = self.root
                path = filename[1:].split("/")
            else:
                current = self.current_folder

            for part in path:
                if part in current.contents and isinstance(current.contents[part], Folder):
                    current = current.contents[part]
                else:
                    print(f"Invalid path: {filename}")
                    return

            print(" | ".join(current.contents.keys()))

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
            self.save()
        else:
            print("File or folder not found")

    def to_dict(self):
        return {
            "root": self.root.to_dict(),
            "path": self.path
        }

    def save(self):
        with open(self.save_file, "w") as f:
            json.dump(self.to_dict(), f, indent=4)

    def load(self):
        if os.path.exists(self.save_file):
            with open(self.save_file, "r") as f:
                data = json.load(f)
                self.root = self.dict_to_folder(data["root"])
                self.current_folder = self.navigate_to_folder(data["path"])
                self.path = data["path"]

    def clear(self):
        if os.path.exists(self.save_file):
            os.remove(self.save_file)
        self.root = Folder("/")
        self.current_folder = self.root
        self.path = "/"
        print("File system reset.")

    def dict_to_folder(self, data):
        folder = Folder(data["name"])
        for name, content in data["contents"].items():
            if content["type"] == "file":
                folder.contents[name] = File(content["name"], content["value"])
            else:
                folder.contents[name] = self.dict_to_folder(content)
        return folder

fs = FileSystem()
while True:
    command = input(f"{fs.path} >>> ")
    if command.lower() == "exit":
        fs.save()
        print("File system saved. Exiting...")
        break
    fs.execute(command)
