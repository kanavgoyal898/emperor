from pathlib import Path

def resolve_absolute_path(path: str) -> Path:
    """
        Resolves a given path to an absolute path. 
        If the path is relative, it is resolved against the current working directory.

        Example:
        file.txt -> /Users/username/.../file.txt
    """
    
    path = Path(path).expanduser()
    if not path.is_absolute():
        path = (Path.cwd() / path).resolve()
    return path
