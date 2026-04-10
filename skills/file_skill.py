import os
import shutil

class FileSkill:
    def __init__(self):
        pass
    
    def create_file(self, filepath, content=""):
        """Create a new file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Created file: {filepath}"
        except Exception as e:
            return f"Error creating file: {str(e)}"
    
    def read_file(self, filepath):
        """Read file contents"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def delete_file(self, filepath):
        """Delete a file"""
        try:
            os.remove(filepath)
            return f"Deleted file: {filepath}"
        except Exception as e:
            return f"Error deleting file: {str(e)}"
    
    def copy_file(self, source, destination):
        """Copy a file"""
        try:
            shutil.copy2(source, destination)
            return f"Copied {source} to {destination}"
        except Exception as e:
            return f"Error copying file: {str(e)}"
    
    def move_file(self, source, destination):
        """Move a file"""
        try:
            shutil.move(source, destination)
            return f"Moved {source} to {destination}"
        except Exception as e:
            return f"Error moving file: {str(e)}"
    
    def create_folder(self, folderpath):
        """Create a new folder"""
        try:
            os.makedirs(folderpath, exist_ok=True)
            return f"Created folder: {folderpath}"
        except Exception as e:
            return f"Error creating folder: {str(e)}"
    
    def list_files(self, folderpath="."):
        """List files in a folder"""
        try:
            files = os.listdir(folderpath)
            return files
        except Exception as e:
            return f"Error listing files: {str(e)}"
    
    def file_exists(self, filepath):
        """Check if file exists"""
        return os.path.exists(filepath)

# Test usage
if __name__ == "__main__":
    files = FileSkill()
    print(files.create_file("test.txt", "Hello from coco!"))
    print(files.read_file("test.txt"))
