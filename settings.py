RUN_MODE_JENKINS = 1
RUN_MODE_PROJECT_DIR = 2
RUN_MODE_LOCAL = 3
RUN_MODE_FROM_PROJECT_LOCAL = 4

RUN_MODE = RUN_MODE_LOCAL

SCRIPT_PAKCAGE_NAME = "ExternalResources"
LOCALE_PACKAGE_NAME = "ExternalLocale"

METAWRITE_EXE_PATH = ".\Metawrite\Metawrite.exe"
METAWRITE_PROTOCOL_PATH = ".\Metawrite\protocol.xml"

# - main run mode ----------------------------------------------------
if RUN_MODE == RUN_MODE_JENKINS:
    EXPORT_PATH = 'd:/Programs/Jenkins/workspace/PythonExec/'

    TEXT_ENCOUNTER_SOURCES_PATH = 'd:/Programs/Jenkins/workspace/PythonExec/Resources'
    QUESTS_SOURCES_PATH = 'd:/Programs/Jenkins/workspace/PythonExec/Resources'
# - for dev -----------------------------------------------------------
elif RUN_MODE == RUN_MODE_PROJECT_DIR:
    EXPORT_PATH = 'd:/Documents/PROJECTS/MECH/'

    TEXT_ENCOUNTER_SOURCES_PATH = 'd:/Documents/PROJECTS/MECH_Work/Params/TextEncounters/'
    QUESTS_SOURCES_PATH = 'd:/Documents/PROJECTS/MECH_Work/Params/Quests/'
# - for dev -----------------------------------------------------------
elif RUN_MODE == RUN_MODE_LOCAL:
    EXPORT_PATH = './Result/'

    TEXT_ENCOUNTER_SOURCES_PATH = './TestData/'
    QUESTS_SOURCES_PATH = './TestData/'
# - for dev -----------------------------------------------------------
elif RUN_MODE == RUN_MODE_FROM_PROJECT_LOCAL:
    EXPORT_PATH = 'D:/Test/'

    TEXT_ENCOUNTER_SOURCES_PATH = 'd:/Documents/PROJECTS/MECH_Work/Params/TextEncounters/'
    QUESTS_SOURCES_PATH = 'd:/Documents/PROJECTS/MECH_Work/Params/Quests/'