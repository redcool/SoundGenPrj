# 音频标准化：mp3 → 192kbps/48kHz；flac → 32bit float WAV 母带 + 192k mp3
param([string]$Path, [switch]$Force)
$ff='H:\Program Files\ffmpeg\bin\ffmpeg.exe'
if(-not (Test-Path -LiteralPath $Path)){ throw "not found: $Path" }
$dir=Split-Path -Parent $Path; $base=[IO.Path]::GetFileNameWithoutExtension($Path)
if($Path -match '\.flac$'){
  $wav=Join-Path $dir ($base+'_master32.wav')
  & $ff -y -loglevel error -i $Path -c:a pcm_f32le -ar 48000 $wav
  $mp3=Join-Path $dir ($base+'_192k.mp3')
  & $ff -y -loglevel error -i $Path -b:a 192k -ar 48000 $mp3
  Write-Output ('OK master32='+$wav+' mp3='+$mp3)
} else {
  $bak=Join-Path $dir ($base+'_128k.mp3')
  if(-not (Test-Path -LiteralPath $bak)){ Copy-Item -LiteralPath $Path -Destination $bak -Force }
  $tmp=Join-Path $dir ($base+'.tmp192.mp3')
  & $ff -y -loglevel error -i $bak -b:a 192k -ar 48000 $tmp
  Move-Item -LiteralPath $tmp -Destination $Path -Force
  Write-Output ('OK 192k: '+$Path)
}