; zen.script Inno Setup Script
; --

; Define application constants. The version is passed in from our build script.
#define MyAppName "zen.script"
#define MyAppPublisher "kittykode io"
#define MyAppURL "https://github.com/kittykatkode/zen.script"
#define MyAppExeName "zen.script.exe"

#ifndef AppVersion
  #define AppVersion "1.0.0"
#endif

[Setup]
AppId={{AUTO}}
AppName={#MyAppName}
AppVersion={#AppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputBaseFilename=zenscript-{#AppVersion}-setup
OutputDir=installers
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=logo_zen_dot.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

