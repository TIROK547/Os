import json
import os
from typing import Dict, Union, List, Optional


class File:
    """Represents a file in the file system."""

    def __init__(
        self, name: str, value: list = [], password: Optional[str] = None
    ) -> None:
        """
        Initialize a File object.

        Args:
            name (str): The name of the file.
            value (str, optional): The content of the file. Defaults to "".
            password (Optional[str], optional): Password to protect the file. Defaults to None.
        """
        self.name = name
        self.value = value
        self.password = password

    def get_value(self) -> str:
        """Return the content of the file as a string."""
        return self.value

    def set_value(self, value: str) -> None:
        """
        Set the content of the file.

        Args:
            value (str): The new content of the file.
        """
        self.value = value

    def to_dict(self) -> Dict[str, Union[str, None]]:
        """Convert the File object to a dictionary for serialization."""
        return {
            "name": self.name,
            "value": self.value,
            "type": "file",
            "password": self.password,
        }


class Folder:
    """Represents a folder in the file system."""

    def __init__(self, name: str, password: Optional[str] = None) -> None:
        """
        Initialize a Folder object.

        Args:
            name (str): The name of the folder.
            password (Optional[str], optional): Password to protect the folder. Defaults to None.
        """
        self.name = name
        self.contents: Dict[str, Union[File, "Folder"]] = {}
        self.password = password

    def to_dict(self) -> Dict[str, Union[str, Dict]]:
        """Convert the Folder object to a dictionary for serialization."""
        return {
            "name": self.name,
            "type": "folder",
            "password": self.password,
            "contents": {key: value.to_dict() for key, value in self.contents.items()},
        }


class FileSystem:
    """Represents a file system with folders and files."""

    def __init__(self, save_file: str = "filesystem.json") -> None:
        """
        Initialize the FileSystem object.

        Args:
            save_file (str, optional): The file to save/load the file system state. Defaults to "filesystem.json".
        """
        self.root = Folder("/")
        self.current_folder = self.root
        self.path = "/"
        self.save_file = save_file
        self.load()

    def execute(self, command: str) -> None:
        """
        Execute a command in the file system.

        Args:
            command (str): The command to execute.
        """
        parts = command.strip().split()
        if not parts:
            return
        cmd = parts[0]
        args = parts[1:]
        if cmd == "mkdir" and args:
            self.mkdir([args[0]])
        elif cmd == "cd" and args:
            self.cd(args[0])
        elif cmd == "ls":
            self.ls(args[0] if args else None)
        elif command == "clear":
            self.clear()
            print("data cleared")
            self.load()
        elif cmd == "cat" and args:
            print("\n".join(self.cat(args[0])))
        elif cmd == "rm" and args:
            self.rm(args[0])
        elif cmd == "edit_name":
            self.edit_name(args)
        elif cmd == "cp" and args:
            self.cp(args)
        elif cmd == "mv":
            self.mv(args)
        elif cmd == "edit_file":
            self.edit_line(args)
        elif cmd == "fragment":
            self.fragment(args)
        elif cmd == "save":
            self.save()
            print("File system saved.")
        elif cmd == "search":
            self.search(args)
        else:
            print("Command not found")

    def check_password(self, item: Union[File, Folder], item_name: str) -> bool:
        """
        Check if the item is password-protected and verify the password.

        Args:
            item (Union[File, Folder]): The item to check.
            item_name (str): The name of the item.

        Returns:
            bool: True if the password is correct or not required, False otherwise.
        """
        if item.password:
            password = input(f"Enter password for {item_name}: ")
            if password != item.password:
                print("Incorrect password")
                return False
        return True

    def cp(self, args: List[str]):
        if not args:
            print("Usage: cp <source> <destination>")
            return
        elif len(args) != 2:
            print("Usage: cp <source> <destination>")
            return
        copy_data = self.cat(args[0])
        self.mkdir([args[1]], copy_data)

    def mv(self, args: List[str]):
        if not args:
            print("Usage: mv <source> <destination>")
            return
        elif len(args) != 2:
            print("Usage: mv <source> <destination>")
            return
        copy_data = self.cat(args[0])
        self.mkdir([args[1]], copy_data)
        self.rm(args[0])

    def fragment(self, argsL: list) -> None:
        if not argsL:
            print("Usage: fragment <source>")
            return
        args = argsL[0]
        new_val = self.current_folder.contents[args].get_value()
        del_indexes = [i for i, line in enumerate(new_val) if line.strip() == ""]

        for index in reversed(del_indexes):
            del new_val[index]

        self.current_folder.contents[args].set_value(new_val)

    def mkdir(self, args: List[str], inp_value: list = []) -> None:
        """
        Create a file or folder.

        Args:
            args (List[str]): The arguments for the command, including name and optional value.
        """

        if not args:
            print("Usage: mkdir <name> [value]")
            return
        value = inp_value
        name = args[0]
        last_line = ""
        path_elements = (
            " ".join(name.split("/")).strip().split(" ")
        )  #! من خدای تکنولوژیم
        file_password = None

        temp = self.current_folder

        if name.startswith("/"):
            self.current_folder = self.root

        for i in range(len(path_elements) - 1):
            if path_elements[i].startswith("."):
                file_password = input(f"Set password for {path_elements[i]}: ")

            if not self.check_password(self.current_folder, path_elements[i]):
                return
            if path_elements[i] not in self.current_folder.contents:
                self.current_folder.contents[path_elements[i]] = Folder(
                    path_elements[i], file_password
                )
            self.current_folder = self.current_folder.contents[path_elements[i]]
            file_password = None

        if path_elements[-1].startswith("."):
            file_password = input(f"Set password for {name}: ")

        final_name = path_elements[-1]
        is_hidden_folder = final_name.startswith(".") and "." not in final_name[1:]
        is_file = "." in final_name and not is_hidden_folder
        if value and is_file:
            print("Value provided. Skipping input.")
            self.current_folder.contents[final_name] = File(
                final_name, value, file_password
            )
        elif is_file:
            while last_line != ".":
                last_line = input(f"Enter value for {name} (press . to stop): ")
                if last_line != ".":
                    value.append(last_line)
            self.current_folder.contents[final_name] = File(
                final_name, value, file_password
            )
        else:
            self.current_folder.contents[final_name] = Folder(final_name, file_password)

        inp_value = []
        self.current_folder = temp
        self.save()

    def cat(self, filename: str) -> None:
        """
        Display the contents of a file.

        Args:
            filename (str): The name of the file to display.
        """
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
                return f"Invalid path: {filename}"

        final_name = path[-1]
        if final_name in current.contents and isinstance(
            current.contents[final_name], File
        ):
            file = current.contents[final_name]
            if not self.check_password(file, final_name):
                return
            return file.get_value()
        else:
            return f"{filename} is not a file or does not exist"

    def cd(self, folder_name: str) -> None:
        """
        Change the current directory.

        Args:
            folder_name (str): The name of the folder to navigate to.
        """
        if folder_name == "/":
            self.current_folder = self.root
            self.path = "/"
            return

        path_elements = folder_name.strip("/").split("/")
        temp_folder = self.root if folder_name.startswith("/") else self.current_folder
        temp_path = "/" if folder_name.startswith("/") else self.path

        for part in path_elements:
            if part == "..":
                if temp_path != "/":
                    temp_path = "/".join(temp_path.strip("/").split("/")[:-1]) or "/"
                    temp_folder = self.navigate_to_folder(temp_path)
            elif part in temp_folder.contents and isinstance(
                temp_folder.contents[part], Folder
            ):
                if not self.check_password(temp_folder.contents[part], part):
                    return
                temp_folder = temp_folder.contents[part]
                temp_path = (temp_path.rstrip("/") + "/" + part).replace("//", "/")
            else:
                print(f"No such folder: {folder_name}")
                return

        self.current_folder = temp_folder
        self.path = temp_path

    def navigate_to_folder(self, path: str) -> Folder:
        """
        Navigate to a folder based on the given path.

        Args:
            path (str): The path to navigate to.

        Returns:
            Folder: The folder at the specified path.
        """
        parts = path.strip("/").split("/")
        current = self.root
        for part in parts:
            if part:
                current = current.contents.get(part, current)
        return current

    def search(self, argsL: Optional[str] = None):
        args = argsL

        if len(args) < 1:
            print("Usage: search <path> [type]")
            return
        if len(args) < 2:
            args.append(args[0])
            args[0] = self.path

        path = args[0].strip().split("/")
        if args[0].startswith("/"):
            current = self.root
            path = args[0][1:].strip().split("/")
        else:
            current = self.current_folder

        for part in path:
            if part in current.contents and isinstance(current.contents[part], Folder):
                folder = current.contents[part]
                if not self.check_password(folder, part):
                    return
                current = folder
            else:
                print(f"Invalid path: {args[0]}")
                return
        file_type = args[1]
        if not file_type.startswith("."):
            file_type = "." + file_type
        if len(" ".join(file_type.split(".")).strip().split()) != 1:
            print("Usage: search <path> [type]")
            return
        files = current.contents.keys()
        res = []
        for file in files:
            temp = file.split(".")
            if len(temp) != 2:
                break
            if "." + temp[1] == file_type:
                res.append(file)
        print(" | ".join(res))

    def edit_name(self, args: List[str]) -> None:
        """
        Rename a file or folder.

        Args:
            args (List[str]): The arguments for the command. Should contain [current_name, new_name].
        """
        if len(args) != 2:
            print("Usage: edit_name <current_name> <new_name>")
            return

        current_name, new_name = args
        if current_name not in self.current_folder.contents:
            print(f"No such file or folder: {current_name}")
            return

        item = self.current_folder.contents[current_name]

        if not self.check_password(item, current_name):
            return

        if new_name in self.current_folder.contents:
            print(f"A file or folder with the name '{new_name}' already exists.")
            return

        self.current_folder.contents[new_name] = self.current_folder.contents.pop(
            current_name
        )
        self.current_folder.contents[new_name].name = new_name

        # Save changes
        self.save()
        print(f"Renamed '{current_name}' to '{new_name}'")

    def ls(self, filename: Optional[str] = None) -> None:
        """
        List the contents of a folder.

        Args:
            filename (Optional[str], optional): The folder to list. Defaults to the current folder.
        """
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
                if part in current.contents and isinstance(
                    current.contents[part], Folder
                ):
                    folder = current.contents[part]
                    if not self.check_password(folder, part):
                        return
                    current = folder
                else:
                    print(f"Invalid path: {filename}")
                    return

            print(" | ".join(current.contents.keys()))

    def edit_line(self, argsL: list):
        if not argsL:
            print("Usage: edit_line <source>")
            return
        args = argsL[0]
        new_val = self.current_folder.contents[args].get_value()
        changing_index = int(
            input(f"what line of {args[-1]} do you want to change? (1-{len(new_val)}):")
        )
        print(f"Your current value is: {new_val[changing_index-1]}")
        new_text = input("Please enter your new value: ")
        new_val[changing_index - 1] = f"{new_text}"
        self.current_folder.contents[args].set_value(new_val)

    def rm(self, filename: str) -> None:
        """
        Remove a file or folder.

        Args:
            filename (str): The name of the file or folder to remove.
        """
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

    def to_dict(self) -> Dict[str, Union[str, Dict]]:
        """Convert the file system to a dictionary for saving."""
        return {"root": self.root.to_dict(), "path": self.path}

    def save(self) -> None:
        """Save the file system to a file."""
        with open(self.save_file, "w") as f:
            json.dump(self.to_dict(), f, indent=4)

    def load(self) -> None:
        """Load the file system from a file."""
        if os.path.exists(self.save_file):
            with open(self.save_file, "r") as f:
                data = json.load(f)
                self.root = self.dict_to_folder(data["root"])
                self.current_folder = self.navigate_to_folder(data["path"])
                self.path = data["path"]

    def clear(self) -> None:
        """Reset the file system to its initial state."""
        if os.path.exists(self.save_file):
            os.remove(self.save_file)
        self.root = Folder("/")
        self.current_folder = self.root
        self.path = "/"
        print("File system reset.")

    def dict_to_folder(self, data: Dict) -> Folder:
        """
        Convert a dictionary to a Folder object.

        Args:
            data (Dict): The dictionary representation of the folder.

        Returns:
            Folder: The reconstructed Folder object.
        """
        folder = Folder(data["name"])
        for name, content in data["contents"].items():
            if content["type"] == "file":
                folder.contents[name] = File(
                    content["name"], content["value"], content["password"]
                )
            else:
                folder.contents[name] = self.dict_to_folder(content)
        return folder


def main() -> None:
    """Main function to run the file system simulation."""
    fs = FileSystem()
    while True:
        command = input(f"{fs.path} >>> ")
        if command.lower() == "exit":
            fs.save()
            print("File system saved. Exiting...")
            break
        fs.execute(command)


if __name__ == "__main__":
    main()

#!mv ask for password twice
