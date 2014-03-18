import atexit
import sys


def main():
    if '-MMD' in sys.argv and '-MF' in sys.argv:
        sys.argv.remove('-MMD')
        idx = sys.argv.index('-MF')
        deps_file = sys.argv[idx + 1]
        sys.argv = sys.argv[:idx] + sys.argv[idx + 2:]
        atexit.register(write_deps, deps_file, sys.argv[1])

    fname = sys.argv[1]
    sys.argv = sys.argv[1:]
    __import__(fname.replace('/', '.').replace('.py', ''))


def write_deps(deps_file, source_file):
    deps = [source_file]
    for m in list(sys.modules.values()):
        mf = getattr(m, '__file__', None)
        if mf and (not mf.startswith('/System') and
                   not mf.startswith('/Library')):
            deps.append(mf.replace('.pyc', '.py').replace(' ', '\\ '))

    with open(deps_file, 'w') as df:
        df.write("%s : %s\n" % (source_file.replace('.py', '.pyc'),
                                ' '.join(deps)))


if __name__ == '__main__':
    main()
