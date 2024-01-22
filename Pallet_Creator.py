import sys
from UI import main
sys.modules.pop('unnecessary_module', None)

if __name__ == "__main__":
    main()