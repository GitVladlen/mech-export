import os
import sys

import teparser


# ---------------------------------------------------------------------------------------------------
def main():
    """
    ---------------------------------
    Structure:
    ---------------------------------
    + MechLocale/
    -- Pak.xml
    -- TextEncounterTexts.xml
    -- QuestTexts.xml
    + MechResources/
    -- Pak.xml
    -+ Scripts/
    --+ TextEncounter/
    ---- __init__.py
    ---- TextEncounter<ID>.py
    ---- ...
    --+ Quests/
    ---- __init__.py
    ---- Quest<ID>.py
    ---- ...
    ---------------------------------
    
    1. create dirs
    2. parse
    3. write files
    4. write Paks
    """

    # list of files for export
    # must be gained from google drive
    ResourceList = ["TextEncounters1"]

    PackageName = "MechResources"
    
    ExportPath = 'd:/Programs/Jenkins/workspace/PythonExec/'
    ResourcePath = 'd:/Programs/Jenkins/workspace/PythonExec/Resources'

    export(ExportPath, PackageName, ResourcePath, ResourceList)

    # write Pak.xml
    PakScriptsList = [
        dict(Path = "TextEncounter/", Module="TextEncounter"),
        dict(Path = "Quests/", Module="Quests"),
    ]
    PakTextsList = [
        dict(Path = "TextEncounterTexts.xml"),
        dict(Path = "QuestTexts.xml"),
    ]
    write_pak(ExportPath, PackageName, PakScriptsList, PakTextsList)
    pass

# ----------------------------------------- Utils -----------------------------------------
def create_dir(path, *args):
    directory = os.path.join(path, *args)
    if not os.path.exists(directory):
        os.makedirs(directory)
        pass
    pass

def write_script(TypeName, ScriptDir, ScriptText):
    ScriptFileName = "%s.py"%(TypeName)
    ScriptFilePath = os.path.join(ScriptDir, ScriptFileName)

    with open(ScriptFilePath, "w") as f:
        f.write(ScriptText)
    pass

def write_texts(AllTexts, TextFileName):
    texts = teparser.format_texts(AllTexts)

    with open(TextFileName, "w") as f:
        f.write(texts)
    pass

def write_init(ScriptDir, reg_info):
    with open(ScriptDir + "__init__.py", "w") as init_file:
        init_file.write("from Game.TextEncounters.TextEncounterManager import TextEncounterManager\n\n\n")
        reg_format = "TextEncounterManager.addTextEncounter(\"{ID}\", \"{Module}\", \"{TypeName}\")\n"
        for (te_id, type_name) in reg_info:
            reg_line = reg_format.format(ID=te_id, Module="TextEncounter", TypeName=type_name)
            init_file.write(reg_line)
            pass
        pass
    pass

def write_pak(ExportPath, PackageName, ScriptsDesc, TextsDesc):
    pak_format_string = """
<Pak>
{Scripts}
    <Texts>
{Texts}
    </Texts>
</Pak>"""
    script_format_string = "    <Scripts Path = \"{Path}\" Module = \"{Module}\"/>"
    text_format_string = "        <Text Path = \"{Path}\"/>"

    scripts_lines = []
    for script_desc in ScriptsDesc:
        scripts_lines.append(script_format_string.format(**script_desc))
        pass

    texts_lines = []
    for text_desc in TextsDesc:
        texts_lines.append(text_format_string.format(**text_desc))

    ScriptsParam = "\n".join(scripts_lines)
    TextsParam = "\n".join(texts_lines)

    PakText = pak_format_string.format(Scripts=ScriptsParam, Texts=TextsParam)

    PakFilePath = os.path.join(ExportPath, PackageName + "/Pak.xml")
    with open(PakFilePath, "w") as f:
        f.write(PakText)
        pass
    pass

# ----------------------------------------- Text Encounters -----------------------------------------
def export(ExportPath, PackageName, ResourcePath, ResourceList):

    ExportDir = os.path.join(ExportPath, PackageName + "/")
    ScriptDir = os.path.join(ExportDir, "TextEncounter/")
    TextDir = os.path.join(ExportDir, "Locale/")

    TextFileName = os.path.join(TextDir, "TextEncounterTexts.xml")

    create_dir(ExportDir)
    create_dir(ScriptDir)
    create_dir(TextDir)

    # export logic
    all_texts = []
    reg_info = []

    for ResourceName in ResourceList:
        if not ResourceName:
            continue

        ResourceFileName = "%s.docx"%(ResourceName)
        ResourceFilePath = os.path.join(ResourcePath, ResourceFileName)

        # debug log
        print (" EXPORT TE DOCX='{}'".format(ResourceFilePath))

        scripts, texts = teparser.process(ResourceFilePath)
        for (te_id, script_text) in scripts:
            # debug log
            print (" EXPORT TE ID={}".format(te_id))

            type_name = "TextEncounter{}".format(te_id)

            write_script(type_name, ScriptDir, script_text)

            reg_info.append((te_id, type_name))
            pass

        all_texts += texts
        pass

    # write text resources
    write_texts(all_texts, TextFileName)

    # test for register in __init__.py
    write_init(ScriptDir, reg_info)
    pass

# ---------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
    pass
# ---------------------------------------------------------------------------------------------------