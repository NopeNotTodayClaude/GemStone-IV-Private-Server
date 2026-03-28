Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$outputPath = Join-Path $projectRoot "USETHIS.sql"
$dbName = "gemstone_dev"
$dbUser = "root"
$dbHost = "localhost"

function Get-ToolPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ToolName
    )

    $cmd = Get-Command $ToolName -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }

    $commonPaths = @(
        "C:\Program Files\MariaDB 12.1\bin\$ToolName.exe",
        "C:\Program Files\MariaDB 11.8\bin\$ToolName.exe",
        "C:\Program Files\MariaDB 11.4\bin\$ToolName.exe",
        "C:\Program Files\MySQL\MySQL Server 8.0\bin\$ToolName.exe"
    )

    foreach ($path in $commonPaths) {
        if (Test-Path $path) {
            return $path
        }
    }

    throw "Could not locate $ToolName on this machine."
}

function Invoke-CheckedProcess {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath,
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments,
        [string]$StdOutPath,
        [string]$StdErrPath
    )

    Push-Location $projectRoot
    try {
        $output = & $FilePath @Arguments 2>&1
        $exitCode = $LASTEXITCODE
    }
    finally {
        Pop-Location
    }

    $stdout = ($output | Out-String)
    $stderr = ""

    if ($StdOutPath) {
        [System.IO.File]::WriteAllText($StdOutPath, $stdout, [System.Text.UTF8Encoding]::new($false))
    }
    if ($StdErrPath) {
        [System.IO.File]::WriteAllText($StdErrPath, $stderr, [System.Text.UTF8Encoding]::new($false))
    }

    if ($exitCode -ne 0) {
        throw "Command failed ($FilePath): $stdout"
    }

    return @{
        StdOut = $stdout
        StdErr = $stderr
    }
}

function Get-SensitiveTables {
    param(
        [Parameter(Mandatory = $true)]
        [string]$MysqlPath
    )

    $query = @"
SELECT DISTINCT t.TABLE_NAME
FROM information_schema.tables t
LEFT JOIN information_schema.columns c
  ON c.TABLE_SCHEMA = t.TABLE_SCHEMA
 AND c.TABLE_NAME = t.TABLE_NAME
WHERE t.TABLE_SCHEMA = '$dbName'
  AND t.TABLE_TYPE = 'BASE TABLE'
  AND (
        t.TABLE_NAME RLIKE '^(character_.*)$'
        OR t.TABLE_NAME IN (
            'accounts',
            'characters',
            'sync_tokens',
            'npc_player_flags',
            'player_shops',
            'transaction_log',
            'picking_queue',
            'artisan_projects'
        )
        OR c.COLUMN_NAME IN (
            'account_id',
            'character_id',
            'owner_id',
            'owner_name',
            'claimer_id',
            'claimer_name',
            'nominee_character_id',
            'nominator_character_id'
        )
      )
ORDER BY t.TABLE_NAME;
"@

    $result = Invoke-CheckedProcess -FilePath $MysqlPath -Arguments @(
        "--host=$dbHost",
        "--user=$dbUser",
        "-N",
        "-e",
        $query,
        $dbName
    )

    return @(
        $result.StdOut -split "(`r`n|`n|`r)" |
        ForEach-Object { $_.Trim() } |
        Where-Object { $_ }
    )
}

$mysqlPath = Get-ToolPath -ToolName "mysql"
$mysqldumpPath = Get-ToolPath -ToolName "mysqldump"
$sensitiveTables = Get-SensitiveTables -MysqlPath $mysqlPath

if (-not $sensitiveTables -or $sensitiveTables.Count -eq 0) {
    throw "No sensitive tables were discovered. Refusing to build a supposedly sanitized export."
}

$tempDir = Join-Path $env:TEMP ("gemstone_sanitized_export_" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $tempDir | Out-Null

$mainDumpPath = Join-Path $tempDir "main_dump.sql"
$privateSchemaPath = Join-Path $tempDir "private_schema.sql"
$stderrPath = Join-Path $tempDir "dump.stderr.txt"

try {
    $commonDumpArgs = @(
        "--host=$dbHost",
        "--user=$dbUser",
        "--default-character-set=utf8mb4",
        "--single-transaction",
        "--routines",
        "--triggers",
        "--events",
        "--skip-dump-date",
        "--databases",
        $dbName
    )

    $ignoreArgs = @()
    foreach ($table in $sensitiveTables) {
        $ignoreArgs += "--ignore-table=$dbName.$table"
    }

    Invoke-CheckedProcess -FilePath $mysqldumpPath -Arguments ($commonDumpArgs + $ignoreArgs) -StdOutPath $mainDumpPath -StdErrPath $stderrPath | Out-Null

    $privateSchemaArgs = @(
        "--host=$dbHost",
        "--user=$dbUser",
        "--default-character-set=utf8mb4",
        "--skip-dump-date",
        "--no-data",
        $dbName
    ) + $sensitiveTables

    Invoke-CheckedProcess -FilePath $mysqldumpPath -Arguments $privateSchemaArgs -StdOutPath $privateSchemaPath -StdErrPath $stderrPath | Out-Null

    $mainDump = Get-Content $mainDumpPath -Raw
    $privateSchema = Get-Content $privateSchemaPath -Raw

    $sanitizedHeader = @(
        "-- Sanitized export for GemStone IV Server",
        "-- Sensitive player/account table data stripped automatically.",
        "-- Schema retained for: " + ($sensitiveTables -join ", "),
        ""
    ) -join [Environment]::NewLine

    $combined = $sanitizedHeader + $mainDump.TrimEnd() + [Environment]::NewLine + [Environment]::NewLine + $privateSchema.Trim() + [Environment]::NewLine
    [System.IO.File]::WriteAllText($outputPath, $combined, [System.Text.UTF8Encoding]::new($false))

    $verifyContent = Get-Content $outputPath -Raw
    $badTables = @()
    foreach ($table in $sensitiveTables) {
        $pattern = 'INSERT INTO `' + [Regex]::Escape($table) + '`'
        if ($verifyContent -match $pattern) {
            $badTables += $table
        }
    }

    if ($badTables.Count -gt 0) {
        throw "Sanitization check failed. Sensitive INSERTs still found for: $($badTables -join ', ')"
    }

    Write-Host ""
    Write-Host "Sanitized export complete."
    Write-Host "Output: $outputPath"
    Write-Host "Stripped table data:"
    foreach ($table in $sensitiveTables) {
        Write-Host "  - $table"
    }
    Write-Host ""
}
finally {
    if (Test-Path $tempDir) {
        Remove-Item -Path $tempDir -Recurse -Force
    }
}
