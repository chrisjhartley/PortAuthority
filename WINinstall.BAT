@echo Downloading Python for Windows - version 3.11.3.
@powershell.exe "Invoke-WebRequest https://python.org/ftp/python/3.11.3/python-3.11.3-amd64.exe -OutFile python_installer.exe -PassThru"
@echo Installing Python...
@.\python_installer.exe /passive
@echo Downloading npcap
@powershell.exe "Invoke-WebRequest https://npcap.com/dist/npcap-1.75.exe -Outfile npcap_installer.exe"
@echo Running npcap installer.  Please click through it.
@.\npcap_installer.exe
@echo OK that's the prereqs...
@@echo Create python link.
@REM #mklink /d %UserProfile%\Desktop\PortAuthority\python.lnk %LocalAppData%\Programs\Python\Python311\python.exe
@REM Only admins can create symlinks in Windows for exactly no reason at all.  Creating the link as Admin makes it 
@REM innaccessible to non-admins.  It's just fundamentally broken like everything else in this hellscape of an OS.
@#@%UserProfile%\Desktop\PortAuthority\python.lnk
REM @%LocalAppData%\Programs\Python\Python311\python.exe
