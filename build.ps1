#Requires -Version 5.1
<#
.SYNOPSIS
    Enterprise-grade build script for String_Multitool

.DESCRIPTION
    This script creates a portable executable package for String_Multitool using PyInstaller.
    Designed for CI/CD environments with comprehensive error handling and logging.

.PARAMETER Clean
    Remove previous build artifacts before building

.PARAMETER Debug
    Enable debug mode for PyInstaller

.PARAMETER OutputPath
    Specify custom output directory (default: dist)

.PARAMETER SkipTests
    Skip running tests before building

.EXAMPLE
    .\build.ps1
    Standard build with default settings

.EXAMPLE
    .\build.ps1 -Clean -DebugMode
    Clean build with debug information

.NOTES
    Author: String_Multitool Development Team
    Version: 2.0.0
    Requires: PowerShell 5.1+, Python 3.10+
#>

[CmdletBinding()]
param(
    [Parameter(HelpMessage = "Clean previous build artifacts")]
    [switch]$Clean,
    
    [Parameter(HelpMessage = "Enable debug mode")]
    [switch]$DebugMode,
    
    [Parameter(HelpMessage = "Output directory path")]
    [ValidateNotNullOrEmpty()]
    [string]$OutputPath = "dist",
    
    [Parameter(HelpMessage = "Skip running tests")]
    [switch]$SkipTests
)

# Configuration
$script:Config = @{
    AppName = "String_Multitool"
    Version = "2.2.0"
    OutputDir = $OutputPath
    PortableDir = "string-multitool-portable"
    RequiredFiles = @(
        "String_Multitool.py",
        "config/transformation_rules.json", 
        "config/security_config.json"
    )
    OptionalFiles = @(
        @{ Source = "README.md"; Dest = "README.md" },
        @{ Source = "LICENSE"; Dest = "LICENSE" },
        @{ Source = "ARCHITECTURE.md"; Dest = "ARCHITECTURE.md" }
    )
    PyInstallerArgs = @(
        "--onefile",
        "--console",
        "--optimize", "2"
    )
}

# Set strict error handling
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

#region Helper Functions

function Write-BuildLog {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Message,
        
        [Parameter()]
        [ValidateSet("Info", "Success", "Warning", "Error")]
        [string]$Level = "Info"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $colors = @{
        Info = "Cyan"
        Success = "Green" 
        Warning = "Yellow"
        Error = "Red"
    }
    
    $prefix = switch ($Level) {
        "Info" { "[INFO]" }
        "Success" { "[PASS]" }
        "Warning" { "[WARN]" }
        "Error" { "[FAIL]" }
    }
    
    Write-Host "[$timestamp] $prefix $Message" -ForegroundColor $colors[$Level]
}

function Test-Prerequisites {
    [CmdletBinding()]
    param()
    
    Write-BuildLog "Checking prerequisites..." -Level Info
    
    # Check Python installation
    try {
        $pythonVersion = python --version 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw "Python not found in PATH"
        }
        Write-BuildLog "Python found: $pythonVersion" -Level Success
    }
    catch {
        Write-BuildLog "Python is required but not found in PATH" -Level Error
        throw
    }
    
    # Check required files
    foreach ($file in $script:Config.RequiredFiles) {
        if (-not (Test-Path $file)) {
            Write-BuildLog "Required file not found: $file" -Level Error
            throw "Missing required file: $file"
        }
    }
    Write-BuildLog "All required files found" -Level Success
    
    # Check/Install PyInstaller
    try {
        $pyinstallerVersion = python -m PyInstaller --version 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw "PyInstaller not found"
        }
        Write-BuildLog "PyInstaller found: $pyinstallerVersion" -Level Success
    }
    catch {
        Write-BuildLog "Installing PyInstaller..." -Level Warning
        uv add --dev pyinstaller
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to install PyInstaller"
        }
        Write-BuildLog "PyInstaller installed successfully" -Level Success
    }
}

function Invoke-CleanBuild {
    [CmdletBinding()]
    param()
    
    Write-BuildLog "Cleaning previous build artifacts..." -Level Info
    
    $pathsToClean = @("build", $script:Config.OutputDir, "*.spec")
    
    foreach ($path in $pathsToClean) {
        if (Test-Path $path) {
            try {
                Remove-Item $path -Recurse -Force -ErrorAction Stop
                Write-BuildLog "Removed: $path" -Level Success
            }
            catch {
                Write-BuildLog "Failed to remove: $path - $($_.Exception.Message)" -Level Warning
            }
        }
    }
}

function Invoke-Tests {
    [CmdletBinding()]
    param()
    
    if ($SkipTests) {
        Write-BuildLog "Skipping tests as requested" -Level Warning
        return
    }
    
    Write-BuildLog "Running tests..." -Level Info
    
    try {
        python -m pytest test_transform.py -v --tb=short
        if ($LASTEXITCODE -ne 0) {
            throw "Tests failed"
        }
        Write-BuildLog "All tests passed" -Level Success
    }
    catch {
        Write-BuildLog "Test execution failed: $($_.Exception.Message)" -Level Error
        throw
    }
}

function New-ExecutablePackage {
    [CmdletBinding()]
    param()
    
    Write-BuildLog "Building executable package..." -Level Info
    
    # Create output directory
    $fullOutputPath = Join-Path $script:Config.OutputDir $script:Config.PortableDir
    New-Item -ItemType Directory -Force -Path $fullOutputPath | Out-Null
    
    # Prepare PyInstaller arguments
    $pyinstallerArgs = $script:Config.PyInstallerArgs + @(
        "--name", $script:Config.AppName,
        "--distpath", $fullOutputPath,
        "--workpath", "build",
        "--add-data", "config;config",
        "--hidden-import", "cryptography",
        "--hidden-import", "pyperclip",
        "--hidden-import", "threading",
        "--hidden-import", "json"
    )
    
    if ($DebugMode) {
        $pyinstallerArgs += @("--log-level", "DEBUG")
        Write-BuildLog "Debug mode enabled" -Level Info
    }
    
    $pyinstallerArgs += "String_Multitool.py"
    
    # Execute PyInstaller
    try {
        Write-BuildLog "Executing PyInstaller with args: $($pyinstallerArgs -join ' ')" -Level Info
        & python -m PyInstaller @pyinstallerArgs
        
        if ($LASTEXITCODE -ne 0) {
            throw "PyInstaller execution failed with exit code $LASTEXITCODE"
        }
        
        Write-BuildLog "Executable built successfully" -Level Success
    }
    catch {
        Write-BuildLog "Build failed: $($_.Exception.Message)" -Level Error
        throw
    }
}

function Copy-AdditionalFiles {
    [CmdletBinding()]
    param()
    
    Write-BuildLog "Copying additional files..." -Level Info
    
    $destinationBase = Join-Path $script:Config.OutputDir $script:Config.PortableDir
    
    foreach ($fileInfo in $script:Config.OptionalFiles) {
        $sourcePath = $fileInfo.Source
        $destPath = Join-Path $destinationBase $fileInfo.Dest
        
        if (Test-Path $sourcePath) {
            try {
                Copy-Item $sourcePath $destPath -Force
                Write-BuildLog "Copied: $sourcePath -> $($fileInfo.Dest)" -Level Success
            }
            catch {
                Write-BuildLog "Failed to copy $sourcePath : $($_.Exception.Message)" -Level Warning
            }
        }
        else {
            Write-BuildLog "Optional file not found: $sourcePath" -Level Warning
        }
    }
}

function New-LauncherScript {
    [CmdletBinding()]
    param()
    
    Write-BuildLog "Creating launcher script..." -Level Info
    
    $destinationBase = Join-Path $script:Config.OutputDir $script:Config.PortableDir
    $batchPath = Join-Path $destinationBase "run.bat"
    
    # Create batch file content as array to avoid Here-String issues
    $batchLines = @(
        "@echo off",
        "cd /d `"%~dp0`"",
        "$($script:Config.AppName).exe %*",
        "if errorlevel 1 (",
        "    echo.",
        "    echo An error occurred. Press any key to exit...",
        "    pause >nul",
        ")"
    )
    
    try {
        $batchLines | Out-File -FilePath $batchPath -Encoding ASCII -Force
        Write-BuildLog "Launcher script created: run.bat" -Level Success
    }
    catch {
        Write-BuildLog "Failed to create launcher script: $($_.Exception.Message)" -Level Error
        throw
    }
}

function New-ZipPackage {
    [CmdletBinding()]
    param()
    
    Write-BuildLog "Creating ZIP package..." -Level Info
    
    $sourcePath = Join-Path $script:Config.OutputDir $script:Config.PortableDir
    $zipPath = Join-Path $script:Config.OutputDir "$($script:Config.PortableDir).zip"
    
    try {
        # Remove existing ZIP if present
        if (Test-Path $zipPath) {
            Remove-Item $zipPath -Force
        }
        
        Compress-Archive -Path "$sourcePath\*" -DestinationPath $zipPath -Force
        Write-BuildLog "ZIP package created: $zipPath" -Level Success
    }
    catch {
        Write-BuildLog "Failed to create ZIP package: $($_.Exception.Message)" -Level Error
        throw
    }
}

function Show-BuildSummary {
    [CmdletBinding()]
    param()
    
    Write-BuildLog "Build Summary" -Level Info
    Write-Host "=" * 50 -ForegroundColor Cyan
    
    $outputDir = Join-Path $script:Config.OutputDir $script:Config.PortableDir
    $zipFile = Join-Path $script:Config.OutputDir "$($script:Config.PortableDir).zip"
    $exeFile = Join-Path $outputDir "$($script:Config.AppName).exe"
    
    Write-Host "Output Directory: $outputDir" -ForegroundColor Cyan
    Write-Host "ZIP Package: $zipFile" -ForegroundColor Cyan
    
    # Display file sizes
    if (Test-Path $exeFile) {
        $exeSize = [math]::Round((Get-Item $exeFile).Length / 1MB, 2)
        Write-Host "Executable Size: $exeSize MB" -ForegroundColor Cyan
    }
    
    if (Test-Path $zipFile) {
        $zipSize = [math]::Round((Get-Item $zipFile).Length / 1MB, 2)
        Write-Host "ZIP Package Size: $zipSize MB" -ForegroundColor Cyan
    }
    
    Write-Host "Build Version: $($script:Config.Version)" -ForegroundColor Cyan
    Write-Host "Build Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
}

#endregion

#region Main Execution

function Invoke-Build {
    [CmdletBinding()]
    param()
    
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    
    try {
        Write-Host "String_Multitool Enterprise Build System v2.0" -ForegroundColor Magenta
        Write-Host "=" * 60 -ForegroundColor Magenta
        
        # Execute build pipeline
        Test-Prerequisites
        
        if ($Clean) {
            Invoke-CleanBuild
        }
        
        Invoke-Tests
        New-ExecutablePackage
        Copy-AdditionalFiles
        New-LauncherScript
        New-ZipPackage
        
        $stopwatch.Stop()
        
        Write-BuildLog "Build completed successfully in $($stopwatch.Elapsed.TotalSeconds.ToString('F2')) seconds" -Level Success
        Show-BuildSummary
        
        Write-Host "`nReady for distribution!" -ForegroundColor Green
    }
    catch {
        $stopwatch.Stop()
        Write-BuildLog "Build failed after $($stopwatch.Elapsed.TotalSeconds.ToString('F2')) seconds" -Level Error
        Write-BuildLog "Error: $($_.Exception.Message)" -Level Error
        
        if ($_.Exception.InnerException) {
            Write-BuildLog "Inner Exception: $($_.Exception.InnerException.Message)" -Level Error
        }
        
        exit 1
    }
}

# Execute main build function
Invoke-Build

#endregion