import os
import sys

import teparser

def main():

    print ("This is main from export.py")
    
    # exportTextEncountersResources(projectName, ProjectPath, ParamsPath, "Locale_RU", "Resources", "Scripts/TextEncounter", "PathTextEncounter.xlsx")

    exportTextEncountersResources()

    pass

# ----------------------------------------- Text Encounters -----------------------------------------
# def exportTextEncountersResources(projectName, ProjectPath, ParamsPath, LocaleDir, ResourceDir, DataDir, DataFile):
def exportTextEncountersResources():
    """
    :param projectName:
    :param ProjectPath:
    :param ParamsPath:
    :param LocaleDir (ex. "Locale_RU"):
    :param ResourceDir (ex. "Resources"):
    :param DataDir (ex. "Scripts/TextEncounter"):
    :param DataFile (ex. "PathTextEncounter.xlsx"):
    """

    ProjectPath = 'd:/Programs/Jenkins/workspace/PythonExec/'
    ParamsPath = ProjectPath
    LocaleDir = "Locale/"
    ResourceDir = ""
    DataDir = ""
    DataFile = ""

    # list of docx file for export
    resourceList = ["TextEncounters1"]

    # create export directory
    ExportPath = 'd:/Programs/Jenkins/workspace/PythonExec/'

    ExportDirectory = os.path.join(ExportPath, "Module/")
    if not os.path.exists(ExportDirectory):
        os.makedirs(ExportDirectory)
        pass

    # create export TextEncounter script path
    scriptPath = os.path.join(ExportDirectory, "TextEncounter/")

    directory = os.path.dirname(scriptPath)
    if not os.path.exists(directory):
        os.makedirs(directory)
        pass

    # create textx resources export directory
    texts_filename = os.path.join(ExportDirectory, LocaleDir, "TextEncounterTexts.xml")

    directory = os.path.dirname(texts_filename)
    if not os.path.exists(directory):
        os.makedirs(directory)
        pass

    # export logic
    all_texts = []
    reg_info = []

    for row in resourceList:
        if not row:
            continue

        docx_path = row

        docxFileName = "%s%s.docx"%(ParamsPath, docx_path)

        print (" EXPORT TE DOCX='{}'".format(docxFileName))
        scripts, texts = teparser.process(docxFileName)

        for (te_id, script_text) in scripts:
            print (" EXPORT TE ID={}".format(te_id))

            type_name = "TextEncounter{}".format(te_id)
            generateFilename = os.path.join(scriptPath, type_name + ".py")

            with open(generateFilename, "w") as f:
                f.write(script_text)

            reg_info.append((te_id, type_name))
            pass

        all_texts += texts
        pass

    # write text resources
    texts = teparser.format_texts(all_texts)

    with open(texts_filename, "w") as f:
        f.write(texts)

    # test for register in __init__.py
    with open(scriptPath + "__init__.py", "w") as init_file:
        init_file.write("from Game.TextEncounters.TextEncounterManager import TextEncounterManager\n\n\n")
        reg_format = "TextEncounterManager.addTextEncounter(\"{ID}\", \"{Module}\", \"{TypeName}\")\n"
        for (te_id, type_name) in reg_info:
            reg_line = reg_format.format(ID=te_id, Module="TextEncounter", TypeName=type_name)
            init_file.write(reg_line)
            pass
        pass
    pass

if __name__ == "__main__":
    main()
    pass