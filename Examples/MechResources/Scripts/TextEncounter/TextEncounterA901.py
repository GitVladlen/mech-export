from Game.TextEncounters.TextEncounter import TextEncounter


class TextEncounterA901(TextEncounter):
    def __init__(self):
        super(TextEncounterA901, self).__init__()
        self.id = "A901"
        self.name = "Name"
        self.type = self.TYPE_ADVENTURE
        
        self.occurrence = self.OCCURRENCE_RECURRING
        self.occurrence = self.OCCURRENCE_RECURRING
        pass

    def _onCheckConditions(self, context):
        
        return True
        pass

    def _onGenerate(self, context, dialog):
        
        outcome = dialog.outcome()

        combat = outcome.combat()
        
        enemy = combat.enemy()
        enemy.prototype = "Enemy_1"
        
        enemy = combat.enemy()
        enemy.prototype = "Enemy_2"

        pass
    pass

""" debug info
------------- Nodes -------------
ID = " A901 "
Name = " Name "
Occurrence = " Recurring "
Dialog = " "
Outcome = " "
Combat = " "
Enemy1 = " Enemy_1 "
Enemy2 = " Enemy_2 "
Occurrence = " Recurring "
------------- Texts -------------

"""
