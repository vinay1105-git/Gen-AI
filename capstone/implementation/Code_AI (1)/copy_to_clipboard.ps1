Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$imgPath = "C:\Users\gurka\Downloads\Code_AI (1)\ppt_architecture_diagram.png"
$img = [System.Drawing.Image]::FromFile($imgPath)
[System.Windows.Forms.Clipboard]::SetImage($img)
Write-Host "SUCCESS: The 16:9 Architecture Diagram has been copied to your Windows Clipboard!"
