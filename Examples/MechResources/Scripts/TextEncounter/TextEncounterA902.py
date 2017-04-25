from Game.TextEncounters.TextEncounter import TextEncounter


class TextEncounterA902(TextEncounter):
    def __init__(self):
        super(TextEncounterA902, self).__init__()
        self.id = "A902"
        self.name = "Name"
        self.type = self.TYPE_ADVENTURE
        
        self.occurrence = self.OCCURRENCE_RECURRING
        pass

    def _onCheckConditions(self, context):
        
        return True
        pass

    def _onGenerate(self, context, dialog):
        dialog.text = "ID_TE_A902_0"
        option = dialog.option()
        option.text = "ID_TE_A902_1"
        
        outcome = option.outcome()

        outcome.gips = 100
        
        
        outcome.quest("Activate", "Q101")

        option = dialog.option()
        option.text = "ID_TE_A902_2"
        
        outcome = option.outcome()

        outcome.quest("Success", "Q101")
        
        
        combat = outcome.combat()
        
        enemy = combat.enemy()
        enemy.prototype = "Enemy_3"

        option_conditions = [
            context.isQuestActive("Q101") is True,]
        if not all(option_conditions):
            dialog.options.remove(option)
        
        option = dialog.option()
        option.text = "ID_TE_A902_3"
        
        outcome = option.outcome()

        outcome.keycard("Add","Red Flame")

        option = dialog.option()
        option.text = "ID_TE_A902_4"
        
        outcome = option.outcome()

        outcome.keycard("Use","Red Flame")
        
        
        option_conditions = [
            context.hasKeycard("Red Flame") is True,]
        if not all(option_conditions):
            dialog.options.remove(option)
        
        pass
    pass

""" debug info
------------- Nodes -------------
ID = " A902 "
Name = " Name "
Occurrence = " Recurring "
Dialog = " Adventure "
Option = " Option 1 "
Outcome = " "
Gips = " 100 "
QuestActivate = " Q101 "
Option = " Option 2 "
Conditions = " "
QuestActive = " Q101 "
Outcome = " "
Combat = " "
Enemy1 = " Enemy_3 "
QuestSuccess = " Q101 "
Option = " Option 3 "
Outcome = " "
AddKeycard = " Red Flame "
Option = " Option 4 "
Conditions = " "
Keycard = " Red Flame "
Outcome = " "
UseKeycard = " Red Flame "
------------- Texts -------------
<Text Key="ID_TE_A902_0" Value="Adventure"/>
<Text Key="ID_TE_A902_1" Value="Option 1"/>
<Text Key="ID_TE_A902_2" Value="Option 2"/>
<Text Key="ID_TE_A902_3" Value="Option 3"/>
<Text Key="ID_TE_A902_4" Value="Option 4"/>
"""
