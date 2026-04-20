# Kapila Invoice - Remote Access Setup
# Run this script to access your invoice app from mobile

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Kapila Invoice - Remote Access Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if ngrok exists
$ngrokPath = ".\ngrok\ngrok.exe"

if (Test-Path $ngrokPath) {
    Write-Host "[OK] ngrok found" -ForegroundColor Green
} else {
    Write-Host "[STEP 1] Downloading ngrok..." -ForegroundColor Yellow
    Write-Host "This may take a minute..."
    
    try {
        Invoke-WebRequest -Uri "https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-windows-amd64.zip" -OutFile "ngrok.zip" -ErrorAction Stop
        Expand-Archive -Path "ngrok.zip" -DestinationPath "ngrok" -Force
        Remove-Item "ngrok.zip" -Force
        Write-Host "[OK] ngrok installed" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Failed to download ngrok" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host ""
Write-Host "[STEP 2] Starting Flask server on port 5001..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python app.py" -WindowStyle Normal

# Wait for Flask to start
Write-Host "Waiting for Flask to start..."
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "[STEP 3] Starting ngrok tunnel..." -ForegroundColor Yellow
Write-Host ""

# Start ngrok and capture output
$ngrokProcess = Start-Process -FilePath ".\ngrok\ngrok.exe" -ArgumentList "http 5001" -NoNewWindow -PassThru -RedirectStandardOutput "ngrok_output.txt"

# Wait a bit for ngrok to initialize
Start-Sleep -Seconds 3

# Read the output file to get the URL
$ngrokUrl = ""
$maxAttempts = 15
$attempt = 0

Write-Host "Looking for your public URL..." -ForegroundColor Cyan

while ($attempt -lt $maxAttempts) {
    Start-Sleep -Seconds 1
    $attempt++
    
    if (Test-Path "ngrok_output.txt") {
        $content = Get-Content "ngrok_output.txt" -Raw -ErrorAction SilentlyContinue
        if ($content -match "https://[a-zA-Z0-9]+\.ngrok\.io") {
            $ngrokUrl = $matches[0]
            break
        }
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  YOUR PUBLIC URL:" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  $ngrokUrl" -ForegroundColor Yellow -BackgroundColor Black
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "INSTRUCTIONS:" -ForegroundColor Cyan
Write-Host "1. Open the URL above on your MOBILE PHONE" -ForegroundColor White
Write-Host "2. You can access from ANYWHERE (not just WiFi)!" -ForegroundColor White
Write-Host "3. Login with: admin / admin123" -ForegroundColor White
Write-Host ""
Write-Host "IMPORTANT:" -ForegroundColor Yellow
Write-Host "- Keep this window open to maintain the connection" -ForegroundColor White
Write-Host "- Each time you restart, you get a NEW URL" -ForegroundColor White
Write-Host "- To stop: Close this window or press Ctrl+C in ngrok window" -ForegroundColor White
Write-Host ""

Write-Host "Press Enter to open URL in browser..."
Read-Host

# Try to open in default browser
Start-Process $ngrokUrl

