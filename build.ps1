$exclude = @("venv", "RPA_BUSCADOR_PRAZOS_CNJ.zip")
$files = Get-ChildItem -Path . -Exclude $exclude
Compress-Archive -Path $files -DestinationPath "RPA_BUSCADOR_PRAZOS_CNJ.zip" -Force