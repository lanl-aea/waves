import os
env = Environment(ENV=os.environ.copy())

SConscript(dirs='.', variant_dir='build', duplicate=False)
SConscript(dirs='docs', variant_dir='build/docs')
