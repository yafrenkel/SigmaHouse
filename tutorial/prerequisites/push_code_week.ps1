# push_code_week.ps1  -  lives in the prerequisites folder, pushes THIS folder to GitHub.
#
# Publishes the Code Week lessons to the repo your kid downloads from.
# Skips parent_guide.html (your private answer key) and this script itself.
#
# Run it (from anywhere):
#   powershell -ExecutionPolicy Bypass -File "C:\Projects\sigma\claude\tutorial\prerequisites\push_code_week.ps1"

$ErrorActionPreference = "Stop"

# ---------- EDIT THIS ONE LINE ----------
$RepoUrl = "https://github.com/irlglobe/code-week.git"
# ----------------------------------------

# This folder (where the lessons + this script live) is the SOURCE.
$Source = $PSScriptRoot
# A small working copy of the GitHub repo (created automatically).
$Repo = "C:\Projects\sigma\code-week"

if ($RepoUrl -like "*YOURNAME*") {
    Write-Host "STOP: edit the RepoUrl line near the top of this script first." -ForegroundColor Red
    exit 1
}

# 1. Get a local copy of the repo (clone the first time, reuse after)
if (-not (Test-Path (Join-Path $Repo ".git"))) {
    Write-Host "First run: cloning $RepoUrl" -ForegroundColor Cyan
    git clone $RepoUrl $Repo
}

# 2. Copy the kid-facing files in: every .html EXCEPT parent_guide.html, plus README.md.
Write-Host "Copying lessons from $Source" -ForegroundColor Cyan
Get-ChildItem $Source -Filter *.html | Where-Object { $_.Name -ne "parent_guide.html" } | Copy-Item -Destination $Repo -Force
Copy-Item (Join-Path $Source "README.md") $Repo -Force

# 2b. Make sure the private answer key never lands in this public repo
Remove-Item (Join-Path $Repo "parent_guide.html") -ErrorAction SilentlyContinue

Set-Location $Repo

# 3. Stage + show what changed
git add -A
Write-Host "Changes to be committed:" -ForegroundColor Cyan
git status --short

# 3b. Safety: parent_guide.html must NOT be tracked here
if (git ls-files | Select-String "parent_guide.html") {
    Write-Host "ABORT: parent_guide.html is in this repo. Remove it before pushing." -ForegroundColor Red
    exit 1
}

# 4. Confirm, commit, push
Write-Host ""
$confirm = Read-Host "Commit and push to GitHub? (Y/N)"
if ($confirm -eq "Y" -or $confirm -eq "y") {
    git commit -m "Update Code Week lessons"
    git push
    Write-Host ""
    Write-Host "Done. Repo updated - send the link to your kid." -ForegroundColor Green
} else {
    Write-Host "Skipped push. Nothing was sent to GitHub." -ForegroundColor Yellow
}
