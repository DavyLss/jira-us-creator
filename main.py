import sys
import os
import traceback
import logging
import shutil

if len(sys.argv) > 1 and sys.argv[1] == "--uninstall":
    LOG_DIR = os.path.join(os.environ.get("LOCALAPPDATA", "."), "jira-us-creator")
    desktop = os.path.join(os.environ.get("USERPROFILE", "."), "Desktop")
    for name in ["Jira US Creator.lnk", "JiraUSCreator.lnk"]:
        p = os.path.join(desktop, name)
        if os.path.exists(p):
            os.remove(p)
    if os.path.exists(LOG_DIR):
        shutil.rmtree(LOG_DIR, ignore_errors=True)
    bat_path = os.path.join(os.environ.get("TEMP", "."), "_uninstall_jira.bat")
    with open(bat_path, "w") as f:
        f.write('@echo off\nping 127.0.0.1 -n 2 >nul\n')
        f.write('del /F /Q "%s"\n' % os.path.abspath(sys.executable))
        f.write('del /F /Q "%s"\n' % bat_path)
    os.startfile(bat_path)
    sys.exit(0)

LOG_DIR = os.path.join(os.environ.get("LOCALAPPDATA", "."), "jira-us-creator")
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "app.log"),
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s")

try:
    from app import main
    main()
except Exception:
    err = traceback.format_exc()
    logging.exception("Fatal error")
    if sys.executable.endswith("pythonw.exe"):
        from ctypes import windll, c_int, byref
        windll.user32.MessageBoxW(0, "Erreur au lancement:\n\n%s" % err, "Erreur", 0x10)
    else:
        print(err)
        input("\nAppuyez sur une touche pour quitter...")
