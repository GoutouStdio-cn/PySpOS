#
#   pyspos.py
#   PySpOS Base Information File
#
#   2026/1/31 By GoutouStdio
#   @2022~2026 GoutouStdio. Open all rights.

#   2026/1/31 update log: add this file to store base information of PySpOS!!!
#   2026/1/31 update 2 log: add null value definition, add spui,sunglass definitions

# Null value.
NULL = 0

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
SPC_VERSION = NULL # SpaceConfig is not developed yet, so we think its version is 0

# Select whether to enable Space User Interface.
SPUI_ENABLED = False # SUI2 is disabled for now, because it is not developed yet.

# SPUI Version.
SPUI_VERSION = NULL # SPUI is not developed yet, so we think its version is 0


if SPUI_ENABLED:
    # Select whether to enable SunGlass.
    SUNGALASS_ENABLED = True # SunGlass is true by default.

    # SunGlass Version.
    SUNGALASS_VERSION = NULL # SunGlass is not developed yet, so we think its version is 0
else:
    # You don't need these values, because you have disabled SPUI.
    SUNGALASS_ENABLED = NULL
    SUNGALASS_VERSION = NULL

# Select whether to enable developer mode.
DEVELOPER_MODE = False # Developer mode is disabled by default. You can enable it for development and testing purposes.
