import os, sys
SCRIPTS = r"H:\AI\YuE\skills\yue2-music\scripts"
sys.path.insert(0, SCRIPTS)
os.chdir(SCRIPTS)
import run_yue2
sys.exit(run_yue2.main())
