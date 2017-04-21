import string
import re


# MAIN =================================================
# ======================================================
_global_te_id = None
_global_texts = []


def parse_encounter_nodes(encounter_nodes):
    global _global_te_id
    global _global_texts

    _global_te_id = get_id_from_nodes(encounter_nodes)
    _global_texts = []

    root = Root(None)
    cur_node = root
    for tag, value in encounter_nodes:
        try:
            cur_node = cur_node.push(tag, value.strip())
        except NoHandleTagException as ex:
            print(ex)
            pass

    script_text = str(root)

    # DEBUG
    # print("=========================", _global_te_id)
    # print(script_text)
    # print("=========================")

    # clear sets of empty lines
    matches = re.findall(r'\n((?:\s*\n){3,})', script_text)
    if matches:
        for match in matches:
            script_text = script_text.replace(match, "\n", 1)

    return _global_te_id, script_text, _global_texts
    pass
# ======================================================

_global_quest_id = None
_global_quest_texts = []

def parse_quest_nodes(nodes):
    global _global_quest_id
    global _global_quest_texts

    _global_quest_id = get_id_from_nodes(nodes)
    _global_quest_texts = []

    quest_root = QuestRoot(None)
    cur_node = quest_root

    for tag, value in nodes:
        try:
            cur_node = cur_node.push(tag, value.strip())
        except NoHandleTagException as ex:
            print(ex)
            pass

    script_text = str(quest_root)

    # clear sets of empty lines
    matches = re.findall(r'\n((?:\s*\n){3,})', script_text)
    if matches:
        for match in matches:
            script_text = script_text.replace(match, "\n", 1)

    return _global_quest_id, script_text, _global_quest_texts
    pass


# BASE CLASSES =========================================
# ======================================================
class Node(object):
    def __init__(self, parent):
        self.parent = parent
        self.params = dict()
        self.to_str_format = ""

        if self.onInit() is False:
            print ("Init failed")

    def onInit(self):
        return self._onInit()

    def _onInit(self):
        return False

    def __str__(self):
        sf = SuperFormatter()
        return sf.format(self.to_str_format, **self.params)


# ======================================================
class ValueNode(Node):
    def parse(self, value):
        return self._parse(value)

    def _parse(self, value):        
        return False


# ======================================================
class ComplexNode(Node): 
    def push(self, tag, value):
        result_node = self._push(tag, value)
        if result_node is None:
            if self.parent is None:
                raise NoHandleTagException("Parent is None", tag, value)
            result_node = self.parent.push(tag, value)
            if result_node is None:
                raise NoHandleTagException("Parent can`t handle tag", tag, value)
        return result_node

    def _push(self, tag, value):
        return None

    def _add_param(self, key, value):
        if isinstance(self.params[key], list):
            self.params[key].append(value)
        else:
            self.params[key] = value

    def addValue(self, key, value, type_=None):
        if type_ is not None:
            node = type_(self)
            if node.parse(value):
                value = node
        self._add_param(key, value)

    def addComplex(self, key, value, type_):
        complex_node = type_(self)
        if value:
            # paragraph feature [br] -> &#10;
            matches = re.findall(r'(\s?\[br\]\s?)', value)
            if matches:
                for match in matches:
                    value = value.replace(match, "&#10;", 1)

            global _global_te_id
            global _global_texts

            TextID = "ID_TE_{ID}_{index}".format(ID=_global_te_id, index=len(_global_texts))
            TextValue = value
            _global_texts.append(dict(key=TextID, value=TextValue))

            complex_node.params["Text"] = TextID
        self._add_param(key, complex_node)
        return complex_node


# DERIVATIVE CLASSES ===================================
# ======================================================
class Root(ComplexNode):
    def _onInit(self):
        self.params.update(dict(
            ID=None,
            Name=None,
            Type=None,
            InitConditions=[],
            Conditions=[],
            Dialog=None,
        ))
# format string ---------------------------------------
        self.to_str_format = """from Game.TextEncounters.TextEncounter import TextEncounter


class TextEncounter{ID}(TextEncounter):
    def __init__(self):
        super(TextEncounter{ID}, self).__init__()
        self.id = "{ID}"
        self.name = "{Name}"
        self.type = {Type}
        {InitConditions:repeat:\n        {{item}}}
        pass

    def _onCheckConditions(self, context):
        {Conditions:if:conditions = [{Conditions:repeat:{{item}}}]
        if not all(conditions):
            return False}
        return True
        pass

    def _onGenerate(self, context, dialog):{Dialog:if:{Dialog}}
        pass
    pass
"""
# -----------------------------------------------------

    def _push(self, tag, value):
        if tag == "ID":
            self.addValue("ID", value)
            self.addValue("Type", value, TypeFromID)
        elif tag == "Name":
            self.addValue("Name", value)
        elif tag == "World":
            self.addValue("InitConditions", value, InitConditionWorld)
        elif tag == "Stages":
            self.addValue("InitConditions", value, InitConditionStages)
        elif tag == "Occurrence":
            self.addValue("InitConditions", value, InitConditionOccurrence)
        elif tag == "Priority":
            self.addValue("InitConditions", value, InitConditionsPriority)
        elif tag == "Frequency":
            self.addValue("InitConditions", value, InitConditionsFrequency)
        elif tag == "Conditions":
            return self.addComplex("Conditions", value, Conditions)
        elif tag == "Dialog":
            return self.addComplex("Dialog", value, Dialog)
        else:
            return None
        return self


# ======================================================
class TypeFromID(ValueNode):
    def _onInit(self):
        self.params["Value"] = None
        self.to_str_format = "{Value}"

    def _parse(self, value):
        match = re.match(r'^(C|A|L|N)\d+', value)
        if match is None:
            return False
        type_name = match.group(1)
        type_name_dict = dict(
            C="self.TYPE_COMBAT",
            A="self.TYPE_ADVENTURE",
            L="self.TYPE_LOOT",
            N="self.TYPE_NOTHING")
        self.params["Value"] = type_name_dict.get(str(type_name))
        return True

# ======================================================
class Dialog(ComplexNode):
    def _onInit(self):
        self.params.update(dict(
            Text = None,
            Options = [],
            Outcome = None,
        ))    
        self.to_str_format = """
        {Text:if:dialog.text = "{Text}"}{Outcome:if:{Outcome}}{Options:if:{Options:repeat:{{item}}}}"""
        
    def _push(self, tag, value):
        if tag == "Option":
            return self.addComplex("Options", value, Option)
        elif tag == "Outcome":
            return self.addComplex("Outcome", value, DialogOutcome)
        else:
            return None
        return self


# =====================================================
class Option(ComplexNode):
    def _onInit(self):
        self.params.update(dict(
            Text = None,
            Conditions = [],
            Outcomes = [],
        ))
        self.to_str_format = """
        option = dialog.option()
        option.text = "{Text}"
        {Outcomes:repeat:{{item}}}
        {Conditions:if:option_conditions = [{Conditions:repeat:{{item}}}]
        if not all(option_conditions):
            dialog.options.remove(option)}
        """

    def _push(self, tag, value):
        if tag == "Conditions":
            return self.addComplex("Conditions", value, Conditions)
        if tag == "Outcome":
            return self.addComplex("Outcomes", value, OptionOutcome)
        else:
            return None
        return self


# =====================================================
class OutcomeNode(ComplexNode):
    def _onInit(self):
        self.params.update(dict(
            Text = None,
            Conditions = [],
            Chance = None,
            Gips = None,
            Mech1 = None,
            Mech2 = None,
            Mech1and2 = None,
            Combat = None,
            QuestActivate = None,
            QuestSuccess = None,
            QuestFail = None,
            LoadTE = None,
            AddKeycard = None,
            UseKeycard = None,
            ReturnHome=None,
            __Entity = None,
            __ConditionNotMet = None,
        ))
        self.to_str_format = """
        outcome = {__Entity}.outcome({Chance:if:{Chance}})
        {LoadTE:if:outcome.load_te = "{LoadTE}"}
        {Text:if:outcome.text = "{Text}"}
        {ReturnHome:if:outcome.return_home = True}
        {Gips:if:{Gips}}
        {Mech1:if:{Mech1}}{Mech2:if:{Mech2}}{Mech1and2:if:{Mech1and2}}
        {QuestActivate:if:{QuestActivate}}
        {QuestSuccess:if:{QuestSuccess}}
        {QuestFail:if:{QuestFail}}
        {Combat:if:{Combat}}
        {AddKeycard:if:{AddKeycard}}
        {UseKeycard:if:{UseKeycard}}
        {Conditions:if:outcome_conditions = [{Conditions:repeat:{{item}}}]
        if not all(outcome_conditions):
            {__ConditionNotMet}}
        """

    def _push(self, tag, value):
        if tag == "Chance":
            self.addValue("Chance", value)
        elif tag == "Gips":
            self.addValue("Gips", value, OutcomeGips)
        elif tag == "Mech1":
            self.addValue("Mech1", value, OutcomeMech1)
        elif tag == "Mech2":
            self.addValue("Mech2", value, OutcomeMech2)
        elif tag == "Mech1&2":
            self.addValue("Mech1and2", value, OutcomeMech1and2)
        elif tag == "QuestActivate":
            self.addValue("QuestActivate", value, OutcomeQuestActivate)
        elif tag == "QuestSuccess":
            self.addValue("QuestSuccess", value, OutcomeQuestSuccess)
        elif tag == "QuestFail":
            self.addValue("QuestFail", value, OutcomeQuestFail)
        elif tag == "AddKeycard":
            self.addValue("AddKeycard", value, OutcomeAddKeycard)
        elif tag == "UseKeycard":
            self.addValue("UseKeycard", value, OutcomeUseKeycard)
        elif tag == "LoadTE":
            self.addValue("LoadTE", value)
        elif tag == "ReturnHome":
            self.addValue("ReturnHome", True)
        elif tag == "Combat":
            return self.addComplex("Combat", value, OutcomeCombat)
        elif tag == "Conditions":
            return self.addComplex("Conditions", value, Conditions)
        else:
            return None
        return self


# =====================================================
class OptionOutcome(OutcomeNode):
    def _onInit(self):
        super(OptionOutcome, self)._onInit()
        self.params.update(dict(
            __Entity = "option",
            __ConditionNotMet = "option.outcomes.remove(outcome)",
        ))


# =====================================================
class DialogOutcome(OutcomeNode):
    def _onInit(self):
        super(DialogOutcome, self)._onInit()
        self.params.update(dict(
            __Entity = "dialog",
            __ConditionNotMet = "dialog.dialog_outcome = None",
        ))


# OUTCOMES ============================================
class OutcomeGips(ValueNode):
    def _onInit(self):
        self.params["Value"] = None
        self.to_str_format = "outcome.gips = {Value}"

    def _parse(self, value):
        rand_match = re.match(r'rand\s*([+-]?\d+)\s+([+-]?\d+)', str(value))
        int_match = re.match(r'([+-]?\d+)', str(value))
        if rand_match:
            from_, to_ = rand_match.groups()
            self.params["Value"] = "self.rand({}, {})".format(from_, to_)
        elif int_match:
            int_value = int_match.group(1)
            self.params["Value"] = int_value
        else:
            return False
        return True


# ===========================================================================================================
class OutcomeMechNodeBase(ValueNode):
    def _onInit(self):
        self.params["Pattern"] = r'(HP|TAP|HE|HPP|TAPP|HEP|HPX|TPX|HEX|HPXP|TPXP|HEXP)\s*(\+|-|=)\s*([\+-]?\d+)'


# ======================================================
class OutcomeMechNode(OutcomeMechNodeBase):
    def _onInit(self):
        super(OutcomeMechNode, self)._onInit()
        self.params.update(dict(
            MechObjectName = None,
            Stats=[],
        ))
        self.to_str_format = """
        mech = outcome.{MechObjectName}(){Stats:repeat:{{item}}}
        """

    def _parse(self, value):
        matches = re.findall(self.params["Pattern"], value)
        if not matches:
            return False

        stats_format = "\n        mech.stats.append((\"{stat}\", \"{operator}\", {number}))"

        for stat, operator, number in matches:
            bones = dict(
                stat=stat,
                operator=operator,
                number=number,
            )
            self.params["Stats"].append(stats_format.format(**bones))
        return True


# ======================================================
class OutcomeMech1(OutcomeMechNode):
    def _onInit(self):
        super(OutcomeMech1, self)._onInit()
        self.params["MechObjectName"] = "mech1"


# ======================================================
class OutcomeMech2(OutcomeMechNode):
    def _onInit(self):
        super(OutcomeMech2, self)._onInit()
        self.params["MechObjectName"] = "mech2"


# ======================================================
class OutcomeMech1and2(OutcomeMechNode):
    def _onInit(self):
        super(OutcomeMech1and2, self)._onInit()
        self.params.update(dict(
            Stats = [],
        ))
        self.to_str_format = """
        mech = outcome.mech1(){Stats:repeat:{{item}}}

        mech = outcome.mech2(){Stats:repeat:{{item}}}
        """

# ======================================================
class OutcomeQuestBase(ValueNode):
    def _onInit(self):
        self.params.update(dict(
            Items=[],
            Method=None,
        ))
        self.to_str_format = "{Items:repeat:\n        outcome.quest(\"{Method}\", \"{{item}}\")}"

    def _parse(self, value):
        items = [item.strip() for item in re.split(r',', str(value))]

        if not items:
            return False

        self.params["Items"] += items
        return True

# =======================================================
class OutcomeQuestActivate(OutcomeQuestBase):
    def _onInit(self):
        super(OutcomeQuestActivate, self)._onInit()
        self.params["Method"] = "Activate"

# =======================================================
class OutcomeQuestSuccess(OutcomeQuestBase):
    def _onInit(self):
        super(OutcomeQuestSuccess, self)._onInit()
        self.params["Method"] = "Success"

# =======================================================
class OutcomeQuestFail(OutcomeQuestBase):
    def _onInit(self):
        super(OutcomeQuestFail, self)._onInit()
        self.params["Method"] = "Fail"


# =======================================================
class OutcomeAddKeycard(ValueNode):
    def _onInit(self):
        self.params["Items"] = []
        self.to_str_format = "{Items:repeat:\n        outcome.keycard(\"Add\",\"{{item}}\")}"

    def _parse(self, value):
        items = [item.strip() for item in re.split(r',', str(value))]
        if not items:
            return False

        self.params["Items"] = items
        return True
        pass


# =====================================================
class OutcomeUseKeycard(ValueNode):
    def _onInit(self):
        self.params["Items"] = []
        self.to_str_format = "{Items:repeat:\n        outcome.keycard(\"Use\",\"{{item}}\")}"

    def _parse(self, value):
        items = [item.strip() for item in re.split(r',', str(value))]
        if not items:
            return False

        self.params["Items"] = items
        return True
        pass


# =====================================================
class OutcomeCombat(ComplexNode):
    def _onInit(self):
        self.params.update(dict(
            Enemy1=None,
            Enemy2=None,
        ))
        self.to_str_format = """
        combat = outcome.combat()
        {Enemy1:if:{Enemy1}}{Enemy2:if:{Enemy2}}
        """

    def _push(self, tag, value):
        if tag == "Enemy1":
            self.addValue("Enemy1", value, OutcomeCombatEnemy)
        elif tag == "Enemy2":
            self.addValue("Enemy2", value, OutcomeCombatEnemy)
        else:
            return None
        return self


# =====================================================
class OutcomeCombatEnemy(ValueNode):
    def _onInit(self):
        self.params.update(dict(
            Prototype=None,
            Stats=[],
        ))
        self.to_str_format = """
        enemy = combat.enemy()
        {Prototype:if:enemy.prototype = "{Prototype}"}{Stats:repeat:{{item}}}
        """

    def _parse(self, value):
        prototype_match = re.match(r'\s*(\w+)\s*', value)
        if not prototype_match:
            return False
        self.params["Prototype"] = prototype_match.group()

        stats_matches = re.findall(r'(HP|TAP|HE|HPP|TAPP|HEP|HPX|TPX|HEX|HPXP|TPXP|HEXP)\s*(\+|-|=)\s*([\+-]?\d+)', value)
        if stats_matches:
            stat_format = "\n        enemy.stats.append((\"{stat}\", \"{operator}\", {number}))"

            for stat, operator, number in stats_matches:
                params = dict(stat=stat, operator=operator, number=number)
                self.params["Stats"].append(stat_format.format(**params))
        return True


# INIT CONDITIONS ======================================
class InitConditionWorld(ValueNode):
    def _onInit(self):
        self.params["World"] = None
        self.to_str_format = "self.world = \"{World}\""

    def _parse(self, value):
        self.params["World"] = value
        return True


# ======================================================
class InitConditionStages(ValueNode):
    def _onInit(self):
        self.params.update(dict(
            From=None,
            To=None,
        ))
        self.to_str_format = "self.stages = range({From}, {To})"

    def _parse(self, value):
        match_two_digits = re.match(r'\s*(\d+)\s+(\d+)\s*', str(value))
        match_one_digit = re.match(r'\s*(\d+)\s*', str(value))

        from_level, to_level = None, None
        if match_two_digits:
            from_level, to_level = map(int, match_two_digits.groups())
        elif match_one_digit:
            from_level = to_level = int(match_one_digit.group())

        if from_level < 0 or to_level < 0:
            print("Invalid Levels") 
            return False

        self.params["From"] = from_level
        self.params["To"] = to_level + 1
        return True
        pass


# =======================================================
class InitConditionOccurrence(ValueNode):
    def _onInit(self):
        self.params["Value"] = None
        self.to_str_format = "self.occurrence = {Value}"

    def _parse(self, value):
        match = re.match(r'(Recurring|Resets|Until completed|Once only)', str(value))

        if not match:
            return False
        bones = {
            "Recurring": "self.OCCURRENCE_RECURRING",
            "Resets": "self.OCCURRENCE_RESETS",
            "Until completed": "self.OCCURRENCE_UNTIL_COMPLETED",
            "Once only": "self.OCCURRENCE_ONLY_ONCE",
        }
        self.params["Value"] = bones[match.group(1)]

        return True
        pass


# =======================================================
class InitConditionsFrequency(ValueNode):
    def _onInit(self):
        self.params["Value"] = None
        self.to_str_format = "self.frequency = {Value}"

    def _parse(self, value):
        match = re.match(r'(\d)', str(value))
        if not match:
            return False
        self.params["Value"] = int(match.group(1))
        return True


# =======================================================
class InitConditionsPriority(ValueNode):
    def _onInit(self):
        self.params["Value"] = None
        self.to_str_format = "self.priority = {Value}"

    def _parse(self, value):
        match = re.match(r'(\d)', str(value))

        if not match:
            return False
        bones = {
            1: "self.PRIORITY_HIGH",
            2: "self.PRIORITY_MID",
            3: "self.PRIORITY_LOW",
        }
        self.params["Value"] = bones[int(match.group(1))]

        return True
        pass


# CONDITIONS ============================================
class Conditions(ComplexNode):
    def _onInit(self):
        self.params.update(dict(
            Mech1 = None,
            Mech2 = None,
            Mech1and2 = None,
            Mech1or2 = None,
            QuestActive = None,
            QuestSuccess = None,
            QuestFail = None,
            Cargo = None,
            Keycard = None,
            CargoItemName = None,
            CargoItemType = None,
        ))
        self.to_str_format = "{Mech1:if:{Mech1}}" \
                             "{Mech2:if:{Mech2}}" \
                             "{Mech1and2:if:{Mech1and2}}" \
                             "{Mech1or2:if:{Mech1or2}}" \
                             "{QuestActive:if:{QuestActive}}" \
                             "{QuestSuccess:if:{QuestSuccess}}" \
                             "{QuestFail:if:{QuestFail}}" \
                             "{Cargo:if:{Cargo}}" \
                             "{Keycard:if:{Keycard}}" \
                             "{CargoItemName:if:{CargoItemName}}" \
                             "{CargoItemType:if:{CargoItemType}}"

    def _push(self, tag, value):
        if tag == "Mech1":
            self.addValue("Mech1", value, ConditionMech1)
        elif tag == "Mech2":
            self.addValue("Mech2", value, ConditionMech2)
        elif tag == "Mech1&2":
            self.addValue("Mech1and2", value, ConditionMech1and2)
        elif tag == "Mech1or2":
            self.addValue("Mech1or2", value, ConditionMech1or2)
        elif tag == "QuestActive":
            self.addValue("QuestActive", value, ConditionQuestActive)
        elif tag == "QuestSuccess":
            self.addValue("QuestSuccess", value, ConditionQuestSuccess)
        elif tag == "QuestFail":
            self.addValue("QuestFail", value, ConditionQuestFail)
        elif tag == "Cargo":
            self.addValue("Cargo", value, ConditionCargo)
        elif tag == "Keycard":
            self.addValue("Keycard", value, ConditionKeycard)
        elif tag == "CargoItemName":
            self.addValue("CargoItemName", value, ConditionCargoItemName)
        elif tag == "CargoItemType":
            self.addValue("CargoItemType", value, ConditionCargoItemType)
        else:
            return None
        return self


# ======================================================
class ConditionMechNodeBase(ValueNode):
    def _onInit(self):
        self.params["Pattern"] = r'(HP|TAP|HE|HPP|TAPP|HEP|HPX|TPX|HEX)\s*(>|>=|<|<=|==|!=)\s*([\+-]?\d+)'


# ======================================================
class ConditionMechNode(ConditionMechNodeBase):
    def _onInit(self):
        super(ConditionMechNode, self)._onInit()
        self.params.update(dict(
            Items = [],
            MechObjectName = None,
        ))
        self.to_str_format = "{Items:repeat:\n            context.{MechObjectName}.{{item}},}"

    def _parse(self, value):
        matches = re.findall(self.params["Pattern"], value)
        if not matches:
            return False
        format_string = "{stat} {operator} {number}"
        for stat, operator, number in matches:
            bones = dict(
                stat=stat.lower(),
                operator=operator,
                number=number,
            )
            self.params["Items"].append(format_string.format(**bones))
        return True


# ======================================================
class ConditionMech1(ConditionMechNode):
    def _onInit(self):
        super(ConditionMech1, self)._onInit()
        self.params["MechObjectName"] = "mech1"


# ======================================================
class ConditionMech2(ConditionMechNode):
    def _onInit(self):
        super(ConditionMech2, self)._onInit()
        self.params["MechObjectName"] = "mech2"


# ======================================================
class ConditionMech1and2(ConditionMechNodeBase):
    def _onInit(self):
        super(ConditionMech1and2, self)._onInit()
        self.params.update(dict(
            Items = [],
        ))
        self.to_str_format = "{Items:repeat:" \
                             "\n            context.mech1.{{item}} and context.mech2.{{item}}," \
                             "}"

    def _parse(self, value):
        matches = re.findall(self.params["Pattern"], value)
        if not matches:
            return False
        format_string = "{stat} {operator} {number}"
        for stat, operator, number in matches:
            bones = dict(
                stat=stat.lower(),
                operator=operator,
                number=number,
            )
            self.params["Items"].append(format_string.format(**bones))
        return True


# ======================================================
class ConditionMech1or2(ConditionMechNodeBase):
    def _onInit(self):
        super(ConditionMech1or2, self)._onInit()
        self.params.update(dict(
            Items = [],
        ))
        self.to_str_format = "{Items:repeat:" \
                             "\n            context.mech1.{{item}} or context.mech2.{{item}}," \
                             "}"

    def _parse(self, value):
        matches = re.findall(self.params["Pattern"], value)
        if not matches:
            return False
        format_string = "{stat} {operator} {number}"
        for stat, operator, number in matches:
            bones = dict(
                stat=stat.lower(),
                operator=operator,
                number=number,
            )
            self.params["Items"].append(format_string.format(**bones))
        return True


# ======================================================
class ConditionQuestBase(ValueNode):
    def _onInit(self):
        self.params.update(dict(
            Items=[],
            Method=None,
        ))
        self.to_str_format = "{Items:repeat:\n            context.{Method}(\"{{item}}\") is True,}"

    def _parse(self, value):
        items = [item.strip() for item in re.split(r',', str(value))]

        if not items:
            return False

        self.params["Items"] += items
        return True


# =======================================================
class ConditionQuestActive(ConditionQuestBase):
    def _onInit(self):
        super(ConditionQuestActive, self)._onInit()
        self.params["Method"] = "isQuestActive"


# =======================================================
class ConditionQuestSuccess(ConditionQuestBase):
    def _onInit(self):
        super(ConditionQuestSuccess, self)._onInit()
        self.params["Method"] = "isQuestSuccess"


# =======================================================
class ConditionQuestFail(ConditionQuestBase):
    def _onInit(self):
        super(ConditionQuestFail, self)._onInit()
        self.params["Method"] = "isQuestFail"


# =======================================================
class ConditionKeycard(ValueNode):
    def _onInit(self):
        self.params["Items"] = []
        self.to_str_format = "{Items:repeat:\n            context.hasKeycard(\"{{item}}\") is True,}"

    def _parse(self, value):
        items = [item.strip() for item in re.split(r',', str(value))]
        if not items:
            return False

        self.params["Items"] = items
        return True
        pass


# =======================================================
class ConditionCargo(ValueNode):
    def _onInit(self):
        self.params.update(dict(
            Full=None,
            Operator=None,
            Value=None,
        ))
        self.to_str_format = "{Full:if:\n            context.isCargoFull() is {Full},}" \
                             "{Value:if:\n            context.getCargoValue() {Operator} {Value},}"

    def _parse(self, value):
        full_match = re.search(r'\s*(Full|Not Full)\s*', str(value))
        value_match = re.search(r'\s*Value\s*(>|>=|<|<=|==)\s*(\d+)\s*', str(value))
        print ("[MATCH] value='{}' match={}".format(value, value_match))
        if full_match:
            bones = {
                "Full": "True",
                "Not Full": "False",
            }
            self.params["Full"] = bones[full_match.group(1)]

        if value_match:
            self.params["Operator"] = value_match.group(1)
            self.params["Value"] = value_match.group(2)

        if not (full_match or value_match):
            return False

        return True
        pass


# =====================================================
class ConditionCargoItemName(ValueNode):
    def _onInit(self):
        self.params["Items"] = []
        self.to_str_format = "{Items:repeat:\n            context.isCargoItemName(\"{{item}}\") is True,}"

    def _parse(self, value):
        items = re.findall(r'\s*(\w+\s*)\s*,?\s*', str(value))
        if not items:
            return False

        self.params["Items"] = items
        return True
        pass


# =====================================================
class ConditionCargoItemType(ValueNode):
    def _onInit(self):
        self.params["Items"] = []
        self.to_str_format = "{Items:repeat:\n            context.isCargoItemType(\"{{item}}\") is True,}"

    def _parse(self, value):
        items = re.findall(r'\s*(\w+\s*)\s*,?\s*', str(value))
        if not items:
            return False

        self.params["Items"] = items
        return True
        pass


# Quests ===============================================
# ======================================================
class QuestRoot(ComplexNode):
    def _onInit(self):
        self.params.update(dict(
            ID=None,
            Name=None,
            Recurrence=None,
        ))
# format string ---------------------------------------
        self.to_str_format = """from Game.Quests.QuestCALN import QuestCALN


class Quest{ID}(QuestCALN):
    def __init__(self):
        super(Quest{ID}, self).__init__()
        self.id = "{ID}"
        self.name = "{Name}"{Recurrence:if:{Recurrence}}
        pass
    pass
"""
# -----------------------------------------------------

    def _push(self, tag, value):
        if tag == "ID":
            self.addValue("ID", value)
        elif tag == "Name":
            self.addValue("Name", value)
        elif tag == "Recurrence":
            self.addValue("Recurrence", value, ValueRecurrence)
        else:
            return None
        return self


#======================================================
class ValueRecurrence(ValueNode):
    def _onInit(self):
        self.params["Value"] = None
        self.to_str_format = "{Value:if:\n        self.recurrence = {Value}}"

    def _parse(self, value):
        value = value.strip().upper()

        value_dict = dict(
            REDO = "self.RECURRENCE_REDO",
            ENDLESS = "self.RECURRENCE_ENDLESS",
            ONCE = "self.RECURRENCE_ONCE",
        )

        self.params["Value"] = value_dict.get(value)

        return True
        pass



# UTILS ===============================================
# =====================================================
def get_id_from_nodes(nodes):
    for tag, value in nodes:
        if tag == "ID":
            return value.strip()
    return None

class NoHandleTagException(Exception):
    def __init__(self, message, tag, value):
        self.message = message
        self.tag = tag
        self.value = value

    def __str__(self):
        return "[TAG EXCEPTION] MESSAGE='{ex.message}' TAG='{ex.tag}' VALUE='{ex.value}'".format(ex=self)


# ======================================================
class SuperFormatter(string.Formatter):
    """World's simplest Template engine."""

    def format_field(self, value, spec):
        if spec.startswith('repeat'):
            template = spec.partition(':')[-1]
            if type(value) is dict:
                value = value.items()
            return ''.join([template.format(item=item) for item in value])
        elif spec == 'call':
            return value()
        elif spec.startswith('if'):
            return (value and spec.partition(':')[-1]) or ''
        else:
            return super(SuperFormatter, self).format_field(value, spec)
# ====================================================