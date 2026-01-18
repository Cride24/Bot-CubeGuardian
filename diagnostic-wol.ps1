# Script de diagnostic Wake-on-LAN pour Bot CubeGuardian
# Compare avec wakemeonlan-x64 qui fonctionne

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "DIAGNOSTIC WAKE-ON-LAN - Bot CubeGuardian" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# Configuration du serveur
$MacAddress = "00:23:7D:FD:C0:5C"
$TargetHost = "192.168.1.245"

Write-Host "Adresse MAC: $MacAddress" -ForegroundColor Yellow
Write-Host "Adresse IP: $TargetHost" -ForegroundColor Yellow
Write-Host ""

# Test 1: Verification de la configuration reseau
Write-Host "TEST 1: Configuration reseau Windows" -ForegroundColor Green
Write-Host "----------------------------------------" -ForegroundColor Green
try {
    $NetworkConfig = Get-NetIPConfiguration | Where-Object { $_.IPv4Address -like "192.168.1.*" }
    if ($NetworkConfig) {
        Write-Host "Interface reseau trouvee:" -ForegroundColor Green
        Write-Host "  Interface: $($NetworkConfig.InterfaceAlias)" -ForegroundColor White
        Write-Host "  Adresse IP: $($NetworkConfig.IPv4Address.IPAddress)" -ForegroundColor White
        Write-Host "  Gateway: $($NetworkConfig.IPv4DefaultGateway.NextHop)" -ForegroundColor White
    } else {
        Write-Host "Aucune interface reseau 192.168.1.x trouvee" -ForegroundColor Red
    }
} catch {
    Write-Host "Erreur lors de la verification reseau: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 2: Test de connectivite vers le serveur
Write-Host "TEST 2: Test de connectivite vers le serveur" -ForegroundColor Green
Write-Host "----------------------------------------" -ForegroundColor Green
try {
    $PingResult = Test-Connection -ComputerName $TargetHost -Count 1 -Quiet
    if ($PingResult) {
        Write-Host "Serveur accessible via ping" -ForegroundColor Green
    } else {
        Write-Host "Serveur non accessible via ping" -ForegroundColor Red
    }
} catch {
    Write-Host "Erreur lors du test ping: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 3: Test de connectivite sur le port Proxmox
Write-Host "TEST 3: Test de connectivite sur le port Proxmox (8006)" -ForegroundColor Green
Write-Host "----------------------------------------" -ForegroundColor Green
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

# Test 4: Test avec PowerShell Wake-on-LAN
Write-Host "TEST 4: Test avec PowerShell Wake-on-LAN" -ForegroundColor Green
Write-Host "----------------------------------------" -ForegroundColor Green
try {
    # Fonction PowerShell pour Wake-on-LAN
    function Send-WakeOnLAN {
        param(
            [string]$MacAddress,
            [string]$BroadcastAddress = "255.255.255.255"
        )
        
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
    }
    
    Write-Host "Envoi du Magic Packet avec PowerShell..."
    Send-WakeOnLAN -MacAddress $MacAddress
    Write-Host "Magic Packet envoye avec PowerShell" -ForegroundColor Green
    
} catch {
    Write-Host "Erreur PowerShell Wake-on-LAN: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 5: Test avec broadcast local
Write-Host "TEST 5: Test avec broadcast local (192.168.1.255)" -ForegroundColor Green
Write-Host "----------------------------------------" -ForegroundColor Green
try {
    Write-Host "Envoi du Magic Packet avec broadcast local..."
    Send-WakeOnLAN -MacAddress $MacAddress -BroadcastAddress "192.168.1.255"
    Write-Host "Magic Packet envoye avec broadcast local" -ForegroundColor Green
} catch {
    Write-Host "Erreur broadcast local: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 6: Verification des ports UDP ouverts
Write-Host "TEST 6: Verification des ports UDP ouverts" -ForegroundColor Green
Write-Host "----------------------------------------" -ForegroundColor Green
try {
    $UdpPorts = Get-NetUDPEndpoint | Where-Object { $_.LocalAddress -like "192.168.1.*" -or $_.LocalAddress -eq "0.0.0.0" }
    Write-Host "Ports UDP ouverts sur l'interface locale:" -ForegroundColor White
    $UdpPorts | Select-Object LocalAddress, LocalPort | Format-Table -AutoSize
} catch {
    Write-Host "Erreur lors de la verification des ports UDP: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "RECOMMANDATIONS:" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "1. Verifiez que le serveur a le Wake-on-LAN active dans le BIOS" -ForegroundColor White
Write-Host "2. Verifiez que la carte reseau supporte le WOL" -ForegroundColor White
Write-Host "3. Testez avec wakemeonlan-x64 pour confirmer que le WOL fonctionne" -ForegroundColor White
Write-Host "4. Verifiez que le firewall ne bloque pas les paquets UDP" -ForegroundColor White
Write-Host "5. Essayez differentes adresses de broadcast" -ForegroundColor White
Write-Host "6. Verifiez que le serveur est bien eteint avant le test" -ForegroundColor White
Write-Host ""

Write-Host "Pour tester avec wakemeonlan-x64:" -ForegroundColor Yellow
Write-Host "wakemeonlan-x64.exe $MacAddress" -ForegroundColor White
