import sys
import traceback
import os

try:
    from app import main
    main()
except Exception:
    if sys.executable.endswith("pythonw.exe"):
        with open(os.path.join(os.environ.get("LOCALAPPDATA", "."), "jira-us-creator", "crash.log"), "w") as f:
            f.write(traceback.format_exc())
        from ctypes import windll, c_int, byref
        windll.user32.MessageBoxW(0, "Erreur au lancement de l'application.\n\n%s" % traceback.format_exc(), "Erreur", 0x10)
    else:
        traceback.print_exc()
        input("\nAppuyez sur une touche pour quitter...")
