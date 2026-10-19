param(
  [Parameter(Mandatory=$true)][string]$Query,
  [int]$MaxResults = 6
)
# SimpleMCPServer web.search 直连调用（绕开 DSH MCP 客户端会话）
$payload = @{ jsonrpc='2.0'; id=1; method='tools/call'; params=@{ name='web.search'; arguments=@{ query=$Query; maxResults=$MaxResults } } }
$json = $payload | ConvertTo-Json -Depth 6
$body = [System.Text.Encoding]::UTF8.GetBytes($json)
$result = Invoke-RestMethod -Uri 'http://127.0.0.1:45678/rpc' -Method Post -ContentType 'application/json; charset=utf-8' -Body $body -TimeoutSec 30
($result.result.content[0].text | ConvertFrom-Json) | ForEach-Object { '[' + $_.title + '] ' + $_.url }; ''; '--- snippets ---'; ($result.result.content[0].text | ConvertFrom-Json) | ForEach-Object { ($_.snippet -replace '\s+',' ').Substring(0,[Math]::Min(200,$_.snippet.Length)) }