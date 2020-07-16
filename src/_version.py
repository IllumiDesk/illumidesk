"""illumidesk version info"""

# for now, update the version so that its the same as the one reflected
# within the repo's root package.json
version_info = (
    0,
    8,
    2,
)
__version__ = ".".join(map(str, version_info[:3]))

if len(version_info) > 3:
    __version__ = "%s%s" % (__version__, version_info[3])
