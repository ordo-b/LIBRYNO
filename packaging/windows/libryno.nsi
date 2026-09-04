; Libryno NSIS Installer Script
; Gera: Libryno-Setup-${VERSION}.exe
; Compilar com: makensis libryno.nsi

!include "LogicLib.nsh"
!include "x64.nsh"
!include "FileFunc.nsh"

; =============================================================================
# Configurações Básicas
; =============================================================================
!define APP_NAME "Libryno"
!define APP_VERSION "2.0.0"
!define APP_PUBLISHER "OrdoB"
!define APP_URL "https://ordob.com/libryno"
!define APP_EXE "libryno.exe"

; Nome do instalador gerado
OutFile "dist\Libryno-Setup-${APP_VERSION}.exe"
InstallDir "$LOCALAPPDATA\Libryno"
InstallDirRegKey HKCU "Software\Libryno" "Install_Dir"

; Request admin rights for installation
RequestExecutionLevel admin

; =============================================================================
# Interface
; =============================================================================
!define MUI_ICON "src\img\icon.ico"
!define MUI_UNICON "src\img\icon.ico"
!define MUI_WELCOMEFINISHPAGE_BITMAP "packaging\windows\banner.bmp"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "packaging\windows\header.bmp"
!define MUI_HEADERIMAGE_UNBITMAP "packaging\windows\header.bmp"

; Welcome page
!insertmacro MUI_PAGE_WELCOME
; License page
!insertmacro MUI_PAGE_LICENSE "packaging\windows\LICENSE.txt"
; Directory page
!insertmacro MUI_PAGE_DIRECTORY
; Install page
!insertmacro MUI_PAGE_INSTFILES
; Finish page
!define MUI_FINISHPAGE_RUN "$INSTDIR\${APP_EXE}"
!define MUI_FINISHPAGE_RUN_NOTCHECKED
!insertmacro MUI_PAGE_FINISH

; Uninstall pages
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!insertmacro MUI_LANGUAGE "PortugueseBR"

; =============================================================================
# Variáveis
; =============================================================================
Var StartMenuFolder
Var CreateDesktopShortcut
Var CreateStartMenuShortcut
Var AutoStart
Var PreviousVersion

; =============================================================================
# Funções
; =============================================================================
Function .onInit
    ; Verifica se já existe versão instalada
    ReadRegStr $PreviousVersion HKCU "Software\Libryno" "Version"
    ${If} $PreviousVersion != ""
        MessageBox MB_YESNO|MB_ICONQUESTION \
            "Já existe uma versão do Libryno instalada (v$PreviousVersion).$\n$\n\
            Deseja atualizar para a versão ${APP_VERSION}?$\n$\n\
            (Seus dados locais serão preservados)" \
            IDYES +2
        Abort
    ${EndIf}

    ; Verifica se está rodando como admin
    UserInfo::GetAccountType
    Pop $0
    ${If} $0 != "Admin"
        MessageBox MB_ICONSTOP "O instalador requer privilégios de administrador. $\n$\nPor favor, execute como administrador."
        Abort
    ${EndIf}
FunctionEnd

Function .onInstSuccess
    ; Registra versão instalada
    WriteRegStr HKCU "Software\Libryno" "Version" "${APP_VERSION}"
    WriteRegStr HKCU "Software\Libryno" "InstallDate" "$(GetDate)"
    WriteRegStr HKCU "Software\Libryno" "InstallDir" "$INSTDIR"

    ; Adiciona ao Painel de Controle (Add/Remove Programs)
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Libryno" \
        "DisplayName" "Libryno"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Libryno" \
        "DisplayVersion" "${APP_VERSION}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Libryno" \
        "Publisher" "${APP_PUBLISHER}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Libryno" \
        "URLInfoAbout" "${APP_URL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Libryno" \
        "InstallLocation" "$INSTDIR"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Libryno" \
        "UninstallString" "$INSTDIR\uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Libryno" \
        "DisplayIcon" "$INSTDIR\libryno.exe"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Libryno" \
        "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Libryno" \
        "NoRepair" 1
FunctionEnd

Function un.onInit
    MessageBox MB_ICONQUESTION|MB_YESNO \
        "Tem certeza que deseja desinstalar o Libryno?$\n$\n\
        Seus dados locais (livros, leitores, empréstimos) NÃO serão removidos. $\n$\n\
        Apenas o programa será desinstalado." \
        IDYES +2
    Abort
FunctionEnd

Function un.onUninstSuccess
    ; Remove entradas do registro
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Libryno"
    DeleteRegKey HKCU "Software\Libryno"

    ; Remove atalhos
    Delete "$SMPROGRAMS\Libryno\Libryno.lnk"
    Delete "$SMPROGRAMS\Libryno\Desinstalar Libryno.lnk"
    Delete "$DESKTOP\Libryno.lnk"

    ; Remove pasta do menu iniciar se vazia
    RMDir "$SMPROGRAMS\Libryno"
FunctionEnd

; =============================================================================
# Seção Principal
; =============================================================================
Section "Main" SEC_MAIN
    SetOutPath $INSTDIR

    ; Binário principal
    File "dist\${APP_EXE}"

    ; DLLs necessárias (PyInstaller já empacota, mas garante)
    File /r "dist\*.dll"
    File /r "dist\*.pyd"

    ; Recursos (ícones, imagens, temas, traduções)
    File /r "src\img\*"
    File /r "src\ui\themes\*"
    File /r "src\ui\i18n\*"

    ; Cria desinstalador
    WriteUninstaller "$INSTDIR\uninstall.exe"

    ; Atalhos
    ${If} ${CreateStartMenuShortcut}
        CreateDirectory "$SMPROGRAMS\Libryno"
        CreateShortcut "$SMPROGRAMS\Libryno\Libryno.lnk" "$INSTDIR\${APP_EXE}" "" "$INSTDIR\src\img\icon.ico"
        CreateShortcut "$SMPROGRAMS\Libryno\Desinstalar Libryno.lnk" "$INSTDIR\uninstall.exe"
    ${EndIf}

    ${If} ${CreateDesktopShortcut}
        CreateShortcut "$DESKTOP\Libryno.lnk" "$INSTDIR\${APP_EXE}" "" "$INSTDIR\src\img\icon.ico"
    ${EndIf}

    ; Auto-start (opcional)
    ${If} ${AutoStart}
        WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "Libryno" '"$INSTDIR\${APP_EXE}" --minimized'
    ${EndIf}
SectionEnd

; =============================================================================
# Seções Opcionais
; =============================================================================
Section "Atalho no Menu Iniciar" SEC_STARTMENU
    ${CreateStartMenuShortcut}
SectionEnd

Section "Atalho na Área de Trabalho" SEC_DESKTOP
    ${CreateDesktopShortcut}
SectionEnd

Section "Iniciar com Windows" SEC_AUTOSTART
    ${AutoStart}
SectionEnd

; =============================================================================
# Desinstalador
; =============================================================================
Section "Uninstall"
    ; Remove arquivos
    Delete "$INSTDIR\${APP_EXE}"
    Delete "$INSTDIR\uninstall.exe"
    Delete "$INSTDIR\*.dll"
    Delete "$INSTDIR\*.pyd"

    ; Remove pastas
    RMDir /r "$INSTDIR\img"
    RMDir /r "$INSTDIR\themes"
    RMDir /r "$INSTDIR\i18n"
    RMDir /r "$INSTDIR\__pycache__"

    ; Remove atalhos
    Delete "$SMPROGRAMS\Libryno\Libryno.lnk"
    Delete "$SMPROGRAMS\Libryno\Desinstalar Libryno.lnk"
    Delete "$DESKTOP\Libryno.lnk"
    RMDir "$SMPROGRAMS\Libryno"

    ; Remove auto-start
    DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "Libryno"

    ; Remove registro
    DeleteRegKey HKCU "Software\Libryno"
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Libryno"

    ; Tenta remover diretório de instalação
    RMDir $INSTDIR
SectionEnd

; =============================================================================
# Funções Auxiliares
; =============================================================================
Function GetDate
    ; Retorna data no formato YYYY-MM-DD
    System::Call 'kernel32::GetLocalTime(i .r0)'
    Pop $0
    System::Call 'kernel32::GetLocalTime(i .r0)'
    Pop $1
    System::Call 'kernel32::GetLocalTime(i .r0)'
    Pop $2
    ; Formato: YYYY-MM-DD
    Push $0
    Push $1
    Push $2
    System::Call 'kernel32::GetLocalTime(i .r0)'
    Pop $3
    System::Call 'kernel32::GetLocalTime(i .r0)'
    Pop $4
    System::Call 'kernel32::GetLocalTime(i .r0)'
    Pop $5
    StrCpy $R0 "$3-$4-$5"
FunctionEnd

; =============================================================================
# Recursos (banner, header, license)
; =============================================================================
; Coloque estes arquivos em packaging/windows/:
; - banner.bmp (150x570)
; - header.bmp (150x60)
; - LICENSE.txt (Apache 2.0)