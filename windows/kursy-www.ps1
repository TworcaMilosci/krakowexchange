# kursy-www.ps1
# Wysyla kursy z C:\Tablica\kursy.js na strone kantorblacksheep.pl po kazdej zmianie.
# Niczego nie zmienia w programie KANTOR ani w tablicy: tylko czyta plik kursy.js.
# Klucz: plik C:\Tablica\www-klucz.txt (jedna linia, ten sam klucz co sekret RATES_PUSH_KEY w Cloudflare).
# Dziennik: C:\Tablica\kursy-www.log

$dir     = 'C:\Tablica'
$src     = Join-Path $dir 'kursy.js'
$keyFile = Join-Path $dir 'www-klucz.txt'
$log     = Join-Path $dir 'kursy-www.log'
$url     = 'https://kantorblacksheep.pl/api/push-rates'

[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

function Write-Log([string]$msg) {
    $line = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') + '  ' + $msg
    try {
        Add-Content -Path $log -Value $line -Encoding UTF8
        $all = Get-Content -Path $log -Encoding UTF8
        if ($all.Count -gt 400) { $all | Select-Object -Last 200 | Set-Content -Path $log -Encoding UTF8 }
    } catch { }
}

function Get-RatesPart([string]$text) {
    # porownujemy tylko czesc z kursami, zeby sama zmiana godziny w pliku nie powodowala wysylki
    $i = $text.IndexOf('rates')
    if ($i -lt 0) { return $text }
    return $text.Substring($i)
}

Write-Log 'start'
$lastSent = ''
$nextTry  = Get-Date

while ($true) {
    try {
        if ((Test-Path $src) -and (Test-Path $keyFile) -and ((Get-Date) -ge $nextTry)) {
            $text  = [IO.File]::ReadAllText($src, [Text.Encoding]::UTF8)
            $rates = Get-RatesPart $text
            if ($rates -ne $lastSent -and $text.Length -gt 20) {
                $key   = ([IO.File]::ReadAllText($keyFile)).Trim()
                $bytes = [Text.Encoding]::UTF8.GetBytes($text)
                try {
                    $resp = Invoke-WebRequest -Uri $url -Method Post -Body $bytes -ContentType 'text/plain; charset=utf-8' -Headers @{ Authorization = "Bearer $key" } -UseBasicParsing -TimeoutSec 20
                    Write-Log ('wyslano: ' + $resp.Content)
                    $lastSent = $rates
                } catch {
                    $body = ''
                    try {
                        $stream = $_.Exception.Response.GetResponseStream()
                        $reader = New-Object IO.StreamReader($stream, [Text.Encoding]::UTF8)
                        $body   = $reader.ReadToEnd()
                    } catch { }
                    $code = 0
                    try { $code = [int]$_.Exception.Response.StatusCode } catch { }
                    Write-Log ('BLAD ' + $code + ': ' + $_.Exception.Message + ' ' + $body)
                    if ($code -eq 422) {
                        # strona odrzucila te kursy (np. literowka): nie ponawiamy, czekamy na poprawke w programie
                        $lastSent = $rates
                    } else {
                        # brak internetu, zly klucz itp.: ponow za minute
                        $nextTry = (Get-Date).AddSeconds(60)
                    }
                }
            }
        }
    } catch {
        Write-Log ('BLAD skryptu: ' + $_.Exception.Message)
        $nextTry = (Get-Date).AddSeconds(60)
    }
    Start-Sleep -Seconds 5
}
