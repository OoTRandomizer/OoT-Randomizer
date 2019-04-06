import random


class Hint(object):
    name = ""
    text = ""
    type = ""

    def __init__(self, name, text, type, choice=None):
        self.name = name
        self.type = type

        if isinstance(text, str):
            self.text = text
        else:
            if choice == None:
                self.text = random.choice(text)
            else:
                self.text = text[choice]


def getHint(name, clearer_hint=False):
    textOptions, clearText, type = hintTable[name]
    if clearer_hint:
        if clearText == None:
            return Hint(name, textOptions, type, 0)
        return Hint(name, clearText, type)
    else:
        return Hint(name, textOptions, type)


def getHintGroup(group, world):
    ret = []
    for name in hintTable:

        # Some hints have a confusing text in the scope of grotto entrance shuffle so we exclude them
        if world.shuffle_grotto_entrances:
            if name == 'GS Hyrule Castle Grotto' or name == 'GS Hyrule Field Near Gerudo Valley':
                continue

        hint = getHint(name, world.clearer_hints)

        # 10 Big Poes does not require hint if 3 or less required.
        if name == '10 Big Poes' and world.big_poe_count <= 3:
            hint.type = 'overworld'

        if hint.type == group and not (name in hintExclusions(world)):
            ret.append(hint)
    return ret


# table of hints, format is (name, hint text, clear hint text, type of hint) there are special characters that are read for certain in game commands:
# ^ is a box break
# & is a new line
# @ will print the player name
# # sets color to white (currently only used for dungeon reward hints).
hintTable = {
    'Magic Meter':                                              (["mystic training", "pixie dust", "a green rectangle"], "a Magic Meter", 'item'),
    'Double Defense':                                           (["a white outline", "damage decrease", "strengthened love"], "Double Defense", 'item'),
    'Slingshot':                                                (["a seed shooter", "a rubberband", "a child's catapult"], "a Slingshot", 'item'),
    'Boomerang':                                                (["a banana", "a stun stick"], "the Boomerang", 'item'),
    'Bow':                                                      (["an archery enabler", "a danger dart launcher"], "a Bow", 'item'),
    'Bomb Bag':                                                 (["an explosive container", "a blast bag"], "a Bomb Bag", 'item'),
    'Progressive Hookshot':                                     (["Dampe's keepsake", "the Grapple Beam", "the BOING! chain"], "a Hookshot", 'item'),
    'Progressive Strength Upgrade':                             (["power gloves", "metal mittens", "the heavy lifty"], "a Strength Upgrade", 'item'),
    'Progressive Scale':                                        (["a deeper dive", "a piece of Zora"], "a Zora Scale", 'item'),
    'Hammer':                                                   (["the dragon smasher", "the metal mallet", "the heavy hitter"], "the Megaton Hammer", 'item'),
    'Iron Boots':                                               (["sink shoes", "clank cleats"], "the Iron Boots", 'item'),
    'Hover Boots':                                              (["butter boots", "sacred slippers", "spacewalkers"], "the Hover Boots", 'item'),
    'Kokiri Sword':                                             (["a butter knife", "a starter slasher", "a switchblade"], "the Kokiri Sword", 'item'),
    'Biggoron Sword':                                           (["the biggest blade", "a colossal cleaver"], "the Biggoron Sword", 'item'),
    'Master Sword':                                             (["evil's bane"], "the Master Sword", 'item'),
    'Deku Shield':                                              (["a wooden ward", "a burnable barrier"], "a Deku Shield", 'item'),
    'Hylian Shield':                                            (["a steel safeguard", "Like Like's metal meal"], "a Hylian Shield", 'item'),
    'Mirror Shield':                                            (["the reflective rampart", "Medusa's weakness", "a silvered surface"], "the Mirror Shield", 'item'),
    'Farores Wind':                                             (["teleportation", "a relocation rune", "a green ball", "a green gust"], "Farore's Wind", 'item'),
    'Nayrus Love':                                              (["a safe space", "an impregnable aura", "a blue barrier", "a blue crystal"], "Nayru's Love", 'item'),
    'Dins Fire':                                                (["an inferno", "a heat wave", "a red ball"], "Din's Fire", 'item'),
    'Fire Arrows':                                              (["the furnace firearm", "the burning bolts", "a magma missile"], "the Fire Arrows", 'item'),
    'Ice Arrows':                                               (["the refrigerator rocket", "the frostbite bolts", "an iceberg maker"], "the Ice Arrows", 'item'),
    'Light Arrows':                                             (["the shining shot", "the luminous launcher", "Ganondorf's bane", "the lighting bolts"], "the Light Arrows", 'item'),
    'Lens of Truth':                                            (["a lie detector", "a ghost tracker", "true sight", "a detective's tool"], "the Lens of Truth", 'item'),
    'Ocarina':                                                  (["a flute", "a music maker"], "an Ocarina", 'item'),
    'Goron Tunic':                                              (["ruby robes", "fireproof fabric", "cooking clothes"], "a Goron Tunic", 'item'),
    'Zora Tunic':                                               (["a sapphire suit", "scuba gear", "a swimsuit"], "a Zora Tunic", 'item'),
    'Epona':                                                    (["a horse", "a four legged friend"], "Epona", 'item'),
    'Zeldas Lullaby':                                           (["a song of royal slumber", "a triforce tune"], "Zelda's Lullaby", 'item'),
    'Eponas Song':                                              (["an equestrian etude", "Malon's melody", "a ranch song"], "Epona's Song", 'item'),
    'Sarias Song':                                              (["a song of dancing Gorons", "Saria's phone number"], "Saria's Song", 'item'),
    'Suns Song':                                                (["Sunny Day", "the ReDead's bane", "the Gibdo's bane"], "the Sun's Song", 'item'),
    'Song of Time':                                             (["a song 7 years long", "the tune of ages"], "the Song of Time", 'item'),
    'Song of Storms':                                           (["Rain Dance", "a thunderstorm tune", "windmill acceleration"], "the Song of Storms", 'item'),
    'Minuet of Forest':                                         (["the song of tall trees", "an arboreal anthem", "a green spark trail"], "the Minuet of Forest", 'item'),
    'Bolero of Fire':                                           (["a song of lethal lava", "a red spark trail", "a volcanic verse"], "the Bolero of Fire", 'item'),
    'Serenade of Water':                                        (["a song of a damp ditch", "a blue spark trail", "the lake's lyric"], "the Serenade of Water", 'item'),
    'Requiem of Spirit':                                        (["a song of sandy statues", "an orange spark trail", "the desert ditty"], "the Requiem of Spirit", 'item'),
    'Nocturne of Shadow':                                       (["a song of spooky spirits", "a graveyard boogie", "a haunted hymn", "a purple spark trail"], "the Nocturne of Shadow", 'item'),
    'Prelude of Light':                                         (["a luminous prologue melody", "a yellow spark trail", "the temple traveler"], "the Prelude of Light", 'item'),
    'Bottle':                                                   (["a glass container", "an empty jar", "encased air"], "a Bottle", 'item'),
    'Bottle with Letter':                                       (["a call for help", "the note that Mweeps", "an SOS call", "a fishy stationery"], "Ruto's Letter", 'item'),
    'Bottle with Milk':                                         (["cow juice", "a white liquid", "a baby's breakfast"], "a Milk Bottle", 'item'),
    'Bottle with Red Potion':                                   (["a vitality vial", "a red liquid"], "a Red Potion Bottle", 'item'),
    'Bottle with Green Potion':                                 (["a magic mixture", "a green liquid"], "a Green Potion Bottle", 'item'),
    'Bottle with Blue Potion':                                  (["an ailment antidote", "a blue liquid"], "a Blue Potion Bottle", 'item'),
    'Bottle with Fairy':                                        (["an imprisoned fairy", "an extra life", "Navi's cousin"], "a Fairy Bottle", 'item'),
    'Bottle with Fish':                                         (["an aquarium", "a deity's snack"], "a Fish Bottle", 'item'),
    'Bottle with Blue Fire':                                    (["a conflagration canteen", "an icemelt jar"], "a Blue Fire Bottle", 'item'),
    'Bottle with Bugs':                                         (["an insectarium", "Skulltula finders"], "a Bug Bottle", 'item'),
    'Bottle with Poe':                                          (["a spooky ghost", "a face in the jar"], "a Poe Bottle", 'item'),
    'Bottle with Big Poe':                                      (["the spookiest ghost", "a sidequest spirit"], "a Big Poe Bottle", 'item'),
    'Stone of Agony':                                           (["the shake stone", "the Rumble Pak (TM)"], "the Stone of Agony", 'item'),
    'Gerudo Membership Card':                                   (["a girl club membership", "a desert tribe's pass"], "the Gerudo Card", 'item'),
    'Progressive Wallet':                                       (["a mo' money holder", "a gem purse", "a portable bank"], "a Wallet", 'item'),
    'Deku Stick Capacity':                                      (["a lumber rack", "more flammable twigs"], "Deku Stick Capacity", 'item'),
    'Deku Nut Capacity':                                        (["more nuts", "flashbang storage"], "Deku Nut Capacity", 'item'),
    'Heart Container':                                          (["a lot of love", "a Valentine's gift", "a boss's organ"], "a Heart Container", 'item'),
    'Piece of Heart':                                           (["a little love", "a broken heart"], "a Piece of Heart", 'item'),
    'Piece of Heart (Treasure Chest Game)':                     ("a victory valentine", "a Piece of Heart", 'item'),
    'Recovery Heart':                                           (["a free heal", "a hearty meal", "a Band-Aid"], "a Recovery Heart", 'item'),
    'Rupee (Treasure Chest Game)':                              ("the dollar of defeat", 'a Green Rupee', 'item'),
    'Deku Stick (1)':                                           ("a breakable branch", 'a Deku Stick', 'item'),
    'Rupee (1)':                                                (["a unique coin", "a penny", "a green gem"], "a Green Rupee", 'item'),
    'Rupees (5)':                                               (["a common coin", "a blue gem"], "a Blue Rupee", 'item'),
    'Rupees (20)':                                              (["couch cash", "a red gem"], "a Red Rupee", 'item'),
    'Rupees (50)':                                              (["big bucks", "a purple gem", "wealth"], "a Purple Rupee", 'item'),
    'Rupees (200)':                                             (["a juicy jackpot", "a yellow gem", "a giant gem", "great wealth"], "a Huge Rupee", 'item'),
    'Weird Egg':                                                (["a chicken dilemma"], "the Weird Egg", 'item'),
    'Zeldas Letter':                                            (["an autograph", "royal stationery", "royal snail mail"], "Zelda's Letter", 'item'),
    'Pocket Egg':                                               (["a Cucco container", "a Cucco, eventually", "a fowl youth"], "the Pocket Egg", 'item'),
    'Pocket Cucco':                                             (["a little clucker"], "the Pocket Cucco", 'item'),
    'Cojiro':                                                   (["a cerulean capon"], "Cojiro", 'item'),
    'Odd Mushroom':                                             (["a powder ingredient"], "an Odd Mushroom", 'item'),
    'Odd Potion':                                               (["Granny's goodies"], "an Odd Potion", 'item'),
    'Poachers Saw':                                             (["a tree killer"], "the Poacher's Saw", 'item'),
    'Broken Sword':                                             (["a shattered slicer"], "the Broken Sword", 'item'),
    'Prescription':                                             (["a pill pamphlet", "a doctor's note"], "the Prescription", 'item'),
    'Eyeball Frog':                                             (["a perceiving polliwog"], "the Eyeball Frog", 'item'),
    'Eyedrops':                                                 (["a vision vial"], "the Eyedrops", 'item'),
    'Claim Check':                                              (["a three day wait"], "the Claim Check", 'item'),
    'Map':                                                      (["a dungeon atlas", "blueprints"], "a Map", 'item'),
    'Compass':                                                  (["a treasure tracker", "a magnetic needle"], "a Compass", 'item'),
    'BossKey':                                                  (["a master of unlocking", "a dungeon's master pass"], "a Boss Key", 'item'),
    'SmallKey':                                                 (["a tool for unlocking", "a dungeon pass", "a lock remover", "a lockpick"], "a Small Key", 'item'),
    'FortressSmallKey':                                         (["a get out of jail free card"], "a Jail Key", 'item'),
    'KeyError':                                                 (["something mysterious", "an unknown treasure"], "An Error (Please Report This)", 'item'),
    'Arrows (5)':                                               (["a few danger darts", "a few sharp shafts"], "Arrows (5 pieces)", 'item'),
    'Arrows (10)':                                              (["some danger darts", "some sharp shafts"], "Arrows (10 pieces)", 'item'),
    'Arrows (30)':                                              (["plenty of danger darts", "plenty of sharp shafts"], "Arrows (30 pieces)", 'item'),
    'Bombs (5)':                                                (["a few explosives", "a few blast balls"], "Bombs (5 pieces)", 'item'),
    'Bombs (10)':                                               (["some explosives", "some blast balls"], "Bombs (10 pieces)", 'item'),
    'Bombs (20)':                                               (["lots-o-explosives", "plenty of blast balls"], "Bombs (20 pieces)", 'item'),
    'Ice Trap':                                                 (["a gift from Ganon", "a chilling discovery", "frosty fun"], "an Ice Trap", 'item'),
    'Magic Bean':                                               (["wizardly legumes"], "a Magic Bean", 'item'),
    'Bombchus':                                                 (["mice bombs", "proximity mice", "wall crawlers", "trail blazers"], "Bombchus", 'item'),
    'Bombchus (5)':                                             (["a few mice bombs", "a few proximity mice", "a few wall crawlers", "a few trail blazers"], "Bombchus (5 pieces)", 'item'),
    'Bombchus (10)':                                            (["some mice bombs", "some proximity mice", "some wall crawlers", "some trail blazers"], "Bombchus (10 pieces)", 'item'),
    'Bombchus (20)':                                            (["plenty of mice bombs", "plenty of proximity mice", "plenty of wall crawlers", "plenty of trail blazers"], "Bombchus (20 pieces)", 'item'),
    'Deku Nuts (5)':                                            (["some nuts", "some flashbangs", "some scrub spit"], "Deku Nuts (5 pieces)", 'item'),
    'Deku Nuts (10)':                                           (["lots-o-nuts", "plenty of flashbangs", "plenty of scrub spit"], "Deku Nuts (10 pieces)", 'item'),
    'Deku Seeds (30)':                                          (["catapult ammo", "lots-o-seeds"], "Deku Seeds (30 pieces)", 'item'),
    'Gold Skulltula Token':                                     (["proof of destruction", "an arachnid chip", "spider remains", "one percent of a curse"], "a Gold Skulltula Token", 'item'),

    '10 Big Poes':                                              (["#Big Poes# leads to", "#ghost hunters# will be rewarded with"], None, 'always'),
    'Deku Theater Skull Mask':                                  ("the #Skull Mask# yields", None, 'always'),
    'Deku Theater Mask of Truth':                               ("the #Mask of Truth# yields", None, 'always'),
    '30 Gold Skulltula Reward':                                 ("slaying #30 Gold Skulltulas# reveals", None, 'always'),
    '40 Gold Skulltula Reward':                                 ("slaying #40 Gold Skulltulas# reveals", None, 'always'),
    '50 Gold Skulltula Reward':                                 ("slaying #50 Gold Skulltulas# reveals", None, 'always'),
    'Ocarina of Time':                                          ("the #treasure thrown by Princess Zelda# is", None, 'always'),
    'Song from Ocarina of Time':                                ("the #Ocarina of Time# teaches", None, 'always'),
    'Biggoron':                                                 ("#Biggoron# crafts", None, 'always'),
    'Frog Ocarina Game':                                        (["an #amphibian feast# yields", "the #croaking choir's magnum opus# awards", "the #froggy finale# yields"], "the final reward from the #Frogs of Zora's River# is", 'always'),

    'Song from Composer Grave':                                 (["in the #Composers' Grave#, ReDead guard", "the #Composer Brothers# wrote"], None, 'song'),
    'Sheik Forest Song':                                        ("deep in #the forest# Sheik teaches", None, 'song'),
    'Sheik at Temple':                                          ("Sheik waits at a #monument to time# to teach", None, 'song'),
    'Sheik in Crater':                                          ("the #crater's melody# is", None, 'song'),
    'Sheik in Ice Cavern':                                      ("the #frozen cavern# echoes with", None, 'song'),
    'Sheik in Kakariko':                                        ("a #ravaged village# mourns with", None, 'song'),
    'Sheik at Colossus':                                        ("a hero ventures beyond #the Wasteland# to learn", None, 'song'),

    'Child Fishing':                                            ("#fishing in youth# bestows", None, 'minigame'),
    'Adult Fishing':                                            ("#fishing in maturity# bestows", None, 'minigame'),
    'Child Shooting Gallery':                                   ("#shooting in youth# grants", None, 'minigame'),
    'Adult Shooting Gallery':                                   ("#shooting in maturity# grants", None, 'minigame'),
    'Bombchu Bowling Bomb Bag':                                 ("the #first explosive prize# is", None, 'minigame'),
    'Bombchu Bowling Piece of Heart':                           ("the #second explosive prize# is", None, 'minigame'),
    'Treasure Chest Game':                                      (["#gambling# grants", "there is a #1/32 chance# to win"], "the #treasure chest game# grants", 'minigame'),
    'Horseback Archery 1500 Points':                            ("mastery of #horseback archery# grants", "scoring 1500 in #horseback archery# grants", 'minigame'),

    '20 Gold Skulltula Reward':                                 ("slaying #20 Gold Skulltulas# reveals", None, 'overworld'),
    'Darunias Joy':                                             ("#Darunia's dance# leads to", None, 'overworld'),
    'Skull Kid':                                                ("the #Skull Kid# grants", None, 'overworld'),
    'Lake Hylia Sun':                                           ("staring into #the sun# grants", "shooting #the sun# grants", 'overworld'),
    'Heart Piece Grave Chest':                                  ("playing #Sun's Song# in a grave spawns", None, 'overworld'),
    'Goron City Leftmost Maze Chest':                           ("in #Goron City# the hammer unlocks", None, 'overworld'),
    'Gerudo Valley Hammer Rocks Chest':                         ("in #Gerudo Valley# the hammer unlocks", None, 'overworld'),
    'GS Hyrule Castle Grotto':                                  ("a #storm near the castle# reveals", None, 'overworld'),
    'GS Hyrule Field Near Gerudo Valley':                       ("buried near #the valley# a spider holds", None, 'overworld'),
    'GS Zora\'s Fountain Hidden Cave':                          ("a spider high above the #icy waters# holds", None, 'overworld'),
    'Haunted Wasteland Structure Chest':                        (["deep in the #Wasteland# is", "beneath #the sands#, flames reveal"], None, 'overworld'),
    'GS Wasteland Ruins':                                       ("a #spider in the Wasteland# hold", None, 'overworld'),
    'Composer Grave Chest':                                     (["in the #Composers' Grave#, darkness hides", "the #Composer Brothers# hid"], None, 'overworld'),
    'Zoras Fountain Bottom Freestanding PoH':                   ("under the #icy waters# lies", None, 'overworld'),
    'Goron City Pot Freestanding PoH':                          ("spinning #Goron pottery# contains", None, 'overworld'),
    'King Zora Thawed':                                         ("unfreezing #King Zora# grants", None, 'overworld'),
    'DMC Deku Scrub Bombs':                                     ("in the Crater a #scrub# sells", None, 'overworld'),

    'Deku Tree MQ After Spinning Log Chest':                    ("within #a tree#, a temporal stone contains", None, 'dungeon'),
    'GS Deku Tree MQ Basement Ceiling':                         ("within #a tree#, a spider on the ceiling holds", None, 'dungeon'),
    'GS Jabu Jabu MQ Invisible Enemies Room':                   ("in the #belly of a deity#, a spider surrounded by shadows holds", None, 'dungeon'),
    'Forest Temple Floormaster Chest':                          ("deep in #the forest#, shadows guard a chest containing", "a Floormaster in #Forest Temple# guards", 'dungeon'),
    'Fire Temple Scarecrow Chest':                              ("high in the #Fire Temple#, Pierre hid", None, 'dungeon'),
    'Fire Temple Megaton Hammer Chest':                         ("high in the #Fire Temple#, Flare Dancers hid", None, 'dungeon'),
    'Fire Temple MQ West Tower Top Chest':                      ("high in the #Fire Temple#, Flare Dancers hid", None, 'dungeon'),
    'GS Fire Temple MQ Above Fire Wall Maze':                   ("high in the #Fire Temple#, a spider holds", None, 'dungeon'),
    'Water Temple River Chest':                                 ("deep under #the lake#, beyond the currents, hides", "the #Water Temple River Chest# holds", 'dungeon'),
    'Water Temple Boss Key Chest':                              ("deep under #the lake#, the gilded chest contains", "the #Water Temple Gilded Chest# holds", 'dungeon'),
    'Water Temple MQ Boss Key Chest':                           ("deep under #the lake#, the gilded chest contains", "the #Water Temple Gilded Chest# holds", 'dungeon'),
    'Water Temple MQ Freestanding Key':                         ("deep under #the lake#, the apparent key is really", None, 'dungeon'),
    'GS Water Temple MQ North Basement':                        ("deep under #the lake#, the locked spider holds", None, 'dungeon'),
    'Gerudo Training Grounds Underwater Silver Rupee Chest':    ("those who seek #sunken silver rupees# will find", None, 'dungeon'),
    'Gerudo Training Grounds MQ Underwater Silver Rupee Chest': ("those who seek #sunken silver rupees# will find", None, 'dungeon'),
    'Gerudo Training Grounds Maze Path Final Chest':            ("the final prize of #the thieves\' training# is", None, 'dungeon'),
    'Gerudo Training Grounds MQ Ice Arrows Chest':              ("the final prize of #the thieves\' training# is", None, 'dungeon'),
    'Bottom of the Well Defeat Boss':                           ("#Dead Hand# holds", "#Dead Hand# in the well holds", 'dungeon'),
    'Bottom of the Well MQ Compass Chest':                      ("#Dead Hand# holds", "#Dead Hand# in the well holds", 'dungeon'),
    'Silver Gauntlets Chest':                                   ("upon the #Colossus's right hand# is", None, 'dungeon'),
    'Mirror Shield Chest':                                      ("upon the #Colossus's left hand# is", None, 'dungeon'),
    'Spirit Temple MQ Child Center Chest':                      ("within #the Colossus# a temporal paradox yields", None, 'dungeon'),
    'Spirit Temple MQ Lower Adult Right Chest':                 ("within #the Colossus# a symphony yields", None, 'dungeon'),
    'GS Spirit Temple MQ Lower Adult Right':                    ("within #the Colossus# a spider's symphony yields", None, 'dungeon'),
    'Shadow Temple Hidden Floormaster Chest':                   (["shadows in an #invisible maze# guard", "after a free #boat ride# comes"], None, 'dungeon'),
    'Shadow Temple MQ Bomb Flower Chest':                       (["shadows in an #invisible maze# guard", "after a free #boat ride# comes"], None, 'dungeon'),

    'House of Skulltula':                                       ("the #cursed family's house#", "the #House of Skulltulas#", 'region'),
    'Mido House':                                               ("the #chest hoarder's house#", "Mido's house", 'region'),
    'Lake Hylia Lab':                                           ("the lake scientist's #laboratory#", "the #Lakeside Laboratory#", 'region'),
    'Fishing Hole':                                             ("a #fishing spot#", "the #Fishing Pond#", 'region'),
    'Castle Town Mask Shop':                                    ("a #shop made to sell happiness#", "the #Happy Mask Shop#", 'region'),
    'Castle Town Rupee Room':                                   ("a place with #lots of pots#", "the #Guard House#", 'region'),
    'Kokiri Shop':                                              ("a #shop held by Kokiris#", "the #Kokiri Shop#", 'region'),
    'Deku Theater':                                             ("a #stage# full of Deku Scrubs", "the #Forest Stage#", 'region'),

    '1001':                                                     ("Ganondorf 2020!", None, 'junk'),
    '1002':                                                     ("They say that monarchy is a terrible system of governance.", None, 'junk'),
    '1003':                                                     ("They say that Zelda is a poor leader.", None, 'junk'),
    '1004':                                                     ("These hints can be quite useful. This is an exception.", None, 'junk'),
    '1006':                                                     ("They say that all the Zora drowned in Wind Waker.", None, 'junk'),
    '1007':                                                     ("They say that PJ64 is a terrible emulator.", None, 'junk'),
    '1008':                                                     ("'Member when Ganon was a blue pig?^I 'member.", None, 'junk'),
    '1009':                                                     ("One who does not have Triforce can't go in.", None, 'junk'),
    '1010':                                                     ("Save your future, end the Happy Mask Salesman.", None, 'junk'),
    '1012':                                                     ("I'm stoned. Get it?", None, 'junk'),
    '1013':                                                     ("Hoot! Hoot! Would you like me to repeat that?", None, 'junk'),
    '1014':                                                     ("Gorons are stupid. They eat rocks.", None, 'junk'),
    '1015':                                                     ("They say that Lon Lon Ranch prospered under Ingo.", None, 'junk'),
    '1016':                                                     ("The single rupee is a unique item.", None, 'junk'),
    '1017':                                                     ("Without the Lens of Truth, the Treasure Chest Mini-Game is a 1 out of 32 chance.^Good luck!", None, 'junk'),
    '1018':                                                     ("Use bombs wisely.", None, 'junk'),
    '1021':                                                     ("I found you, faker!", None, 'junk'),
    '1022':                                                     ("You're comparing yourself to me?^Ha! You're not even good enough to be my fake.", None, 'junk'),
    '1023':                                                     ("I'll make you eat those words.", None, 'junk'),
    '1024':                                                     ("What happened to Sheik?", None, 'junk'),
    '1025':                                                     ("L2P @.", None, 'junk'),
    '1026':                                                     ("I heard @ isn't very good at Zelda.", None, 'junk'),
    '1027':                                                     ("I'm Lonk from Pennsylvania.", None, 'junk'),
    '1028':                                                     ("I bet you'd like to have more bombs.", None, 'junk'),
    '1029':                                                     ("When all else fails, use Fire.", None, 'junk'),
    '1030':                                                     ("Here's a hint, @. Don't be bad.", None, 'junk'),
    '1031':                                                     ("Game Over. Return of Ganon.", None, 'junk'),
    '1032':                                                     ("May the way of the Hero lead to the Triforce.", None, 'junk'),
    '1033':                                                     ("Can't find an item? Scan an Amiibo.", None, 'junk'),
    '1034':                                                     ("They say this game has just a few glitches.", None, 'junk'),
    '1035':                                                     ("BRRING BRRING This is Ulrira. Wrong number?", None, 'junk'),
    '1036':                                                     ("Tingle Tingle Kooloo Limpah", None, 'junk'),
    '1037':                                                     ("L is real 2041", None, 'junk'),
    '1038':                                                     ("They say that Ganondorf will appear in the next Mario Tennis.", None, 'junk'),
    '1039':                                                     ("Medigoron sells the earliest Breath of the Wild demo.", None, 'junk'),
    '1040':                                                     ("There's a reason why I am special inquisitor!", None, 'junk'),
    '1041':                                                     ("You were almost a @ sandwich.", None, 'junk'),
    '1042':                                                     ("I'm a helpful hint Gossip Stone!^See, I'm helping.", None, 'junk'),
    '1043':                                                     ("Dear @, please come to the castle. I've baked a cake for you.&Yours truly, princess Zelda.", None, 'junk'),
    '1044':                                                     ("They say all toasters toast toast.", None, 'junk'),
    '1045':                                                     ("They say that Okami is the best Zelda game.", None, 'junk'),
    '1046':                                                     ("They say that quest guidance can be found at a talking rock.", None, 'junk'),
    '1047':                                                     ("They say that the final item you're looking for can be found somewhere in Hyrule.", None, 'junk'),
    '1048':                                                     ("Mweep.^Mweep.^Mweep.^Mweep.^Mweep.^Mweep.^Mweep.^Mweep.^Mweep.^Mweep.^Mweep.^Mweep.", None, 'junk'),
    '1049':                                                     ("They say that Barinade fears Deku Nuts.", None, 'junk'),
    '1050':                                                     ("They say that Flare Dancers do not fear Goron-crafted blades.", None, 'junk'),
    '1051':                                                     ("They say that Morpha is easily trapped in a corner.", None, 'junk'),
    '1052':                                                     ("They say that Bongo Bongo really hates the cold.", None, 'junk'),
    '1053':                                                     ("They say that crouch stabs mimic the effects of your last attack.", None, 'junk'),
    '1054':                                                     ("They say that bombing the hole Volvagia last flew into can be rewarding.", None, 'junk'),
    '1055':                                                     ("They say that invisible ghosts can be exposed with Deku Nuts.", None, 'junk'),
    '1056':                                                     ("They say that the real Phantom Ganon is bright and loud.", None, 'junk'),
    '1057':                                                     ("They say that walking backwards is very fast.", None, 'junk'),
    '1058':                                                     ("They say that leaping above the Castle Town entrance enriches most children.", None, 'junk'),

    'Deku Tree':                                                ("an ancient tree", "Deku Tree", 'dungeonName'),
    'Dodongos Cavern':                                          ("an immense cavern", "Dodongo's Cavern", 'dungeonName'),
    'Jabu Jabus Belly':                                         ("the belly of a deity", "Jabu Jabu's Belly", 'dungeonName'),
    'Forest Temple':                                            ("a deep forest", "Forest Temple", 'dungeonName'),
    'Fire Temple':                                              ("a high mountain", "Fire Temple", 'dungeonName'),
    'Water Temple':                                             ("a vast lake", "Water Temple", 'dungeonName'),
    'Shadow Temple':                                            ("the house of the dead", "Shadow Temple", 'dungeonName'),
    'Spirit Temple':                                            ("the goddess of the sand", "Spirit Temple", 'dungeonName'),
    'Ice Cavern':                                               ("a frozen maze", "Ice Cavern", 'dungeonName'),
    'Bottom of the Well':                                       ("a shadow\'s prison", "Bottom of the Well", 'dungeonName'),
    'Gerudo Training Grounds':                                  ("the test of thieves", "Gerudo Training Grounds", 'dungeonName'),
    'Ganons Castle':                                            ("a conquered citadel", "Ganon's Castle", 'dungeonName'),
    
    'Queen Gohma':                                              ("One inside an #ancient tree#...^", "One in the #Deku Tree#...^", 'boss'),
    'King Dodongo':                                             ("One within an #immense cavern#...^", "One in #Dodongo's Cavern#...^", 'boss'),
    'Barinade':                                                 ("One in the #belly of a deity#...^", "One in #Jabu Jabu's Belly#...^", 'boss'),
    'Phantom Ganon':                                            ("One in a #deep forest#...^", "One in the #Forest Temple#...^", 'boss'),
    'Volvagia':                                                 ("One on a #high mountain#...^", "One in the #Fire Temple#...^", 'boss'),
    'Morpha':                                                   ("One under a #vast lake#...^", "One in the #Water Temple#...^", 'boss'),
    'Bongo Bongo':                                              ("One within the #house of the dead#...^", "One in the #Shadow Temple#...^", 'boss'),
    'Twinrova':                                                 ("One inside a #goddess of the sand#...^", "One in the #Spirit Temple#...^", 'boss'),
    'Links Pocket':                                             ("One in #@'s pocket#...^", "One #@ already has#...^", 'boss'),
    'Spiritual Stone Text Start':                               ("Ye who owns 3 Spiritual Stones...^", None, 'boss'),
    'Spiritual Stone Text End':                                 ("\x13\x08Stand with the Ocarina of Time&and play the Song of Time.", None, 'boss'),
    'Medallion Text Start':                                     ("When evil rules all, an awakening&voice from the Sacred Realm will&call those destined to be Sages,&who dwell in the \x05\x41five temples\x05\x40.^", None, 'boss'),
    'Medallion Text End':                                       ("\x13\x12Together with the Hero of Time,&the awakened ones will bind&the evil and return the light&of peace to the world.", None, 'boss'),
    
    'Validation Line':                                          ("Hmph... Since you made it this far,&I'll let you know what glorious&prize of Ganon's you likely&missed out on in my tower.^Behold...^", None, 'validation line'),
    'Light Arrow Location':                                     ("Ha ha ha... You'll never beat me by&reflecting my lightning bolts&and unleashing the arrows from&", None, 'Light Arrow Location'),
    '2001':                                                     ("Oh! It's @.&I was expecting someone called&Sheik. Do you know what&happened to them?", None, 'ganonLine'),
    '2002':                                                     ("I knew I shouldn't have put the key&on the other side of my door.", None, 'ganonLine'),
    '2003':                                                     ("Looks like it's time for a&round of tennis.", None, 'ganonLine'),
    '2004':                                                     ("You'll never deflect my bolts of&energy with your sword,&then shoot me with those Light&Arrows you happen to have.", None, 'ganonLine'),
    '2005':                                                     ("Why did I leave my trident&back in the desert?", None, 'ganonLine'),
    '2006':                                                     ("Zelda is probably going to do&something stupid, like send you&back to your own timeline.^So this is quite meaningless.&Do you really want&to save this moron?", None, 'ganonLine'),
    '2007':                                                     ("What about Zelda makes you think&she'd be a better ruler than I?^I saved Lon Lon Ranch,&fed the hungry,&and my castle floats.", None, 'ganonLine'),
    '2008':                                                     ("I've learned this spell,&it's really neat,&I'll keep it later&for your treat!", None, 'ganonLine'),
    '2009':                                                     ("Many tricks are up my sleeve,&to save yourself&you'd better leave!", None, 'ganonLine'),
    '2010':                                                     ("After what you did to&Koholint Island, how can&you call me the bad guy?", None, 'ganonLine'),
    '2011':                                                     ("Today, let's begin down&'The Hero is Defeated' timeline.", None, 'ganonLine'),
}


# This specifies which hints will never appear due to either having known or known useless contents or due to the locations not existing.
def hintExclusions(world, clear_cache=False):
    if not clear_cache and hintExclusions.exclusions is not None:
        return hintExclusions.exclusions

    hintExclusions.exclusions = []
    hintExclusions.exclusions.extend(world.disabled_locations)

    for location in world.get_locations():
        if location.locked:
            hintExclusions.exclusions.append(location.name)

    world_location_names = [
        location.name for location in world.get_locations()]

    location_hints = []
    for name in hintTable:
        hint = getHint(name, world.clearer_hints)
        if hint.type in ['always',
                         'minigame',
                         'overworld',
                         'dungeon',
                         'song']:
            location_hints.append(hint)

    for hint in location_hints:
        if hint.name not in world_location_names:
            hintExclusions.exclusions.append(hint.name)

    return hintExclusions.exclusions


hintExclusions.exclusions = None
