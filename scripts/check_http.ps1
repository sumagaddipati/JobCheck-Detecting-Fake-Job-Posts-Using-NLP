try {
    $r = Invoke-WebRequest -Uri http://127.0.0.1:5000 -UseBasicParsing -TimeoutSec 5
    Write-Host "status $($r.StatusCode)"
} catch {
    Write-Host "error $($_.Exception.Message)"
}