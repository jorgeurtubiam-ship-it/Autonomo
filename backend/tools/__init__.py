"""
Tools Module - Inicialización
"""

# File Operations
from .file_tools import (
    ReadFileTool,
    WriteFileTool,
    ListDirectoryTool,
    SearchFilesTool,
    DeleteFileTool,
    GetFileInfoTool
)

# Command Execution
from .command_tools import (
    ExecuteCommandTool,
    RunScriptTool,
    InstallPackageTool
)

# Git Operations
from .git_tools import (
    GitStatusTool,
    GitDiffTool,
    GitCommitTool,
    GitLogTool
)

# HTTP Request
from .http_request import HttpRequestTool

# Browser Navigation
from .browser_tool import BrowserTool

# Vision
from .vision_tools import VisionTool, VisionPointTool

__all__ = [
    # File Operations
    "ReadFileTool",
    "WriteFileTool",
    "ListDirectoryTool",
    "SearchFilesTool",
    "DeleteFileTool",
    "GetFileInfoTool",
    
    # Command Execution
    "ExecuteCommandTool",
    "RunScriptTool",
    "InstallPackageTool",
    
    # Git Operations
    "GitStatusTool",
    "GitDiffTool",
    "GitCommitTool",
    "GitLogTool",
    
    # HTTP
    "HttpRequestTool",
    
    # Browser
    "BrowserTool",
    
    # Vision
    "VisionTool",
    "VisionPointTool",
]


def get_all_tools():
    """
    Retorna instancias de todos los tools disponibles
    
    Returns:
        Lista de tools
    """
    return [
        # File Operations
        ReadFileTool(),
        WriteFileTool(),
        ListDirectoryTool(),
        SearchFilesTool(),
        DeleteFileTool(),
        GetFileInfoTool(),
        
        # Command Execution
        ExecuteCommandTool(),
        RunScriptTool(),
        InstallPackageTool(),
        
        # Git Operations
        GitStatusTool(),
        GitDiffTool(),
        GitCommitTool(),
        GitLogTool(),
        
        # HTTP
        HttpRequestTool(),
        
        # Browser
        BrowserTool(),
        
        # Vision
        VisionTool(),
        VisionPointTool(),
    ]
