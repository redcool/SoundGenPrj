$ff='H:\Program Files\ffmpeg\bin\ffmpeg.exe'
$src='H:\Works\SoundGenPrj\tmp\ignis_fixed'
$rows = @(
  '网开一面_商汤|||《网开一面》_商_约前1600_商汤|||义名之歌-商-卷1'
  '鼎中乾坤_伊尹|||《鼎中乾坤》_商_约前1600_伊尹|||义名之歌-商-卷1'
  '披甲而战_妇好|||《披甲而战》_商_约前1200_妇好|||义名之歌-商-卷1'
  '七窍心_比干|||《七窍心》_商_约前1050_比干|||义名之歌-商-卷1'
  '迁殷_盘庚|||《迁殷》_商_约前1300_盘庚|||义名之歌-商-卷1'
  '去国_微子|||《去国》_商_约前1050_微子|||义名之歌-商-卷1'
  '雊雉_祖己|||《雊雉》_商_约前1200_祖己|||义名之歌-商-卷1'
  '诰_仲虺|||《诰》_商_约前1600_仲虺|||义名之歌-商-卷1'
  '商卷1_专辑封面|||义名之歌-商卷1_专辑封面|||义名之歌-商-卷1'
  '羑里_姬昌|||《羑里》_商末周初_约前1050_姬昌|||义名之歌-西周-卷1'
  '牧野_姬发|||《牧野》_周_约前1046_姬发|||义名之歌-西周-卷1'
  '愿者上钩_姜尚|||《愿者上钩》_周_约前1045_姜尚|||义名之歌-西周-卷1'
  '吐哺_姬旦|||《吐哺》_周_约前1040_姬旦|||义名之歌-西周-卷1'
  '西周卷1_专辑封面|||义名之歌-西周卷1_专辑封面|||义名之歌-西周-卷1'
  '三过家门_大禹|||《三过家门》_夏_约前2070_大禹|||义名之歌-夏-卷1'
  '射日_后羿|||《射日》_上古_传说_后羿|||义名之歌-夏-卷1'
  '夏卷1_专辑封面|||义名之歌-夏卷1_专辑封面|||义名之歌-夏-卷1'
)
foreach($r in $rows){
  $p=$r -split '\|\|\|',3; $n=$p[0]; $canon=$p[1]; $album=$p[2]
  $inp = Join-Path $src ($n + '.png')
  if(Test-Path -LiteralPath $inp){
    $outFile = 'H:\Works\SoundGenPrj\output\history-rock\' + $canon + '_v3_gptimage.png'
    & $ff -y -loglevel error -i $inp -vf scale=1024:1024 $outFile
    New-Item -ItemType Directory -Force -Path ('H:\Works\SoundGenPrj\albums\' + $album + '\封面') | Out-Null
    Copy-Item -LiteralPath $outFile -Destination ('H:\Works\SoundGenPrj\albums\' + $album + '\封面\' + $canon + '_v3_gptimage.png') -Force
    Write-Output ('PLACED ' + $canon)
  } else { Write-Output ('MISS ' + $n) }
}