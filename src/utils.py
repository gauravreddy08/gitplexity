from git import Repo
import os
import shutil

def clone(url: str, to_directory='root'):
    if os.path.exists(to_directory):
        shutil.rmtree(to_directory)
    os.makedirs(to_directory)
    try:
        Repo.clone_from(url, to_directory)
        return True
    except Exception as e:
        print(f"Invalid Git repository: {str(e)}")
        return False