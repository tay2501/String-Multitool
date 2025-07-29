#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Build script for String_Multitool - Creates portable executable package

.DESCRIPTION
    This script creates a portable executable package for String_Multitool using PyInstaller.
    The resulting package includes all dependencies and can run on Windows systems without
    requiring Python installation.

.EXAMPLE
    .\build.ps1
    Creates a portable executable in the dist/ directory
#>

param(
    [switch]$Clean = $false,
    [switch]$Debug = $false
)

# Set error action preference
$ErrorActionPreference = "Stop"

Write-Host "🚀 String_Multitool Build Script" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Clean previous builds if requested
if ($Clean) {
    Write-Host "🧹 Cleaning previous builds..." -ForegroundColor Yellow
    if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
    if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
    if (Test-Path "*.spec") { Remove-Item -Force "*.spec" }
}

# Check if PyInstaller is installed
try {
    $pyinstallerVersion = python -m PyInstaller --version 2>$null
    Write-Host "✅ PyInstaller found: $pyinstallerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ PyInstaller not found. Installing..." -ForegroundColor Red
    python -m pip install pyinstaller
    Write-Host "✅ PyInstaller installed" -ForegroundColor Green
}

# Verify required files exist
$requiredFiles = @("String_Multitool.py", "config/transformation_rules.json", "config/security_config.json")
foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        Write-Host "❌ Required file not found: $file" -ForegroundColor Red
        exit 1
    }
}

Write-Host "✅ All required files found" -ForegroundColor Green

# Create build directory structure
Write-Host "📁 Creating build structure..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "dist/string-multitool-portable" | Out-Null

# Build executable with PyInstaller
Write-Host "🔨 Building executable..." -ForegroundColor Yellow

$pyinstallerArgs = @(
    "--onefile",
    "--name", "String_Multitool",
    "--distpath", "dist/string-multitool-portable",
    "--workpath", "build",
    "--add-data", "config;config",
    "--hidden-import", "cryptography",
    "--hidden-import", "pyperclip",
    "--console"
)

if ($Debug) {
    $pyinstallerArgs += "--debug", "all"
} else {
    $pyinstallerArgs += "--noconsole"
}

$pyinstallerArgs += "String_Multitool.py"

try {
    & python -m PyInstaller @pyinstallerArgs
    Write-Host "✅ Executable built successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Build failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Copy additional files to distribution
Write-Host "📋 Copying additional files..." -ForegroundColor Yellow

$additionalFiles = @(
    @{Source = "README.md"; Dest = "dist/string-multitool-portable/README.md"},
    @{Source = "LICENSE"; Dest = "dist/string-multitool-portable/LICENSE"},
    @{Source = "requirements.txt"; Dest = "dist/string-multitool-portable/requirements.txt"}
)

foreach ($file in $additionalFiles) {
    if (Test-Path $file.Source) {
        Copy-Item $file.Source $file.Dest -Force
        Write-Host "  ✅ Copied $($file.Source)" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  Optional file not found: $($file.Source)" -ForegroundColor Yellow
    }
}

# Create batch file for easy execution
$batchContent = @"
@echo off
cd /d "%~dp0"
String_Multitool.exe %*
pause
"@

$batchContent | Out-File -FilePath "dist/string-multitool-portable/run.bat" -Encoding ASCII
Write-Host "  ✅ Created run.bat" -ForegroundColor Green

# Create ZIP package
Write-Host "📦 Creating ZIP package..." -ForegroundColor Yellow
try {
    Compress-Archive -Path "dist/string-multitool-portable/*" -DestinationPath "dist/string-multitool-portable.zip" -Force
    Write-Host "✅ ZIP package created: dist/string-multitool-portable.zip" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to create ZIP package: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Display build summary
Write-Host ""
Write-Host "🎉 Build completed successfully!" -ForegroundColor Green
Write-Host "📁 Output directory: dist/string-multitool-portable/" -ForegroundColor Cyan
Write-Host "📦 ZIP package: dist/string-multitool-portable.zip" -ForegroundColor Cyan

# Display file sizes
$exeFile = "dist/string-multitool-portable/String_Multitool.exe"
$zipFile = "dist/string-multitool-portable.zip"

if (Test-Path $exeFile) {
    $exeSize = [math]::Round((Get-Item $exeFile).Length / 1MB, 2)
    Write-Host "📊 Executable size: $exeSize MB" -ForegroundColor Cyan
}

if (Test-Path $zipFile) {
    $zipSize = [math]::Round((Get-Item $zipFile).Length / 1MB, 2)
    Write-Host "📊 ZIP package size: $zipSize MB" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "🚀 Ready for distribution!" -ForegroundColor Green