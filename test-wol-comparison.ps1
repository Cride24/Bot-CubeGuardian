# Script de test et comparaison Wake-on-LAN
# Compare le bot avec wakemeonlan-x64

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "TEST ET COMPARAISON WAKE-ON-LAN" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# Configuration du serveur
$MacAddress = "00:23:7D:FD:C0:5C"
$TargetHost = "192.168.1.245"

Write-Host "Adresse MAC: $MacAddress" -ForegroundColor Yellow
Write-Host "Adresse IP: $TargetHost" -ForegroundColor Yellow
Write-Host ""

# Fonction pour envoyer Magic Packet avec PowerShell
function Send-WakeOnLAN-PowerShell {
    param(
        [string]$MacAddress,
        [string]$BroadcastAddress = "255.255.255.255"
    )
    
    try {
        # Nettoyer l'adresse MAC
        $MacAddress = $MacAddress -replace '[^0-9A-F]', ''
        
        # Creer le Magic Packet
        $MagicPacket = [byte[]](,0xFF * 6)
        for ($i = 0; $i -lt 16; $i++) {
            for ($j = 0; $j -lt 6; $j += 2) {
                $MagicPacket += [byte][Convert]::ToInt16($MacAddress.Substring($j, 2), 16)
            }
        }
        
        # Envoyer le paquet
        $UdpClient = New-Object System.Net.Sockets.UdpClient
        $UdpClient.Connect($BroadcastAddress, 9)
        $UdpClient.Send($MagicPacket, $MagicPacket.Length)
        $UdpClient.Close()
        
        return $true
    } catch {
        Write-Host "Erreur PowerShell WOL: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Test 1: Test avec wakemeonlan-x64 (si disponible)
Write-Host "TEST 1: Test avec wakemeonlan-x64" -ForegroundColor Green
Write-Host "----------------------------------------" -ForegroundColor Green

$WakemeonlanPath = "wakemeonlan-x64.exe"
if (Get-Command $WakemeonlanPath -ErrorAction SilentlyContinue) {
    Write-Host "wakemeonlan-x64.exe trouve" -ForegroundColor Green
    Write-Host "Envoi du Magic Packet avec wakemeonlan-x64..."
    
    try {
        $Result = & $WakemeonlanPath $MacAddress
        Write-Host "wakemeonlan-x64: $Result" -ForegroundColor Green
    } catch {
        Write-Host "Erreur wakemeonlan-x64: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "wakemeonlan-x64.exe non trouve dans le PATH" -ForegroundColor Yellow
    Write-Host "Recherche dans le repertoire courant..." -ForegroundColor Yellow
    
    if (Test-Path ".\wakemeonlan-x64.exe") {
        Write-Host "wakemeonlan-x64.exe trouve dans le repertoire courant" -ForegroundColor Green
        Write-Host "Envoi du Magic Packet avec wakemeonlan-x64..."
        
        try {
            $Result = & ".\wakemeonlan-x64.exe" $MacAddress
            Write-Host "wakemeonlan-x64: $Result" -ForegroundColor Green
        } catch {
            Write-Host "Erreur wakemeonlan-x64: $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "wakemeonlan-x64.exe non trouve" -ForegroundColor Red
    }
}
Write-Host ""

# Test 2: Test avec PowerShell
Write-Host "TEST 2: Test avec PowerShell" -ForegroundColor Green
Write-Host "----------------------------------------" -ForegroundColor Green

Write-Host "Envoi du Magic Packet avec PowerShell..."
$PowerShellResult = Send-WakeOnLAN-PowerShell -MacAddress $MacAddress
if ($PowerShellResult) {
    Write-Host "PowerShell WOL: Succes" -ForegroundColor Green
} else {
    Write-Host "PowerShell WOL: Echec" -ForegroundColor Red
}
Write-Host ""

# Test 3: Test avec broadcast local
Write-Host "TEST 3: Test avec broadcast local" -ForegroundColor Green
Write-Host "----------------------------------------" -ForegroundColor Green

Write-Host "Envoi du Magic Packet avec broadcast local (192.168.1.255)..."
$LocalResult = Send-WakeOnLAN-PowerShell -MacAddress $MacAddress -BroadcastAddress "192.168.1.255"
if ($LocalResult) {
    Write-Host "PowerShell WOL local: Succes" -ForegroundColor Green
} else {
    Write-Host "PowerShell WOL local: Echec" -ForegroundColor Red
}
Write-Host ""

# Test 4: Test avec adresse IP specifique
Write-Host "TEST 4: Test avec adresse IP specifique" -ForegroundColor Green
Write-Host "----------------------------------------" -ForegroundColor Green

Write-Host "Envoi du Magic Packet avec adresse IP specifique ($TargetHost)..."
$DirectResult = Send-WakeOnLAN-PowerShell -MacAddress $MacAddress -BroadcastAddress $TargetHost
if ($DirectResult) {
    Write-Host "PowerShell WOL direct: Succes" -ForegroundColor Green
} else {
    Write-Host "PowerShell WOL direct: Echec" -ForegroundColor Red
}
Write-Host ""

# Test 5: Test du bot Python
Write-Host "TEST 5: Test du bot Python" -ForegroundColor Green
Write-Host "----------------------------------------" -ForegroundColor Green

Write-Host "Execution du test Python ameliore..."
try {
    $PythonResult = python test-wol-enhanced.py
    Write-Host "Resultat Python:" -ForegroundColor White
    Write-Host $PythonResult -ForegroundColor White
} catch {
    Write-Host "Erreur execution Python: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 6: Verification de la connectivite
Write-Host "TEST 6: Verification de la connectivite" -ForegroundColor Green
Write-Host "----------------------------------------" -ForegroundColor Green

Write-Host "Test de connectivite vers le serveur..."
$PingResult = Test-Connection -ComputerName $TargetHost -Count 1 -Quiet
if ($PingResult) {
    Write-Host "Serveur accessible via ping" -ForegroundColor Green
} else {
    Write-Host "Serveur non accessible via ping" -ForegroundColor Red
}

Write-Host "Test de connectivite sur le port Proxmox (8006)..."
try {
    $TcpClient = New-Object System.Net.Sockets.TcpClient
    $Connect = $TcpClient.BeginConnect($TargetHost, 8006, $null, $null)
    $Wait = $Connect.AsyncWaitHandle.WaitOne(5000, $false)
    
    if ($Wait) {
        $TcpClient.EndConnect($Connect)
        Write-Host "Port 8006 accessible" -ForegroundColor Green
        $TcpClient.Close()
    } else {
        Write-Host "Port 8006 non accessible (timeout)" -ForegroundColor Red
    }
} catch {
    Write-Host "Port 8006 non accessible: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "RECOMMANDATIONS:" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "1. Verifiez que le serveur est bien eteint avant le test" -ForegroundColor White
Write-Host "2. Attendez 30-60 secondes apres l'envoi du paquet" -ForegroundColor White
Write-Host "3. Verifiez que le serveur demarre (LED, ventilateurs, etc.)" -ForegroundColor White
Write-Host "4. Comparez les resultats entre les differentes methodes" -ForegroundColor White
Write-Host "5. Si wakemeonlan-x64 fonctionne mais pas le bot, le probleme est dans l'implémentation" -ForegroundColor White
Write-Host ""

Write-Host "Pour tester manuellement avec wakemeonlan-x64:" -ForegroundColor Yellow
Write-Host "wakemeonlan-x64.exe $MacAddress" -ForegroundColor White
