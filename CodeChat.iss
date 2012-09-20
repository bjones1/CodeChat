; This produces a setup .msi to install CodeChat. It was created from Example1.iss which comes with Inno setup plus info from
; http://opencandy.com/2011/06/09/installer-platform-comparison-making-the-right-choice/.

; A few handy definitions to avoid repetition
#define PRODUCT_NAME 'CodeChat'
#define PRODUCT_VERSION 'r193'

[Setup]
AppName={#PRODUCT_NAME}
AppVersion={#PRODUCT_VERSION}
DefaultDirName={pf}\{#PRODUCT_NAME}
DefaultGroupName={#PRODUCT_NAME}
UninstallDisplayIcon={app}\bin\code_chat.exe
Compression=lzma2
SolidCompression=yes
OutputBaseFilename="Install {#PRODUCT_NAME}"
OutputDir=.

[Files]
Source: "dist\all\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\{#PRODUCT_NAME}"; Filename: "{app}\bin\code_chat.exe"
Name: "{group}\{#PRODUCT_NAME} help"; Filename: "{app}\doc\contents.html"
