import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "lib3d"))
import showcase_comp; showcase_comp.main(HERE)
