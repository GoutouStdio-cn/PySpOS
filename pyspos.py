#
#   pyspos.py
#   PySpOS Base Information File
#
#   2026/1/31 By GoutouStdio
#   @2022~2026 GoutouStdio. Open all rights.

#   2026/1/31 update log: add this file to store base information of PySpOS!!!
#   ...


# OS Name.
OS_NAME = "PySpOS"

# OS Major Version. (0~99)
OS_MAJOR_VER = 3

# OS Develop stage. 
#   Possible values: "alpha", "beta", "stable"
#   "alpha": Early development stage, may contain many bugs and incomplete features.
#   "beta": Feature complete, but may still contain bugs. More stable than alpha.
#   "stable": Official release, thoroughly tested and stable for general use.
#   You can change this value to your custom format, but you need change parse_spf to truely use it.
OS_DEVELOP_STAGE = "beta"

# OS Minor Version. (0~99)
OS_MINOR_VER = 1

# Full OS Version String.
OS_VERSION = f"{OS_MAJOR_VER}.{OS_MINOR_VER}"

# OS Vendor. (your Company/Author Name)
OS_VENDOR = "GoutouStdio"

# OS Copyright.
OS_COPYRIGHT = "@2022~2026 GoutouStdio. Open all rights."

# Select whether to enable spf support.
SPF_ENABLED = True

# SPF parser version.
SPF_VERSION = "0.1" # The spf parser is too simple, so we think the version should be 0.1.

# Select whether to enable SpaceConfig.
SPC_ENABLED = False # SpaceConfig is disabled for now, because it is not developed yet.

# SpaceConfig Version.
SPC_VERSION = 0 # SpaceConfig is not developed yet, so we think its version is 0

# Select whether to enable developer mode.
DEVELOPER_MODE = False # Developer mode is disabled by default. You can enable it for development and testing purposes.