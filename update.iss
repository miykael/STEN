
; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "STEN"
#define MyAppVersion "1.0"
#define MyAppPublisher "Laboratory for Investigative Neurophysiology (the LINE)"
#define MyAppURL "http://www.unil.ch/line/home/menuinst/about-the-line/software--analysis-tools.html#standard_412"
#define MyAppExeName "Interface.py"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{0B9653C5-44F7-41E4-90E5-94D5384512FA}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={pf}\{#MyAppName}
DisableDirPage=yes
DefaultGroupName={#MyAppName}
OutputBaseFilename=StenUpdate_20150605
Compression=lzma
SolidCompression=yes
CreateUninstallRegKey=no
UpdateUninstallLogAppName=no
UsePreviousAppDir=yes
DisableProgramGroupPage=yes
LicenseFile=C:\Users\jknebel\Documents\python\install\licence.txt
InfoAfterFile=C:\Users\jknebel\Documents\python\install\Citation.rtf

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Files]
Source: "C:\Users\jknebel\Documents\python\PyProject\STEN\Interface.py"; DestDir: "{app}"
Source: "C:\Users\jknebel\Documents\python\PyProject\STEN\LeftPanel.py"; DestDir: "{app}"
Source: "C:\Users\jknebel\Documents\python\PyProject\STEN\PostStat.py"; DestDir: "{app}"
Source: "C:\Users\jknebel\Documents\python\PyProject\STEN\RightPanel.py"; DestDir: "{app}"
Source: "C:\Users\jknebel\Documents\python\PyProject\STEN\Stat.py"; DestDir: "{app}"


[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, "&", "&&")}}"; Flags: shellexec postinstall skipifsilent
