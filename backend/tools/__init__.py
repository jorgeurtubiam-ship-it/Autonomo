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

# Zabbix
from .zabbix_tools import ZabbixTool

# Rundeck
from .rundeck_tools import RundeckTool, RundeckListTool

# Analysis
from .analysis_tools import InfrastructureAnalysisTool

# OCI
from .oci_tools import OCITool

# Checkmk
from .checkmk_tools import CheckmkTool, CheckmkListHostsTool

# Dremio
from .dremio_tools import DremioQueryTool, DremioCatalogTool

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
    
    # Zabbix
    "ZabbixTool",
    
    # Rundeck
    "RundeckTool",
    "RundeckListTool",
    
    # Analysis
    "InfrastructureAnalysisTool",
    
    # OCI
    "OCITool",
    
    # Checkmk
    "CheckmkTool",
    "CheckmkListHostsTool",
    
    # Dremio
    "DremioQueryTool",
    "DremioCatalogTool",
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
        
        # Zabbix
        ZabbixTool(),
        
        # Rundeck
        RundeckTool(),
        RundeckListTool(),
        
        # Analysis
        InfrastructureAnalysisTool(),
        
        # OCI
        OCITool(),
        
        # Checkmk
        CheckmkTool(),
        CheckmkListHostsTool(),
        
        # Dremio
        DremioQueryTool(),
        DremioCatalogTool(),
    ]
