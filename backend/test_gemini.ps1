$ErrorActionPreference = "Stop"
try {
    Write-Host "1. Creando historia..."
    $body = @{theme="espacio exterior"} | ConvertTo-Json
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/story/create" -Method Post -Body $body -ContentType "application/json"
    $jobId = $response.job_id
    Write-Host "   Job ID: $jobId"

    for ($i = 0; $i -lt 20; $i++) {
        Start-Sleep -Seconds 3
        $statusResp = Invoke-RestMethod -Uri "http://localhost:8000/api/job/$jobId" -Method Get
        $status = $statusResp.status
        Write-Host "   Intento $($i+1): Estado = $status"

        if ($status -eq "completado") {
            Write-Host "   ¡Éxito! Historia generada. ID: $($statusResp.story_id)"
            exit 0
        }
        if ($status -eq "error") {
            Write-Host "   Error: $($statusResp.error)"
            exit 1
        }
    }
    Write-Host "   Tiempo agotado."
} catch {
    Write-Host "   Error: $_"
    exit 1
}
