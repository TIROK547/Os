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
            self.mkdir(args)
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

    def check_password(self, item, item_name):
        """Check if the item is password-protected and verify the password."""
        if item.password:
            password = input(f"Enter password for {item_name}: ")
            if password != item.password:
                print("Incorrect password")
                return False
        return True

    def mkdir(self, args):
        """Create a file or folder."""
        if not args:
            print("Usage: mkdir <name> [value]")
            return

        # Extract the name and value from the arguments
        name = args[0]
        value = " ".join(args[1:]) if len(args) > 1 else ""
        path_elements = name.split("/")
        file_password = None

        temp = self.current_folder

        # Check if the name indicates a password-protected file/folder
        if path_elements[-1].startswith("."):
            file_password = input(f"Set password for {name}: ")

        if name.startswith("/"):
            self.current_folder = self.root

        # Navigate to the parent folder
        for i in range(len(path_elements) - 1):
            if path_elements[i] not in self.current_folder.contents:
                self.current_folder.contents[path_elements[i]] = Folder(path_elements[i])
            self.current_folder = self.current_folder.contents[path_elements[i]]

        # Create the file or folder
        final_name = path_elements[-1]
        if "." in final_name:  # It's a file
            self.current_folder.contents[final_name] = File(final_name, value, file_password)
        else:  # It's a folder
            self.current_folder.contents[final_name] = Folder(final_name, file_password)

        self.current_folder = temp
        self.save()

    def cat(self, filename):
        """Display the contents of a file."""
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
            file = current.contents[final_name]
            if not self.check_password(file, final_name):
                return
            print(file.get_value())
        else:
            print(f"{filename} is not a file or does not exist")

    def cd(self, folder_name):
        """Change the current directory."""
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
                    folder = self.current_folder.contents[folder_name]
                    if not self.check_password(folder, folder_name):
                        return
                    self.current_folder = folder
                    self.path += folder_name + "/"
                else:
                    print(f"{folder_name} is not a folder")
            else:
                print(f"No such folder: {folder_name}")

    def navigate_to_folder(self, path):
        """Navigate to a folder based on the given path."""
        parts = path.strip("/").split("/")
        current = self.root
        for part in parts:
            if part:
                current = current.contents.get(part, current)
        return current

    def ls(self, filename: str = None):
        """List the contents of a folder."""
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
                    folder = current.contents[part]
                    if not self.check_password(folder, part):
                        return
                    current = folder
                else:
                    print(f"Invalid path: {filename}")
                    return

            print(" | ".join(current.contents.keys()))

    def rm(self, filename):
        """Remove a file or folder."""
        path = filename.strip().split("/")
        temp = self.current_folder

        if filename.startswith("/"):
            current = self.root
            path = filename[1:].split("/")
        else:
            current = self.current_folder

        for part in path[:-1]:
            if part in current.contents and isinstance(current.contents[part], Folder):
                folder = current.contents[part]
                if not self.check_password(folder, part):
                    return
                current = folder
            else:
                print(f"Invalid path: {filename}")
                return

        final_name = path[-1]
        if final_name in current.contents:
            item = current.contents[final_name]
            if not self.check_password(item, final_name):
                return
            del current.contents[final_name]
            self.save()
        else:
            print("File or folder not found")

    def to_dict(self):
        """Convert the file system to a dictionary for saving."""
        return {
            "root": self.root.to_dict(),
            "path": self.path
        }

    def save(self):
        """Save the file system to a file."""
        with open(self.save_file, "w") as f:
            json.dump(self.to_dict(), f, indent=4)

    def load(self):
        """Load the file system from a file."""
        if os.path.exists(self.save_file):
            with open(self.save_file, "r") as f:
                data = json.load(f)
                self.root = self.dict_to_folder(data["root"])
                self.current_folder = self.navigate_to_folder(data["path"])
                self.path = data["path"]

    def clear(self):
        """Reset the file system."""
        if os.path.exists(self.save_file):
            os.remove(self.save_file)
        self.root = Folder("/")
        self.current_folder = self.root
        self.path = "/"
        print("File system reset.")

    def dict_to_folder(self, data):
        """Convert a dictionary to a Folder object."""
        folder = Folder(data["name"])
        for name, content in data["contents"].items():
            if content["type"] == "file":
                folder.contents[name] = File(content["name"], content["value"], content["password"])
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