;///////////////////////////////////////////////////////////////////////////
;// The pyedpro install file
; Make sure to uncomment DICOM series before distribution

;--------------------------------
;Include Modern UI

	!include "MUI2.nsh"

	!insertmacro MUI_DEFAULT MUI_UNWELCOMEFINISHPAGE_BITMAP "xnt.bmp"
	!insertmacro MUI_DEFAULT MUI_WELCOMEFINISHPAGE_BITMAP "xnt.bmp"

;--------------------------------
;Name and file

  Name "pyedpro"

;--------------------------------
;Build target selection

	; Define this for no samples build
#	!define NODICOM 1

    !echo "------------------------"
    !echo "Build pyedpro Original Version"

    OutFile "pyedpro_install.exe"
    !define BANNER  "logo.jpg"

    ;Default installation folder
    InstallDir "$PROGRAMFILES\pyedpro"

    BrandingText " pyedpro pygobject example "

    ;Get installation folder from registry if available
    InstallDirRegKey HKCU "Software\pyedpro" ""

;--------------------------------
;Interface Settings

	!define	MUI_HEADERIMAGE
	!define MUI_HEADERIMAGE_BITMAP xntheader3.bmp
	!define MUI_ABORTWARNING

;--------------------------------
;Pages

  !insertmacro MUI_PAGE_WELCOME
  !insertmacro MUI_PAGE_LICENSE "License.txt"
  ;!insertmacro MUI_PAGE_COMPONENTS

  !insertmacro MUI_PAGE_DIRECTORY
  !insertmacro MUI_PAGE_INSTFILES

  !define 	 	MUI_FINISHPAGE_RUN $PROGRAMFILES\pyedpro\pyedpro.exe
  !insertmacro 	MUI_PAGE_FINISH

  !insertmacro MUI_UNPAGE_WELCOME
  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES
  !insertmacro MUI_UNPAGE_FINISH

;--------------------------------
;Languages

    !insertmacro MUI_LANGUAGE "English"

    icon pyedpro.ico
    uninstallicon pyedpro.ico

; -------------------------------------------------------------------------
;Installer Sections

Section "-Install pyedpro Code" SecCode

    SetShellVarContext all

    SetOutPath "$INSTDIR"

	;MessageBox MB_OK $EXEDIR

    ; Add your own files here...
    ;File  /oname=pyedpro.exe .\dist]pyedpro\pyedpro.exe

    ; Copy logo to target
    ;File  /oname=logo.jpg ${BANNER}

    ; Copy OEM FILE to target
    ;File /oname=${XBANNER} oem.txt

	;File  x-ray.bmp
    ;File  Readme.txt
    File  License.txt
    ;File  /oname=default.ges.org default.gesture

    ; User manual
    ;File  /r /x ".svn" /x "*.cpt"  /x "images" .\umanual

    ;// All files
	File  /r /x "*.svn" /x "*.obj" /x "*.pch"  /x "*.ncb" /x "*.opt" /x "*.plg" ".\dist\pyedpro\"

    SetOutPath "$SYSDIR"

    ; ---------------------------------------------------------------------
    SetOutPath $INSTDIR

    CreateDirectory $SMPROGRAMS\pyedpro

    CreateShortCut "$SMPROGRAMS\pyedpro\pyedpro.lnk" "$INSTDIR\pyedpro.exe" "" \
                    "$INSTDIR\pyedpro.exe" 0  SW_SHOWNORMAL  "ALT|CONTROL|X"

    ;CreateShortCut "$QUICKLAUNCH\pyedpro.lnk" "$INSTDIR\pyedpro.exe"
    ;CreateShortCut "$SENDTO\pyedpro.lnk" "$INSTDIR\pyedpro.exe"

    ;CreateShortCut "$SMPROGRAMS\pyedpro\pyedpro Web Site.lnk" "http:\\www.pyedpro.com" "" \
    ;                "" 0  SW_SHOWNORMAL  "ALT|CONTROL|W"

    ;CreateDirectory $SMPROGRAMS\pyedpro\Documents
    ;CreateShortCut "$SMPROGRAMS\pyedpro\Documents\Readme.lnk" "$INSTDIR\Readme.txt"
    ;CreateShortCut "$SMPROGRAMS\pyedpro\Documents\HTML Documentation.lnk" "$INSTDIR\umanual\index.html"

    ;CreateShortCut "$SMPROGRAMS\pyedpro\Documents\Quick Start.lnk" "$INSTDIR\Quick_Start.doc"

    ;CreateDirectory $SMPROGRAMS\pyedpro\Tools
    ;CreateShortCut "$SMPROGRAMS\pyedpro\Tools\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
    ;CreateShortCut "$SMPROGRAMS\pyedpro\Tools\License.lnk" "$INSTDIR\License.txt"
    ;CreateShortCut "$DESKTOP\pyedpro.lnk" "$INSTDIR\pyedpro.exe"

    ;Store installation folder
    WriteRegStr HKCU "Software\pyedpro" "" $INSTDIR

    ; ---------------------------------------------------------------------
    ;Register pyedpro file as .pyedpro handler

    ;WriteRegStr HKCR ".xnt" "" "pyedpro.FileHandler"
    ;WriteRegStr HKCR "pyedpro.FileHandler" "" ""
    ;WriteRegStr HKCR "pyedpro.FileHandler\shell" "" ""
    ;WriteRegStr HKCR "pyedpro.FileHandler\DefaultIcon" "" "$INSTDIR\pyedpro.exe,0"
    ;WriteRegStr HKCR "pyedpro.FileHandler\shell\Open\" "" "Open pyedpro File"
    ;WriteRegStr HKCR "pyedpro.FileHandler\shell\Open\command" "" '$INSTDIR\pyedpro.exe "%1"'
    ;WriteRegStr HKCR "pyedpro.FileHandler\shell\Edit" "" "Edit pyedpro File"
    ;WriteRegStr HKCR "pyedpro.FileHandler\shell\Edit\command" "" '$INSTDIR\pyedpro.exe "%1"'
	;WriteRegStr HKCR "pyedpro.FileHandler\shell\Unpack" "" "Unpack Component Files"
    ;WriteRegStr HKCR "pyedpro.FileHandler\shell\Unpack\command" "" '$INSTDIR\pyedpro.exe "/unpack %1"'

    ;WriteRegStr HKCR ".gesture" "" "pyedpro.GestureHandler"

    ;Create uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"

    ; Create control panel unistaller
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\pyedpro"  "DisplayName" "pyedpro Annotation Program"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\pyedpro"  "UninstallString" $INSTDIR\Uninstall.exe
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\pyedpro"  "DisplayIcon" $INSTDIR\pyedpro.exe,0"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\pyedpro"  "DisplayVersion" "Version 1.0"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\pyedpro"  "HelpLink" "http://www.pyedpro.com"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\pyedpro"  "NoModify" 1
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\pyedpro"  "NoRepair" 1

SectionEnd

Section "-pyedpro Data"  SecData

	;File spell.txt
	;File medspell.txt

    ;CreateDirectory "C:\pyedpro\"

    ;SetOutPath "C:\pyedpro\"

    ;CreateDirectory "C:\pyedpro\samples"
    ;CreateDirectory "C:\pyedpro\samples\dicom"
    ;CreateDirectory "C:\pyedpro\samples\dicom_ser"
    ;CreateDirectory "C:\pyedpro\samples\images"
    ;CreateDirectory "C:\pyedpro\samples\notes"

	;CreateDirectory "C:\pyedpro\images\"
	;CreateDirectory "C:\pyedpro\notes\"
	;CreateDirectory "C:\pyedpro\db\"
	;CreateDirectory "C:\pyedpro\data"

	;File default.gesture

    ;File  /r /x ".svn" "data"
	;File  /r /x ".svn" "db"
	;File  /r /x ".svn" "stock"

SectionEnd

Section  "Image Samples" SecImg

    SetOutPath "C:\pyedpro\samples\"

	;File  /r /x ".svn" "samples\images"
	;DetailPrint "Copying image samples ..."
	;CopyFiles /SILENT "$EXEDIR\samples\images" "C:\pyedpro\samples"

SectionEnd

Section "DICOM Single Frame Samples"  SecSamp

    SetOutPath "C:\pyedpro\samples\"

	;File  /r /x ".svn" "samples\dicom"
	DetailPrint "Copying DICOM samples ... "
	CopyFiles /SILENT "$EXEDIR\samples\dicom" "C:\pyedpro\samples"


SectionEnd

Section  "DICOM Multi Frame Samples" SecDICOM

    SetOutPath "C:\pyedpro\samples\"

    ;File /r /x ".svn" 	"samples\dicom_ser"
	DetailPrint "Copying DICOM series samples ... "
	CopyFiles /SILENT "$EXEDIR\samples\dicom_ser" "C:\pyedpro\samples"

SectionEnd

;--------------------------------
;Uninstaller Section

Section "Uninstall"

    SetShellVarContext all

    Delete "$INSTDIR\Uninstall.exe"
    Delete "$INSTDIR\pyedpro.exe"

    RMDir /r "$INSTDIR"

    Delete "$SMPROGRAMS\pyedpro\pyedpro.lnk"
    Delete "$SMPROGRAMS\pyedpro\Readme.lnk"
    Delete "$SMPROGRAMS\pyedpro\License.lnk"

    Delete "$SMPROGRAMS\pyedpro\Guide_inside.pdf"
    Delete "$SMPROGRAMS\pyedpro\Guide_outside.pdf"
    Delete "$SMPROGRAMS\pyedpro\manual.pdf"

    Delete "$QUICKLAUNCH\pyedpro.lnk"
    Delete "$DESKTOP\pyedpro.lnk"
    Delete "$SENDTO\pyedpro.lnk"

    RMDir /r "$SMPROGRAMS\pyedpro\Tools\"
    RMDir /r "$SMPROGRAMS\pyedpro\"

    DeleteRegKey HKCU "Software\pyedpro"
    DeleteRegKey HKCR ".pyedpro"
    DeleteRegKey HKCR "pyedpro.FileHandler"
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\pyedpro"

SectionEnd

  LangString DESC_SecCode ${LANG_ENGLISH} "Program Code.$\r$\n$\r$\n\
  UnCheck (unselect) this if you do not want the installation to modify or update the pyedpro executable."

  LangString DESC_SecData ${LANG_ENGLISH} "Initial Data.$\r$\n$\r$\n\
  UnCheck (unselect) this if you do not want the installation to modify or update any of your sample images."

  ;LangString DESC_SecGal ${LANG_ENGLISH} "Galleries and Modules.$\r$\n$\r$\n\
  ;UnCheck (unselect) this if you do not want the installation to modify or update any of your gallery items."

  ;LangString DESC_SecSamp ${LANG_ENGLISH} "Sample images/data.$\r$\n$\r$\n\
  ;UnCheck (unselect) this if you do not want the installation to modify or update any of your sample patient items. (safe to leave it checked)"

  ;LangString DESC_SecDicom ${LANG_ENGLISH} "Sample DICOM images/data.$\r$\n$\r$\n\
  ;UnCheck (unselect) this if you do not want the installation to modify or update any of your DICOM sample items. (safe to leave it checked)"

  ;LangString DESC_Img ${LANG_ENGLISH} "Sample images.$\r$\n$\r$\n\
  ;UnCheck (unselect) this if you do not want the installation to modify or update any of your image sample items. (safe to leave it checked)"

  ;Assign language strings to sections
  ;!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    ;!insertmacro MUI_DESCRIPTION_TEXT ${SecCode} $(DESC_SecCode)
    ;!insertmacro MUI_DESCRIPTION_TEXT ${SecData} $(DESC_SecData)
    ;!insertmacro MUI_DESCRIPTION_TEXT ${SecDICOM} $(DESC_SecDicom)
    ;!insertmacro MUI_DESCRIPTION_TEXT ${SecSamp} $(DESC_SecSamp)
  ;!insertmacro MUI_FUNCTION_DESCRIPTION_END

