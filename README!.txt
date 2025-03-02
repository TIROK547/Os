# File System Simulator

This project is a Python-based file system simulator that allows users to execute commands similar to those in a Linux-like environment. The file system supports creating, modifying, and managing files and folders with password protection.

## Features
- **Create files and folders** (`mkdir`)
- **Navigate directories** (`cd`)
- **List directory contents** (`ls`)
- **View file contents** (`cat`)
- **Edit file contents** (`edit_file`)
- **Rename files or folders** (`edit_name`)
- **Copy and move files** (`cp`, `mv`)
- **Delete files or folders** (`rm`)
- **Search for files by type or name** (`search`)
- **Save and load the file system state** (`save`, `load`)
- **Reset the file system** (`clear`)

## Installation & Setup
No additional dependencies are required. Simply run the script using Python:
```sh
python filesystem.py
```

## Usage
Upon running the script, you can use the command-line interface to interact with the file system.

### Example Commands:
```sh
mkdir my_folder        # Create a folder named 'my_folder'
cd my_folder          # Navigate into 'my_folder'
mkdir my_file.txt     # Create a file named 'my_file.txt'
edit_file my_file.txt # Edit 'my_file.txt' line by line
ls                    # List contents of the current directory
cat my_file.txt       # Display contents of 'my_file.txt'
mv my_file.txt /      # Move 'my_file.txt' to the root directory
rm my_file.txt        # Remove 'my_file.txt'
search .txt           # Search for all .txt files
```

## Password Protection
- Files and folders with names starting with `.` will be password-protected.
- Users will be prompted to enter a password when accessing protected files or folders.

## Saving & Loading
- The file system automatically saves state to `filesystem.json`.
- Use the `save` command to manually save the file system.
- Use the `load` command to reload the file system state.
- The system state is loaded on startup.
- To reset the file system, use the `clear` command.

## Exit
To exit the simulator and save the current file system state, use:
```sh
exit
```

## Known Issues
- empty

## License
This project is open-source and free to use.

