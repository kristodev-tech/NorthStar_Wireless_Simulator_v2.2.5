#define AppName "NorthStar Wireless Simulator"
#define AppVersion "2.2.5"
#define AppExe "NorthStarWirelessSimulator.exe"
[Setup]
AppId={{9D6082C5-3526-4A50-BEA5-734D2192D921}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=NorthStar Software Works
AppPublisherURL=https://northstarsoftwareworks.com
DefaultDirName={localappdata}\Programs\NorthStar Wireless Simulator
DefaultGroupName=NorthStar Wireless Simulator
PrivilegesRequired=lowest
OutputDir=..\installer
OutputBaseFilename=NorthStarWirelessSimulator_2.2.5_Setup
SetupIconFile=..\assets\branding\northstar.ico
UninstallDisplayIcon={app}\{#AppExe}
LicenseFile=..\docs\EULA.txt
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
MinVersion=10.0
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
CloseApplications=yes
[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Shortcuts:"; Flags: unchecked
[Files]
Source: "..\dist\NorthStarWirelessSimulator\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\docs\*"; DestDir: "{app}\docs"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\examples\*"; DestDir: "{app}\examples"; Flags: ignoreversion
Source: "..\assets\branding\desktop_wallpaper.png"; DestDir: "{app}\branding"; Flags: ignoreversion
Source: "..\assets\branding\product_image_800x800.png"; DestDir: "{app}\branding"; Flags: ignoreversion
[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExe}"
Name: "{group}\User Guide"; Filename: "{app}\docs\User_Guide.html"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon
[Run]
Filename: "{app}\{#AppExe}"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent
