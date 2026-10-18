# OpenVisio v18.3 Windows launcher. Author: Abdelhalim Talbi.
# Requires Windows PowerShell 5.1 / .NET Framework; no Python installation.
param([ValidateRange(0,65535)][int]$Port = 0, [switch]$NoBrowser)
$ErrorActionPreference = 'Stop'
$root = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$listener = New-Object System.Net.HttpListener
$tcp = New-Object System.Net.Sockets.TcpListener([System.Net.IPAddress]::Loopback, $Port)
try {
  $tcp.Start()
  $actualPort = ([System.Net.IPEndPoint]$tcp.LocalEndpoint).Port
} finally { $tcp.Stop() }
$url = "http://127.0.0.1:$actualPort/"
$listener.Prefixes.Add($url)
$mime = @{'.html'='text/html; charset=utf-8';'.js'='text/javascript; charset=utf-8';'.css'='text/css; charset=utf-8';'.json'='application/json; charset=utf-8';'.svg'='image/svg+xml';'.png'='image/png';'.ico'='image/x-icon';'.woff2'='font/woff2'}
try {
  $listener.Start()
  Write-Host "OpenVisio v18.3 - Abdelhalim Talbi"
  Write-Host "Local URL: $url"
  Write-Host 'Press Ctrl+C to stop.'
  if (-not $NoBrowser) { Start-Process $url }
  while ($listener.IsListening) {
    $context = $listener.GetContext()
    $response = $context.Response
    try {
      if ($context.Request.HttpMethod -ne 'GET' -and $context.Request.HttpMethod -ne 'HEAD') {
        $response.StatusCode = 405
        continue
      }
      $relative = [Uri]::UnescapeDataString($context.Request.Url.AbsolutePath).TrimStart('/')
      if ([string]::IsNullOrEmpty($relative)) { $relative = 'index.html' }
      $relative = $relative.Replace('/', [IO.Path]::DirectorySeparatorChar)
      $path = [IO.Path]::GetFullPath((Join-Path $root $relative))
      $rootPrefix = $root.TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
      if (-not $path.StartsWith($rootPrefix, [StringComparison]::OrdinalIgnoreCase)) { $response.StatusCode = 403; continue }
      $ext = [IO.Path]::GetExtension($path).ToLowerInvariant()
      if (-not $mime.ContainsKey($ext) -or -not [IO.File]::Exists($path)) { $response.StatusCode = 404; continue }
      $bytes = [IO.File]::ReadAllBytes($path)
      $response.ContentType = $mime[$ext]
      $response.ContentLength64 = $bytes.Length
      $response.Headers.Add('X-Content-Type-Options', 'nosniff')
      $response.Headers.Add('X-Frame-Options', 'DENY')
      $response.Headers.Add('Cache-Control', 'no-store')
      if ($context.Request.HttpMethod -eq 'GET') { $response.OutputStream.Write($bytes,0,$bytes.Length) }
    } catch {
      Write-Warning $_.Exception.Message
      try { $response.StatusCode = 500 } catch {}
    } finally { $response.Close() }
  }
} finally { if ($listener.IsListening) { $listener.Stop() }; $listener.Close() }
