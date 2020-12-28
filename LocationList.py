from collections import OrderedDict


def shop_address(shop_id, shelf_id):
    return 0xC71ED0 + (0x40 * shop_id) + (0x08 * shelf_id)

#   Abbreviations
#       DMC     Death Mountain Crater
#       DMT     Death Mountain Trail
#       GC      Goron City
#       GF      Gerudo Fortress
#       GS      Gold Skulltula
#       GV      Gerudo Valley
#       HC      Hyrule Castle
#       HF      Hyrule Field
#       KF      Kokiri Forest
#       LH      Lake Hylia
#       LLR     Lon Lon Ranch
#       LW      Lost Woods
#       OGC     Outside Ganon's Castle
#       SFM     Sacred Forest Meadow
#       ToT     Temple of Time
#       ZD      Zora's Domain
#       ZF      Zora's Fountain
#       ZR      Zora's River

# The order of this table is reflected in the spoiler's list of locations (except Hints aren't included).
# Within a section, the order of types is: gifts/freestanding/chests, Deku Scrubs, Cows, Gold Skulltulas, Shops.

# NPC Scrubs are on the overworld, while GrottoNPC / GrottoNPCOnce is a special handler for Grottos
# Grottos scrubs are the same scene and actor, so we use a unique grotto ID for the scene
# Remove the "2" from RepeatNPC2 and GrottoNPC2 when scrubs and cows can be repeatable
# Remove the "Once" from GrottoNPCOnce and change 'LW Deku Scrub Near Bridge' to RepeatNPC when upgrade deku scrubs can be repeatable

# Note that the scene for skulltulas is not the actual scene the token appears in
# Rather, it is the index of the grouping used when storing skulltula collection
# For example, zora river, zora's domain, and zora fountain are all a single 'scene' for skulltulas

#   Location:                                           Type          Scene Default Addresses                 Categories
location_table = OrderedDict([
    ## Dungeon Rewards
    ("Links Pocket",                                    ("Boss",        None,  None, None,                     None)),
    ("Queen Gohma",                                     ("Boss",        None,  0x6C, (0x0CA315F, 0x2079571),   None)),
    ("King Dodongo",                                    ("Boss",        None,  0x6D, (0x0CA30DF, 0x2223309),   None)),
    ("Barinade",                                        ("Boss",        None,  0x6E, (0x0CA36EB, 0x2113C19),   None)),
    ("Phantom Ganon",                                   ("Boss",        None,  0x66, (0x0CA3D07, 0x0D4ED79),   None)),
    ("Volvagia",                                        ("Boss",        None,  0x67, (0x0CA3D93, 0x0D10135),   None)),
    ("Morpha",                                          ("Boss",        None,  0x68, (0x0CA3E1F, 0x0D5A3A9),   None)),
    ("Bongo Bongo",                                     ("Boss",        None,  0x6A, (0x0CA3F43, 0x0D13E19),   None)),
    ("Twinrova",                                        ("Boss",        None,  0x69, (0x0CA3EB3, 0x0D39FF1),   None)),
    ("Ganon",                                           ("Event",       None,  None, None,                     None)),

    ## Songs
    ("Song from Impa",                                  ("Song",        0xFF,  0x26, (0x2E8E925, 0x2E8E925),   ("Hyrule Castle", "Market", "Songs"))),
    ("Song from Malon",                                 ("Song",        0xFF,  0x27, (0x0D7EB53, 0x0D7EBCF),   ("Lon Lon Ranch", "Songs",))),
    ("Song from Saria",                                 ("Song",        0xFF,  0x28, (0x20B1DB1, 0x20B1DB1),   ("Sacred Forest Meadow", "Forest", "Songs"))),
    ("Song from Composers Grave",                       ("Song",        0xFF,  0x29, (0x332A871, 0x332A871),   ("the Graveyard", "Kakariko", "Songs"))),
    ("Song from Ocarina of Time",                       ("Song",        0xFF,  0x2A, (0x252FC89, 0x252FC89),   ("Hyrule Field", "Songs", "Need Spiritual Stones"))),
    ("Song from Windmill",                              ("Song",        0xFF,  0x2B, (0x0E42C07, 0x0E42B8B),   ("Kakariko Village", "Kakariko", "Songs"))),
    ("Sheik in Forest",                                 ("Song",        0xFF,  0x20, (0x20B0809, 0x20B0809),   ("Sacred Forest Meadow", "Forest", "Songs"))),
    ("Sheik in Crater",                                 ("Song",        0xFF,  0x21, (0x224D7F1, 0x224D7F1),   ("Death Mountain Crater", "Death Mountain", "Songs"))),
    ("Sheik in Ice Cavern",                             ("Song",        0xFF,  0x22, (0x2BEC889, 0x2BEC889),   ("Ice Cavern", "Songs",))),
    ("Sheik at Colossus",                               ("Song",        0xFF,  0x23, (0x218C57D, 0x218C57D),   ("Desert Colossus", "Songs",))),
    ("Sheik in Kakariko",                               ("Song",        0xFF,  0x24, (0x2000FE1, 0x2000FE1),   ("Kakariko Village", "Kakariko", "Songs"))),
    ("Sheik at Temple",                                 ("Song",        0xFF,  0x25, (0x2531329, 0x2531329),   ("Temple of Time", "Market", "Songs"))),

    ## Overworld
    # Kokiri Forest
    ("KF Midos Top Left Chest",                         ("Chest",       0x28,  0x00, None,                     ("Kokiri Forest", "Forest",))),
    ("KF Midos Top Right Chest",                        ("Chest",       0x28,  0x01, None,                     ("Kokiri Forest", "Forest",))),
    ("KF Midos Bottom Left Chest",                      ("Chest",       0x28,  0x02, None,                     ("Kokiri Forest", "Forest",))),
    ("KF Midos Bottom Right Chest",                     ("Chest",       0x28,  0x03, None,                     ("Kokiri Forest", "Forest",))),
    ("KF Kokiri Sword Chest",                           ("Chest",       0x55,  0x00, None,                     ("Kokiri Forest", "Forest",))),
    ("KF Storms Grotto Chest",                          ("Chest",       0x3E,  0x0C, None,                     ("Kokiri Forest", "Forest", "Grottos"))),
    ("KF Links House Cow",                              ("RepeatNPC2",  0x34,  0x15, None,                     ("KF Links House", "Forest", "Cow", "Minigames"))),
    ("KF GS Know It All House",                         ("GS Token",    0x0C,  0x02, None,                     ("Kokiri Forest", "Skulltulas",))),
    ("KF GS Bean Patch",                                ("GS Token",    0x0C,  0x01, None,                     ("Kokiri Forest", "Skulltulas",))),
    ("KF GS House of Twins",                            ("GS Token",    0x0C,  0x04, None,                     ("Kokiri Forest", "Skulltulas",))),
    ("KF Shop Item 1",                                  ("Shop",        0x2D,  0x30, (shop_address(0, 0), None), ("Kokiri Forest", "Forest", "Shops"))),
    ("KF Shop Item 2",                                  ("Shop",        0x2D,  0x31, (shop_address(0, 1), None), ("Kokiri Forest", "Forest", "Shops"))),
    ("KF Shop Item 3",                                  ("Shop",        0x2D,  0x32, (shop_address(0, 2), None), ("Kokiri Forest", "Forest", "Shops"))),
    ("KF Shop Item 4",                                  ("Shop",        0x2D,  0x33, (shop_address(0, 3), None), ("Kokiri Forest", "Forest", "Shops"))),
    ("KF Shop Item 5",                                  ("Shop",        0x2D,  0x34, (shop_address(0, 4), None), ("Kokiri Forest", "Forest", "Shops"))),
    ("KF Shop Item 6",                                  ("Shop",        0x2D,  0x35, (shop_address(0, 5), None), ("Kokiri Forest", "Forest", "Shops"))),
    ("KF Shop Item 7",                                  ("Shop",        0x2D,  0x36, (shop_address(0, 6), None), ("Kokiri Forest", "Forest", "Shops"))),
    ("KF Shop Item 8",                                  ("Shop",        0x2D,  0x37, (shop_address(0, 7), None), ("Kokiri Forest", "Forest", "Shops"))),

    # Lost Woods
    ("LW Gift from Saria",                              ("Cutscene",    0xFF,  0x02, None,                     ("the Lost Woods", "Forest",))),
    ("LW Ocarina Memory Game",                          ("NPC",         0x5B,  0x76, None,                     ("the Lost Woods", "Forest", "Minigames"))),
    ("LW Target in Woods",                              ("NPC",         0x5B,  0x60, None,                     ("the Lost Woods", "Forest",))),
    ("LW Near Shortcuts Grotto Chest",                  ("Chest",       0x3E,  0x14, None,                     ("the Lost Woods", "Forest", "Grottos"))),
    ("Deku Theater Skull Mask",                         ("NPC",         0x3E,  0x77, None,                     ("the Lost Woods", "Forest", "Grottos"))),
    ("Deku Theater Mask of Truth",                      ("NPC",         0x3E,  0x7A, None,                     ("the Lost Woods", "Forest", "Need Spiritual Stones", "Grottos"))),
    ("LW Skull Kid",                                    ("NPC",         0x5B,  0x3E, None,                     ("the Lost Woods", "Forest",))),
    ("LW Deku Scrub Near Bridge",                       ("NPC",         0x5B,  0x77, None,                     ("the Lost Woods", "Forest", "Deku Scrub", "Deku Scrub Upgrades"))),
    ("LW Deku Scrub Near Deku Theater Left",            ("RepeatNPC2",  0x5B,  0x31, None,                     ("the Lost Woods", "Forest", "Deku Scrub"))),
    ("LW Deku Scrub Near Deku Theater Right",           ("RepeatNPC2",  0x5B,  0x30, None,                     ("the Lost Woods", "Forest", "Deku Scrub"))),
    ("LW Deku Scrub Grotto Front",                      ("GrottoNPCOnce",0xF5, 0x79, None,                     ("the Lost Woods", "Forest", "Deku Scrub", "Deku Scrub Upgrades", "Grottos"))),
    ("LW Deku Scrub Grotto Rear",                       ("GrottoNPC2",  0xF5,  0x33, None,                     ("the Lost Woods", "Forest", "Deku Scrub", "Grottos"))),
    ("LW GS Bean Patch Near Bridge",                    ("GS Token",    0x0D,  0x01, None,                     ("the Lost Woods", "Skulltulas",))),
    ("LW GS Bean Patch Near Theater",                   ("GS Token",    0x0D,  0x02, None,                     ("the Lost Woods", "Skulltulas",))),
    ("LW GS Above Theater",                             ("GS Token",    0x0D,  0x04, None,                     ("the Lost Woods", "Skulltulas",))),

    # Sacred Forest Meadow
    ("SFM Wolfos Grotto Chest",                         ("Chest",       0x3E,  0x11, None,                     ("Sacred Forest Meadow", "Forest", "Grottos"))),
    ("SFM Deku Scrub Grotto Front",                     ("GrottoNPC2",  0xEE,  0x3A, None,                     ("Sacred Forest Meadow", "Forest", "Deku Scrub", "Grottos"))),
    ("SFM Deku Scrub Grotto Rear",                      ("GrottoNPC2",  0xEE,  0x39, None,                     ("Sacred Forest Meadow", "Forest", "Deku Scrub", "Grottos"))),

    ("SFM GS",                                          ("GS Token",    0x0D,  0x08, None,                     ("Sacred Forest Meadow", "Skulltulas",))),

    # Hyrule Field
    ("HF Ocarina of Time Item",                         ("NPC",         0x51,  0x0C, None,                     ("Hyrule Field", "Need Spiritual Stones",))),
    ("HF Near Market Grotto Chest",                     ("Chest",       0x3E,  0x00, None,                     ("Hyrule Field", "Grottos",))),
    ("HF Tektite Grotto Freestanding PoH",              ("Collectable", 0x3E,  0x01, None,                     ("Hyrule Field", "Grottos",))),
    ("HF Southeast Grotto Chest",                       ("Chest",       0x3E,  0x02, None,                     ("Hyrule Field", "Grottos",))),
    ("HF Open Grotto Chest",                            ("Chest",       0x3E,  0x03, None,                     ("Hyrule Field", "Grottos",))),
    ("HF Deku Scrub Grotto",                            ("GrottoNPCOnce",0xE6, 0x3E, None,                     ("Hyrule Field", "Deku Scrub", "Deku Scrub Upgrades", "Grottos"))),
    ("HF Cow Grotto Cow",                               ("RepeatNPC2",  0x3E,  0x16, None,                     ("Hyrule Field", "Cow", "Grottos"))),
    ("HF GS Cow Grotto",                                ("GS Token",    0x0A,  0x01, None,                     ("Hyrule Field", "Skulltulas", "Grottos"))),
    ("HF GS Near Kak Grotto",                           ("GS Token",    0x0A,  0x02, None,                     ("Hyrule Field", "Skulltulas", "Grottos"))),

    # Market
    ("Market Shooting Gallery Reward",                  ("NPC",         0x42,  0x60, None,                     ("the Market", "Market", "Minigames"))),
    ("Market Bombchu Bowling First Prize",              ("NPC",         0x4B,  0x34, None,                     ("the Market", "Market", "Minigames"))),
    ("Market Bombchu Bowling Second Prize",             ("NPC",         0x4B,  0x3E, None,                     ("the Market", "Market", "Minigames"))),
    ("Market Bombchu Bowling Bombchus",                 ("NPC",         0x4B,  None, None,                     ("the Market", "Market", "Minigames"))),
    ("Market Lost Dog",                                 ("NPC",         0x35,  0x3E, None,                     ("the Market", "Market",))),
    ("Market Treasure Chest Game Reward",               ("Chest",       0x10,  0x0A, None,                     ("the Market", "Market", "Minigames"))),
    ("Market 10 Big Poes",                              ("NPC",         0x4D,  0x0F, None,                     ("the Market", "Hyrule Castle",))),
    ("Market GS Guard House",                           ("GS Token",    0x0E,  0x08, None,                     ("the Market", "Skulltulas",))),
    ("Market Bazaar Item 1",                            ("Shop",        0x2C,  0x30, (shop_address(4, 0), None), ("the Market", "Market", "Shops"))),
    ("Market Bazaar Item 2",                            ("Shop",        0x2C,  0x31, (shop_address(4, 1), None), ("the Market", "Market", "Shops"))),
    ("Market Bazaar Item 3",                            ("Shop",        0x2C,  0x32, (shop_address(4, 2), None), ("the Market", "Market", "Shops"))),
    ("Market Bazaar Item 4",                            ("Shop",        0x2C,  0x33, (shop_address(4, 3), None), ("the Market", "Market", "Shops"))),
    ("Market Bazaar Item 5",                            ("Shop",        0x2C,  0x34, (shop_address(4, 4), None), ("the Market", "Market", "Shops"))),
    ("Market Bazaar Item 6",                            ("Shop",        0x2C,  0x35, (shop_address(4, 5), None), ("the Market", "Market", "Shops"))),
    ("Market Bazaar Item 7",                            ("Shop",        0x2C,  0x36, (shop_address(4, 6), None), ("the Market", "Market", "Shops"))),
    ("Market Bazaar Item 8",                            ("Shop",        0x2C,  0x37, (shop_address(4, 7), None), ("the Market", "Market", "Shops"))),

    ("Market Potion Shop Item 1",                       ("Shop",        0x31,  0x30, (shop_address(3, 0), None), ("the Market", "Market", "Shops"))),
    ("Market Potion Shop Item 2",                       ("Shop",        0x31,  0x31, (shop_address(3, 1), None), ("the Market", "Market", "Shops"))),
    ("Market Potion Shop Item 3",                       ("Shop",        0x31,  0x32, (shop_address(3, 2), None), ("the Market", "Market", "Shops"))),
    ("Market Potion Shop Item 4",                       ("Shop",        0x31,  0x33, (shop_address(3, 3), None), ("the Market", "Market", "Shops"))),
    ("Market Potion Shop Item 5",                       ("Shop",        0x31,  0x34, (shop_address(3, 4), None), ("the Market", "Market", "Shops"))),
    ("Market Potion Shop Item 6",                       ("Shop",        0x31,  0x35, (shop_address(3, 5), None), ("the Market", "Market", "Shops"))),
    ("Market Potion Shop Item 7",                       ("Shop",        0x31,  0x36, (shop_address(3, 6), None), ("the Market", "Market", "Shops"))),
    ("Market Potion Shop Item 8",                       ("Shop",        0x31,  0x37, (shop_address(3, 7), None), ("the Market", "Market", "Shops"))),

    ("Market Bombchu Shop Item 1",                      ("Shop",        0x32,  0x30, (shop_address(2, 0), None), ("the Market", "Market", "Shops"))),
    ("Market Bombchu Shop Item 2",                      ("Shop",        0x32,  0x31, (shop_address(2, 1), None), ("the Market", "Market", "Shops"))),
    ("Market Bombchu Shop Item 3",                      ("Shop",        0x32,  0x32, (shop_address(2, 2), None), ("the Market", "Market", "Shops"))),
    ("Market Bombchu Shop Item 4",                      ("Shop",        0x32,  0x33, (shop_address(2, 3), None), ("the Market", "Market", "Shops"))),
    ("Market Bombchu Shop Item 5",                      ("Shop",        0x32,  0x34, (shop_address(2, 4), None), ("the Market", "Market", "Shops"))),
    ("Market Bombchu Shop Item 6",                      ("Shop",        0x32,  0x35, (shop_address(2, 5), None), ("the Market", "Market", "Shops"))),
    ("Market Bombchu Shop Item 7",                      ("Shop",        0x32,  0x36, (shop_address(2, 6), None), ("the Market", "Market", "Shops"))),
    ("Market Bombchu Shop Item 8",                      ("Shop",        0x32,  0x37, (shop_address(2, 7), None), ("the Market", "Market", "Shops"))),

    ("ToT Light Arrows Cutscene",                       ("Cutscene",    0xFF,  0x01, None,                     ("Temple of Time", "Market",))),

    # Hyrule Castle
    ("HC Malon Egg",                                    ("NPC",         0x5F,  0x47, None,                     ("Hyrule Castle", "Market",))),
    ("HC Zeldas Letter",                                ("NPC",         0x4A,  0x0B, None,                     ("Hyrule Castle", "Market",))),
    ("HC Great Fairy Reward",                           ("Cutscene",    0xFF,  0x11, None,                     ("Hyrule Castle", "Market", "Fairies"))),
    ("HC GS Tree",                                      ("GS Token",    0x0E,  0x04, None,                     ("Hyrule Castle", "Skulltulas",))),
    ("HC GS Storms Grotto",                             ("GS Token",    0x0E,  0x02, None,                     ("Hyrule Castle", "Skulltulas", "Grottos"))),

    # Lon Lon Ranch
    ("LLR Talons Chickens",                             ("NPC",         0x4C,  0x14, None,                     ("Lon Lon Ranch", "Kakariko", "Minigames"))),
    ("LLR Freestanding PoH",                            ("Collectable", 0x4C,  0x01, None,                     ("Lon Lon Ranch",))),
    ("LLR Deku Scrub Grotto Left",                      ("GrottoNPC2",  0xFC,  0x30, None,                     ("Lon Lon Ranch", "Deku Scrub", "Grottos"))),
    ("LLR Deku Scrub Grotto Center",                    ("GrottoNPC2",  0xFC,  0x33, None,                     ("Lon Lon Ranch", "Deku Scrub", "Grottos"))),
    ("LLR Deku Scrub Grotto Right",                     ("GrottoNPC2",  0xFC,  0x37, None,                     ("Lon Lon Ranch", "Deku Scrub", "Grottos"))),
    ("LLR Stables Left Cow",                            ("RepeatNPC2",  0x36,  0x15, None,                     ("Lon Lon Ranch", "Cow",))),
    ("LLR Stables Right Cow",                           ("RepeatNPC2",  0x36,  0x16, None,                     ("Lon Lon Ranch", "Cow",))),
    ("LLR Tower Left Cow",                              ("RepeatNPC2",  0x4C,  0x16, None,                     ("Lon Lon Ranch", "Cow",))),
    ("LLR Tower Right Cow",                             ("RepeatNPC2",  0x4C,  0x15, None,                     ("Lon Lon Ranch", "Cow",))),
    ("LLR GS House Window",                             ("GS Token",    0x0B,  0x04, None,                     ("Lon Lon Ranch", "Skulltulas",))),
    ("LLR GS Tree",                                     ("GS Token",    0x0B,  0x08, None,                     ("Lon Lon Ranch", "Skulltulas",))),
    ("LLR GS Rain Shed",                                ("GS Token",    0x0B,  0x02, None,                     ("Lon Lon Ranch", "Skulltulas",))),
    ("LLR GS Back Wall",                                ("GS Token",    0x0B,  0x01, None,                     ("Lon Lon Ranch", "Skulltulas",))),

    # Kakariko
    ("Kak Anju as Child",                               ("NPC",         0x52,  0x0F, None,                     ("Kakariko Village", "Kakariko", "Minigames"))),
    ("Kak Anju as Adult",                               ("NPC",         0x52,  0x1D, None,                     ("Kakariko Village", "Kakariko",))),
    ("Kak Impas House Freestanding PoH",                ("Collectable", 0x37,  0x01, None,                     ("Kakariko Village", "Kakariko",))),
    ("Kak Windmill Freestanding PoH",                   ("Collectable", 0x48,  0x01, None,                     ("Kakariko Village", "Kakariko",))),
    ("Kak Man on Roof",                                 ("NPC",         0x52,  0x3E, None,                     ("Kakariko Village", "Kakariko",))),
    ("Kak Open Grotto Chest",                           ("Chest",       0x3E,  0x08, None,                     ("Kakariko Village", "Kakariko", "Grottos"))),
    ("Kak Redead Grotto Chest",                         ("Chest",       0x3E,  0x0A, None,                     ("Kakariko Village", "Kakariko", "Grottos"))),
    ("Kak Shooting Gallery Reward",                     ("NPC",         0x42,  0x30, None,                     ("Kakariko Village", "Kakariko", "Minigames"))),
    ("Kak 10 Gold Skulltula Reward",                    ("NPC",         0x50,  0x45, None,                     ("Kakariko Village", "Kakariko", "Skulltula House"))),
    ("Kak 20 Gold Skulltula Reward",                    ("NPC",         0x50,  0x39, None,                     ("Kakariko Village", "Kakariko", "Skulltula House"))),
    ("Kak 30 Gold Skulltula Reward",                    ("NPC",         0x50,  0x46, None,                     ("Kakariko Village", "Kakariko", "Skulltula House"))),
    ("Kak 40 Gold Skulltula Reward",                    ("NPC",         0x50,  0x03, None,                     ("Kakariko Village", "Kakariko", "Skulltula House"))),
    ("Kak 50 Gold Skulltula Reward",                    ("NPC",         0x50,  0x3E, None,                     ("Kakariko Village", "Kakariko", "Skulltula House"))),
    ("Kak Impas House Cow",                             ("RepeatNPC2",  0x37,  0x15, None,                     ("Kakariko Village", "Kakariko", "Cow"))),
    ("Kak GS Tree",                                     ("GS Token",    0x10,  0x20, None,                     ("Kakariko Village", "Skulltulas",))),
    ("Kak GS Guards House",                             ("GS Token",    0x10,  0x02, None,                     ("Kakariko Village", "Skulltulas",))),
    ("Kak GS Watchtower",                               ("GS Token",    0x10,  0x04, None,                     ("Kakariko Village", "Skulltulas",))),
    ("Kak GS Skulltula House",                          ("GS Token",    0x10,  0x10, None,                     ("Kakariko Village", "Skulltulas",))),
    ("Kak GS House Under Construction",                 ("GS Token",    0x10,  0x08, None,                     ("Kakariko Village", "Skulltulas",))),
    ("Kak GS Above Impas House",                        ("GS Token",    0x10,  0x40, None,                     ("Kakariko Village", "Skulltulas",))),
    ("Kak Bazaar Item 1",                               ("Shop",        0x2C,  0x38, (shop_address(5, 0), None), ("Kakariko Village", "Kakariko", "Shops"))),
    ("Kak Bazaar Item 2",                               ("Shop",        0x2C,  0x39, (shop_address(5, 1), None), ("Kakariko Village", "Kakariko", "Shops"))),
    ("Kak Bazaar Item 3",                               ("Shop",        0x2C,  0x3A, (shop_address(5, 2), None), ("Kakariko Village", "Kakariko", "Shops"))),
    ("Kak Bazaar Item 4",                               ("Shop",        0x2C,  0x3B, (shop_address(5, 3), None), ("Kakariko Village", "Kakariko", "Shops"))),
    ("Kak Bazaar Item 5",                               ("Shop",        0x2C,  0x3D, (shop_address(5, 4), None), ("Kakariko Village", "Kakariko", "Shops"))),
    ("Kak Bazaar Item 6",                               ("Shop",        0x2C,  0x3E, (shop_address(5, 5), None), ("Kakariko Village", "Kakariko", "Shops"))),
    ("Kak Bazaar Item 7",                               ("Shop",        0x2C,  0x3F, (shop_address(5, 6), None), ("Kakariko Village", "Kakariko", "Shops"))),
    ("Kak Bazaar Item 8",                               ("Shop",        0x2C,  0x40, (shop_address(5, 7), None), ("Kakariko Village", "Kakariko", "Shops"))),
    ("Kak Potion Shop Item 1",                          ("Shop",        0x30,  0x30, (shop_address(1, 0), None), ("Kakariko Village", "Kakariko", "Shops"))),
    ("Kak Potion Shop Item 2",                          ("Shop",        0x30,  0x31, (shop_address(1, 1), None), ("Kakariko Village", "Kakariko", "Shops"))),
    ("Kak Potion Shop Item 3",                          ("Shop",        0x30,  0x32, (shop_address(1, 2), None), ("Kakariko Village", "Kakariko", "Shops"))),
    ("Kak Potion Shop Item 4",                          ("Shop",        0x30,  0x33, (shop_address(1, 3), None), ("Kakariko Village", "Kakariko", "Shops"))),
    ("Kak Potion Shop Item 5",                          ("Shop",        0x30,  0x34, (shop_address(1, 4), None), ("Kakariko Village", "Kakariko", "Shops"))),
    ("Kak Potion Shop Item 6",                          ("Shop",        0x30,  0x35, (shop_address(1, 5), None), ("Kakariko Village", "Kakariko", "Shops"))),
    ("Kak Potion Shop Item 7",                          ("Shop",        0x30,  0x36, (shop_address(1, 6), None), ("Kakariko Village", "Kakariko", "Shops"))),
    ("Kak Potion Shop Item 8",                          ("Shop",        0x30,  0x37, (shop_address(1, 7), None), ("Kakariko Village", "Kakariko", "Shops"))),

    # Graveyard
    ("Graveyard Shield Grave Chest",                    ("Chest",       0x40,  0x00, None,                     ("the Graveyard", "Kakariko",))),
    ("Graveyard Heart Piece Grave Chest",               ("Chest",       0x3F,  0x00, None,                     ("the Graveyard", "Kakariko",))),
    ("Graveyard Composers Grave Chest",                 ("Chest",       0x41,  0x00, None,                     ("the Graveyard", "Kakariko",))),
    ("Graveyard Freestanding PoH",                      ("Collectable", 0x53,  0x04, None,                     ("the Graveyard", "Kakariko",))),
    ("Graveyard Dampe Gravedigging Tour",               ("Collectable", 0x53,  0x08, None,                     ("the Graveyard", "Kakariko",))),
    ("Graveyard Hookshot Chest",                        ("Chest",       0x48,  0x00, None,                     ("the Graveyard", "Kakariko",))),
    ("Graveyard Dampe Race Freestanding PoH",           ("Collectable", 0x48,  0x07, None,                     ("the Graveyard", "Kakariko", "Minigames"))),
    ("Graveyard GS Bean Patch",                         ("GS Token",    0x10,  0x01, None,                     ("the Graveyard", "Skulltulas",))),
    ("Graveyard GS Wall",                               ("GS Token",    0x10,  0x80, None,                     ("the Graveyard", "Skulltulas",))),

    # Death Mountain Trail
    ("DMT Freestanding PoH",                            ("Collectable", 0x60,  0x1E, None,                     ("Death Mountain Trail", "Death Mountain",))),
    ("DMT Chest",                                       ("Chest",       0x60,  0x01, None,                     ("Death Mountain Trail", "Death Mountain",))),
    ("DMT Storms Grotto Chest",                         ("Chest",       0x3E,  0x17, None,                     ("Death Mountain Trail", "Death Mountain", "Grottos"))),
    ("DMT Great Fairy Reward",                          ("Cutscene",    0xFF,  0x13, None,                     ("Death Mountain Trail", "Death Mountain", "Fairies"))),
    ("DMT Biggoron",                                    ("NPC",         0x60,  0x57, None,                     ("Death Mountain Trail", "Death Mountain",))),
    ("DMT Cow Grotto Cow",                              ("RepeatNPC2",  0x3E,  0x15, None,                     ("Death Mountain Trail", "Death Mountain", "Cow", "Grottos"))),
    ("DMT GS Near Kak",                                 ("GS Token",    0x0F,  0x04, None,                     ("Death Mountain Trail", "Skulltulas",))),
    ("DMT GS Bean Patch",                               ("GS Token",    0x0F,  0x02, None,                     ("Death Mountain Trail", "Skulltulas",))),
    ("DMT GS Above Dodongos Cavern",                    ("GS Token",    0x0F,  0x08, None,                     ("Death Mountain Trail", "Skulltulas",))),
    ("DMT GS Falling Rocks Path",                       ("GS Token",    0x0F,  0x10, None,                     ("Death Mountain Trail", "Skulltulas",))),

    # Goron City
    ("GC Darunias Joy",                                 ("NPC",         0x62,  0x54, None,                     ("Goron City",))),
    ("GC Pot Freestanding PoH",                         ("Collectable", 0x62,  0x1F, None,                     ("Goron City", "Goron City",))),
    ("GC Rolling Goron as Child",                       ("NPC",         0x62,  0x34, None,                     ("Goron City",))),
    ("GC Rolling Goron as Adult",                       ("NPC",         0x62,  0x2C, None,                     ("Goron City",))),
    ("GC Medigoron",                                    ("RepeatNPC",   0x62,  0x28, None,                     ("Goron City",))),
    ("GC Maze Left Chest",                              ("Chest",       0x62,  0x00, None,                     ("Goron City",))),
    ("GC Maze Right Chest",                             ("Chest",       0x62,  0x01, None,                     ("Goron City",))),
    ("GC Maze Center Chest",                            ("Chest",       0x62,  0x02, None,                     ("Goron City",))),
    ("GC Deku Scrub Grotto Left",                       ("GrottoNPC2",  0xFB,  0x30, None,                     ("Goron City", "Deku Scrub", "Grottos"))),
    ("GC Deku Scrub Grotto Center",                     ("GrottoNPC2",  0xFB,  0x33, None,                     ("Goron City", "Deku Scrub", "Grottos"))),
    ("GC Deku Scrub Grotto Right",                      ("GrottoNPC2",  0xFB,  0x37, None,                     ("Goron City", "Deku Scrub", "Grottos"))),
    ("GC GS Center Platform",                           ("GS Token",    0x0F,  0x20, None,                     ("Goron City", "Skulltulas",))),
    ("GC GS Boulder Maze",                              ("GS Token",    0x0F,  0x40, None,                     ("Goron City", "Skulltulas",))),
    ("GC Shop Item 1",                                  ("Shop",        0x2E,  0x30, (shop_address(8, 0), None), ("Goron City", "Shops",))),
    ("GC Shop Item 2",                                  ("Shop",        0x2E,  0x31, (shop_address(8, 1), None), ("Goron City", "Shops",))),
    ("GC Shop Item 3",                                  ("Shop",        0x2E,  0x32, (shop_address(8, 2), None), ("Goron City", "Shops",))),
    ("GC Shop Item 4",                                  ("Shop",        0x2E,  0x33, (shop_address(8, 3), None), ("Goron City", "Shops",))),
    ("GC Shop Item 5",                                  ("Shop",        0x2E,  0x34, (shop_address(8, 4), None), ("Goron City", "Shops",))),
    ("GC Shop Item 6",                                  ("Shop",        0x2E,  0x35, (shop_address(8, 5), None), ("Goron City", "Shops",))),
    ("GC Shop Item 7",                                  ("Shop",        0x2E,  0x36, (shop_address(8, 6), None), ("Goron City", "Shops",))),
    ("GC Shop Item 8",                                  ("Shop",        0x2E,  0x37, (shop_address(8, 7), None), ("Goron City", "Shops",))),
    
    # Death Mountain Crater
    ("DMC Volcano Freestanding PoH",                    ("Collectable", 0x61,  0x08, None,                     ("Death Mountain Crater", "Death Mountain",))),
    ("DMC Wall Freestanding PoH",                       ("Collectable", 0x61,  0x02, None,                     ("Death Mountain Crater", "Death Mountain",))),
    ("DMC Upper Grotto Chest",                          ("Chest",       0x3E,  0x1A, None,                     ("Death Mountain Crater", "Death Mountain", "Grottos"))),
    ("DMC Great Fairy Reward",                          ("Cutscene",    0xFF,  0x14, None,                     ("Death Mountain Crater", "Death Mountain", "Fairies",))),
    ("DMC Deku Scrub",                                  ("RepeatNPC2",  0x61,  0x37, None,                     ("Death Mountain Crater", "Death Mountain", "Deku Scrub"))),
    ("DMC Deku Scrub Grotto Left",                      ("GrottoNPC2",  0xF9,  0x30, None,                     ("Death Mountain Crater", "Death Mountain", "Deku Scrub", "Grottos"))),
    ("DMC Deku Scrub Grotto Center",                    ("GrottoNPC2",  0xF9,  0x33, None,                     ("Death Mountain Crater", "Death Mountain", "Deku Scrub", "Grottos"))),
    ("DMC Deku Scrub Grotto Right",                     ("GrottoNPC2",  0xF9,  0x37, None,                     ("Death Mountain Crater", "Death Mountain", "Deku Scrub", "Grottos"))),
    ("DMC GS Crate",                                    ("GS Token",    0x0F,  0x80, None,                     ("Death Mountain Crater", "Skulltulas",))),
    ("DMC GS Bean Patch",                               ("GS Token",    0x0F,  0x01, None,                     ("Death Mountain Crater", "Skulltulas",))),

    # Zora's River
    ("ZR Magic Bean Salesman",                          ("NPC",         0x54,  0x16, None,                     ("Zora's River",))),
    ("ZR Open Grotto Chest",                            ("Chest",       0x3E,  0x09, None,                     ("Zora's River", "Grottos",))),
    ("ZR Frogs in the Rain",                            ("NPC",         0x54,  0x3E, None,                     ("Zora's River", "Minigames",))),
    ("ZR Frogs Ocarina Game",                           ("NPC",         0x54,  0x76, None,                     ("Zora's River",))),
    ("ZR Near Open Grotto Freestanding PoH",            ("Collectable", 0x54,  0x04, None,                     ("Zora's River",))),
    ("ZR Near Domain Freestanding PoH",                 ("Collectable", 0x54,  0x0B, None,                     ("Zora's River",))),
    ("ZR Deku Scrub Grotto Front",                      ("GrottoNPC2",  0xEB,  0x3A, None,                     ("Zora's River", "Deku Scrub", "Grottos"))),
    ("ZR Deku Scrub Grotto Rear",                       ("GrottoNPC2",  0xEB,  0x39, None,                     ("Zora's River", "Deku Scrub", "Grottos"))),
    ("ZR GS Tree",                                      ("GS Token",    0x11,  0x02, None,                     ("Zora's River", "Skulltulas",))),
    ("ZR GS Ladder",                                    ("GS Token",    0x11,  0x01, None,                     ("Zora's River", "Skulltulas",))),
    ("ZR GS Near Raised Grottos",                       ("GS Token",    0x11,  0x10, None,                     ("Zora's River", "Skulltulas",))),
    ("ZR GS Above Bridge",                              ("GS Token",    0x11,  0x08, None,                     ("Zora's River", "Skulltulas",))),

    # Zora's Domain
    ("ZD Diving Minigame",                              ("NPC",         0x58,  0x37, None,                     ("Zora's Domain", "Minigames",))),
    ("ZD Chest",                                        ("Chest",       0x58,  0x00, None,                     ("Zora's Domain", ))),
    ("ZD King Zora Thawed",                             ("NPC",         0x58,  0x2D, None,                     ("Zora's Domain",))),
    ("ZD GS Frozen Waterfall",                          ("GS Token",    0x11,  0x40, None,                     ("Zora's Domain", "Skulltulas",))),
    ("ZD Shop Item 1",                                  ("Shop",        0x2F,  0x30, (shop_address(7, 0), None), ("Zora's Domain", "Shops",))),
    ("ZD Shop Item 2",                                  ("Shop",        0x2F,  0x31, (shop_address(7, 1), None), ("Zora's Domain", "Shops",))),
    ("ZD Shop Item 3",                                  ("Shop",        0x2F,  0x32, (shop_address(7, 2), None), ("Zora's Domain", "Shops",))),
    ("ZD Shop Item 4",                                  ("Shop",        0x2F,  0x33, (shop_address(7, 3), None), ("Zora's Domain", "Shops",))),
    ("ZD Shop Item 5",                                  ("Shop",        0x2F,  0x34, (shop_address(7, 4), None), ("Zora's Domain", "Shops",))),
    ("ZD Shop Item 6",                                  ("Shop",        0x2F,  0x35, (shop_address(7, 5), None), ("Zora's Domain", "Shops",))),
    ("ZD Shop Item 7",                                  ("Shop",        0x2F,  0x36, (shop_address(7, 6), None), ("Zora's Domain", "Shops",))),
    ("ZD Shop Item 8",                                  ("Shop",        0x2F,  0x37, (shop_address(7, 7), None), ("Zora's Domain", "Shops",))),

    # Zora's Fountain
    ("ZF Great Fairy Reward",                           ("Cutscene",    0xFF,  0x10, None,                     ("Zora's Fountain", "Fairies",))),
    ("ZF Iceberg Freestanding PoH",                     ("Collectable", 0x59,  0x01, None,                     ("Zora's Fountain",))),
    ("ZF Bottom Freestanding PoH",                      ("Collectable", 0x59,  0x14, None,                     ("Zora's Fountain",))),
    ("ZF GS Above the Log",                             ("GS Token",    0x11,  0x04, None,                     ("Zora's Fountain", "Skulltulas",))),
    ("ZF GS Tree",                                      ("GS Token",    0x11,  0x80, None,                     ("Zora's Fountain", "Skulltulas",))),
    ("ZF GS Hidden Cave",                               ("GS Token",    0x11,  0x20, None,                     ("Zora's Fountain", "Skulltulas",))),

    # Lake Hylia
    ("LH Underwater Item",                              ("NPC",         0x57,  0x15, None,                     ("Lake Hylia",))),
    ("LH Child Fishing",                                ("NPC",         0x49,  0x3E, None,                     ("Lake Hylia", "Minigames",))),
    ("LH Adult Fishing",                                ("NPC",         0x49,  0x38, None,                     ("Lake Hylia", "Minigames",))),
    ("LH Lab Dive",                                     ("NPC",         0x38,  0x3E, None,                     ("Lake Hylia",))),
    ("LH Freestanding PoH",                             ("Collectable", 0x57,  0x1E, None,                     ("Lake Hylia",))),
    ("LH Sun",                                          ("NPC",         0x57,  0x58, None,                     ("Lake Hylia",))),
    ("LH Deku Scrub Grotto Left",                       ("GrottoNPC2",  0xEF,  0x30, None,                     ("Lake Hylia", "Deku Scrub", "Grottos"))),
    ("LH Deku Scrub Grotto Center",                     ("GrottoNPC2",  0xEF,  0x33, None,                     ("Lake Hylia", "Deku Scrub", "Grottos"))),
    ("LH Deku Scrub Grotto Right",                      ("GrottoNPC2",  0xEF,  0x37, None,                     ("Lake Hylia", "Deku Scrub", "Grottos"))),
    ("LH GS Bean Patch",                                ("GS Token",    0x12,  0x01, None,                     ("Lake Hylia", "Skulltulas",))),
    ("LH GS Lab Wall",                                  ("GS Token",    0x12,  0x04, None,                     ("Lake Hylia", "Skulltulas",))),
    ("LH GS Small Island",                              ("GS Token",    0x12,  0x02, None,                     ("Lake Hylia", "Skulltulas",))),
    ("LH GS Lab Crate",                                 ("GS Token",    0x12,  0x08, None,                     ("Lake Hylia", "Skulltulas",))),
    ("LH GS Tree",                                      ("GS Token",    0x12,  0x10, None,                     ("Lake Hylia", "Skulltulas",))),

    # Gerudo Valley
    ("GV Crate Freestanding PoH",                       ("Collectable", 0x5A,  0x02, None,                     ("Gerudo Valley", "Gerudo",))),
    ("GV Waterfall Freestanding PoH",                   ("Collectable", 0x5A,  0x01, None,                     ("Gerudo Valley", "Gerudo",))),
    ("GV Chest",                                        ("Chest",       0x5A,  0x00, None,                     ("Gerudo Valley", "Gerudo",))),
    ("GV Deku Scrub Grotto Front",                      ("GrottoNPC2",  0xF0,  0x3A, None,                     ("Gerudo Valley", "Gerudo", "Deku Scrub", "Grottos"))),
    ("GV Deku Scrub Grotto Rear",                       ("GrottoNPC2",  0xF0,  0x39, None,                     ("Gerudo Valley", "Gerudo", "Deku Scrub", "Grottos"))),
    ("GV Cow",                                          ("RepeatNPC2",  0x5A,  0x15, None,                     ("Gerudo Valley", "Gerudo", "Cow"))),
    ("GV GS Small Bridge",                              ("GS Token",    0x13,  0x02, None,                     ("Gerudo Valley", "Skulltulas",))),
    ("GV GS Bean Patch",                                ("GS Token",    0x13,  0x01, None,                     ("Gerudo Valley", "Skulltulas",))),
    ("GV GS Behind Tent",                               ("GS Token",    0x13,  0x08, None,                     ("Gerudo Valley", "Skulltulas",))),
    ("GV GS Pillar",                                    ("GS Token",    0x13,  0x04, None,                     ("Gerudo Valley", "Skulltulas",))),

    # Gerudo's Fortress
    ("GF North F1 Carpenter",                           ("Collectable", 0x0C,  0x0C, None,                     ("Gerudo's Fortress", "Gerudo",))),
    ("GF North F2 Carpenter",                           ("Collectable", 0x0C,  0x0A, None,                     ("Gerudo's Fortress", "Gerudo",))),
    ("GF South F1 Carpenter",                           ("Collectable", 0x0C,  0x0E, None,                     ("Gerudo's Fortress", "Gerudo",))),
    ("GF South F2 Carpenter",                           ("Collectable", 0x0C,  0x0F, None,                     ("Gerudo's Fortress", "Gerudo",))),
    ("GF Gerudo Membership Card",                       ("NPC",         0x0C,  0x3A, None,                     ("Gerudo's Fortress", "Gerudo",))),
    ("GF Chest",                                        ("Chest",       0x5D,  0x00, None,                     ("Gerudo's Fortress", "Gerudo",))),
    ("GF HBA 1000 Points",                              ("NPC",         0x5D,  0x3E, None,                     ("Gerudo's Fortress", "Gerudo", "Minigames"))),
    ("GF HBA 1500 Points",                              ("NPC",         0x5D,  0x30, None,                     ("Gerudo's Fortress", "Gerudo", "Minigames"))),
    ("GF GS Top Floor",                                 ("GS Token",    0x14,  0x02, None,                     ("Gerudo's Fortress", "Skulltulas",))),
    ("GF GS Archery Range",                             ("GS Token",    0x14,  0x01, None,                     ("Gerudo's Fortress", "Skulltulas",))),

    # Wasteland
    ("Wasteland Bombchu Salesman",                      ("RepeatNPC",   0x5E,  0x03, None,                     ("Haunted Wasteland",))),
    ("Wasteland Chest",                                 ("Chest",       0x5E,  0x00, None,                     ("Haunted Wasteland",))),
    ("Wasteland GS",                                    ("GS Token",    0x15,  0x02, None,                     ("Haunted Wasteland", "Skulltulas",))),

    # Colossus
    ("Colossus Great Fairy Reward",                     ("Cutscene",    0xFF,  0x12, None,                     ("Desert Colossus", "Fairies",))),
    ("Colossus Freestanding PoH",                       ("Collectable", 0x5C,  0x0D, None,                     ("Desert Colossus",))),
    ("Colossus Deku Scrub Grotto Front",                ("GrottoNPC2",  0xFD,  0x3A, None,                     ("Desert Colossus", "Deku Scrub", "Grottos"))),
    ("Colossus Deku Scrub Grotto Rear",                 ("GrottoNPC2",  0xFD,  0x39, None,                     ("Desert Colossus", "Deku Scrub", "Grottos"))),
    ("Colossus GS Bean Patch",                          ("GS Token",    0x15,  0x01, None,                     ("Desert Colossus", "Skulltulas",))),
    ("Colossus GS Tree",                                ("GS Token",    0x15,  0x08, None,                     ("Desert Colossus", "Skulltulas",))),
    ("Colossus GS Hill",                                ("GS Token",    0x15,  0x04, None,                     ("Desert Colossus", "Skulltulas",))),

    # Outside Ganon's Castle
    ("OGC Great Fairy Reward",                          ("Cutscene",    0xFF,  0x15, None,                     ("outside Ganon's Castle", "Market", "Fairies"))),
    ("OGC GS",                                          ("GS Token",    0x0E,  0x01, None,                     ("outside Ganon's Castle", "Skulltulas",))),

    ## Dungeons
    # Deku Tree vanilla
    ("Deku Tree Map Chest",                                 ("Chest",       0x00,  0x03, None,                 ("Deku Tree",))),
    ("Deku Tree Slingshot Room Side Chest",                 ("Chest",       0x00,  0x05, None,                 ("Deku Tree",))),
    ("Deku Tree Slingshot Chest",                           ("Chest",       0x00,  0x01, None,                 ("Deku Tree",))),
    ("Deku Tree Compass Chest",                             ("Chest",       0x00,  0x02, None,                 ("Deku Tree",))),
    ("Deku Tree Compass Room Side Chest",                   ("Chest",       0x00,  0x06, None,                 ("Deku Tree",))),
    ("Deku Tree Basement Chest",                            ("Chest",       0x00,  0x04, None,                 ("Deku Tree",))),
    ("Deku Tree GS Compass Room",                           ("GS Token",    0x00,  0x08, None,                 ("Deku Tree", "Skulltulas",))),
    ("Deku Tree GS Basement Vines",                         ("GS Token",    0x00,  0x04, None,                 ("Deku Tree", "Skulltulas",))),
    ("Deku Tree GS Basement Gate",                          ("GS Token",    0x00,  0x02, None,                 ("Deku Tree", "Skulltulas",))),
    ("Deku Tree GS Basement Back Room",                     ("GS Token",    0x00,  0x01, None,                 ("Deku Tree", "Skulltulas",))),
    # Deku Tree MQ
    ("Deku Tree MQ Map Chest",                              ("Chest",       0x00,  0x03, None,                 ("Deku Tree",))),
    ("Deku Tree MQ Slingshot Chest",                        ("Chest",       0x00,  0x06, None,                 ("Deku Tree",))),
    ("Deku Tree MQ Slingshot Room Back Chest",              ("Chest",       0x00,  0x02, None,                 ("Deku Tree",))),
    ("Deku Tree MQ Compass Chest",                          ("Chest",       0x00,  0x01, None,                 ("Deku Tree",))),
    ("Deku Tree MQ Basement Chest",                         ("Chest",       0x00,  0x04, None,                 ("Deku Tree",))),
    ("Deku Tree MQ Before Spinning Log Chest",              ("Chest",       0x00,  0x05, None,                 ("Deku Tree",))),
    ("Deku Tree MQ After Spinning Log Chest",               ("Chest",       0x00,  0x00, None,                 ("Deku Tree",))),
    ("Deku Tree MQ Deku Scrub",                             ("RepeatNPC2",  0x00,  0x34, None,                 ("Deku Tree", "Deku Scrub",))),
    ("Deku Tree MQ GS Lobby",                               ("GS Token",    0x00,  0x02, None,                 ("Deku Tree", "Skulltulas",))),
    ("Deku Tree MQ GS Compass Room",                        ("GS Token",    0x00,  0x08, None,                 ("Deku Tree", "Skulltulas",))),
    ("Deku Tree MQ GS Basement Graves Room",                ("GS Token",    0x00,  0x04, None,                 ("Deku Tree", "Skulltulas",))),
    ("Deku Tree MQ GS Basement Back Room",                  ("GS Token",    0x00,  0x01, None,                 ("Deku Tree", "Skulltulas",))),
    # Deku Tree shared
    ("Deku Tree Queen Gohma Heart",                         ("BossHeart",   0x11,  0x4F, None,                 ("Deku Tree",))),

    # Dodongo's Cavern vanilla
    ("Dodongos Cavern Map Chest",                           ("Chest",       0x01,  0x08, None,                 ("Dodongo's Cavern",))),
    ("Dodongos Cavern Compass Chest",                       ("Chest",       0x01,  0x05, None,                 ("Dodongo's Cavern",))),
    ("Dodongos Cavern Bomb Flower Platform Chest",          ("Chest",       0x01,  0x06, None,                 ("Dodongo's Cavern",))),
    ("Dodongos Cavern Bomb Bag Chest",                      ("Chest",       0x01,  0x04, None,                 ("Dodongo's Cavern",))),
    ("Dodongos Cavern End of Bridge Chest",                 ("Chest",       0x01,  0x0A, None,                 ("Dodongo's Cavern",))),
    ("Dodongos Cavern Deku Scrub Side Room Near Dodongos",  ("RepeatNPC2",  0x01,  0x31, None,                 ("Dodongo's Cavern", "Deku Scrub",))),
    ("Dodongos Cavern Deku Scrub Lobby",                    ("RepeatNPC2",  0x01,  0x34, None,                 ("Dodongo's Cavern", "Deku Scrub",))),
    ("Dodongos Cavern Deku Scrub Near Bomb Bag Left",       ("RepeatNPC2",  0x01,  0x30, None,                 ("Dodongo's Cavern", "Deku Scrub",))),
    ("Dodongos Cavern Deku Scrub Near Bomb Bag Right",      ("RepeatNPC2",  0x01,  0x33, None,                 ("Dodongo's Cavern", "Deku Scrub",))),
    ("Dodongos Cavern GS Side Room Near Lower Lizalfos",    ("GS Token",    0x01,  0x10, None,                 ("Dodongo's Cavern", "Skulltulas",))),
    ("Dodongos Cavern GS Scarecrow",                        ("GS Token",    0x01,  0x02, None,                 ("Dodongo's Cavern", "Skulltulas",))),
    ("Dodongos Cavern GS Alcove Above Stairs",              ("GS Token",    0x01,  0x04, None,                 ("Dodongo's Cavern", "Skulltulas",))),
    ("Dodongos Cavern GS Vines Above Stairs",               ("GS Token",    0x01,  0x01, None,                 ("Dodongo's Cavern", "Skulltulas",))),
    ("Dodongos Cavern GS Back Room",                        ("GS Token",    0x01,  0x08, None,                 ("Dodongo's Cavern", "Skulltulas",))),
    # Dodongo's Cavern MQ
    ("Dodongos Cavern MQ Map Chest",                        ("Chest",       0x01,  0x00, None,                 ("Dodongo's Cavern",))),
    ("Dodongos Cavern MQ Bomb Bag Chest",                   ("Chest",       0x01,  0x04, None,                 ("Dodongo's Cavern",))),
    ("Dodongos Cavern MQ Torch Puzzle Room Chest",          ("Chest",       0x01,  0x03, None,                 ("Dodongo's Cavern",))),
    ("Dodongos Cavern MQ Larvae Room Chest",                ("Chest",       0x01,  0x02, None,                 ("Dodongo's Cavern",))),
    ("Dodongos Cavern MQ Compass Chest",                    ("Chest",       0x01,  0x05, None,                 ("Dodongo's Cavern",))),
    ("Dodongos Cavern MQ Under Grave Chest",                ("Chest",       0x01,  0x01, None,                 ("Dodongo's Cavern",))),
    ("Dodongos Cavern MQ Deku Scrub Lobby Front",           ("RepeatNPC2",  0x01,  0x33, None,                 ("Dodongo's Cavern", "Deku Scrub",))),
    ("Dodongos Cavern MQ Deku Scrub Lobby Rear",            ("RepeatNPC2",  0x01,  0x31, None,                 ("Dodongo's Cavern", "Deku Scrub",))),
    ("Dodongos Cavern MQ Deku Scrub Side Room Near Lower Lizalfos", ("RepeatNPC2", 0x01,  0x39, None,          ("Dodongo's Cavern", "Deku Scrub",))),
    ("Dodongos Cavern MQ Deku Scrub Staircase",             ("RepeatNPC2",  0x01,  0x34, None,                 ("Dodongo's Cavern", "Deku Scrub",))),
    ("Dodongos Cavern MQ GS Scrub Room",                    ("GS Token",    0x01,  0x02, None,                 ("Dodongo's Cavern", "Skulltulas",))),
    ("Dodongos Cavern MQ GS Larvae Room",                   ("GS Token",    0x01,  0x10, None,                 ("Dodongo's Cavern", "Skulltulas",))),
    ("Dodongos Cavern MQ GS Lizalfos Room",                 ("GS Token",    0x01,  0x04, None,                 ("Dodongo's Cavern", "Skulltulas",))),
    ("Dodongos Cavern MQ GS Song of Time Block Room",       ("GS Token",    0x01,  0x08, None,                 ("Dodongo's Cavern", "Skulltulas",))),
    ("Dodongos Cavern MQ GS Back Area",                     ("GS Token",    0x01,  0x01, None,                 ("Dodongo's Cavern", "Skulltulas",))),
    # Dodongo's Cavern shared
    ("Dodongos Cavern Boss Room Chest",                     ("Chest",       0x12,  0x00, None,                 ("Dodongo's Cavern",))),
    ("Dodongos Cavern King Dodongo Heart",                  ("BossHeart",   0x12,  0x4F, None,                 ("Dodongo's Cavern",))),

    # Jabu Jabu's Belly vanilla
    ("Jabu Jabus Belly Boomerang Chest",                    ("Chest",       0x02,  0x01, None,                 ("Jabu Jabu's Belly",))),
    ("Jabu Jabus Belly Map Chest",                          ("Chest",       0x02,  0x02, None,                 ("Jabu Jabu's Belly",))),
    ("Jabu Jabus Belly Compass Chest",                      ("Chest",       0x02,  0x04, None,                 ("Jabu Jabu's Belly",))),
    ("Jabu Jabus Belly Deku Scrub",                         ("RepeatNPC2",  0x02,  0x30, None,                 ("Jabu Jabu's Belly", "Deku Scrub",))),
    ("Jabu Jabus Belly GS Water Switch Room",               ("GS Token",    0x02,  0x08, None,                 ("Jabu Jabu's Belly", "Skulltulas",))),
    ("Jabu Jabus Belly GS Lobby Basement Lower",            ("GS Token",    0x02,  0x01, None,                 ("Jabu Jabu's Belly", "Skulltulas",))),
    ("Jabu Jabus Belly GS Lobby Basement Upper",            ("GS Token",    0x02,  0x02, None,                 ("Jabu Jabu's Belly", "Skulltulas",))),
    ("Jabu Jabus Belly GS Near Boss",                       ("GS Token",    0x02,  0x04, None,                 ("Jabu Jabu's Belly", "Skulltulas",))),
    # Jabu Jabu's Belly MQ
    ("Jabu Jabus Belly MQ Map Chest",                       ("Chest",       0x02,  0x03, None,                 ("Jabu Jabu's Belly",))),
    ("Jabu Jabus Belly MQ First Room Side Chest",           ("Chest",       0x02,  0x05, None,                 ("Jabu Jabu's Belly",))),
    ("Jabu Jabus Belly MQ Second Room Lower Chest",         ("Chest",       0x02,  0x02, None,                 ("Jabu Jabu's Belly",))),
    ("Jabu Jabus Belly MQ Compass Chest",                   ("Chest",       0x02,  0x00, None,                 ("Jabu Jabu's Belly",))),
    ("Jabu Jabus Belly MQ Basement Near Switches Chest",    ("Chest",       0x02,  0x08, None,                 ("Jabu Jabu's Belly",))),
    ("Jabu Jabus Belly MQ Basement Near Vines Chest",       ("Chest",       0x02,  0x04, None,                 ("Jabu Jabu's Belly",))),
    ("Jabu Jabus Belly MQ Boomerang Room Small Chest",      ("Chest",       0x02,  0x01, None,                 ("Jabu Jabu's Belly",))),
    ("Jabu Jabus Belly MQ Boomerang Chest",                 ("Chest",       0x02,  0x06, None,                 ("Jabu Jabu's Belly",))),
    ("Jabu Jabus Belly MQ Falling Like Like Room Chest",    ("Chest",       0x02,  0x09, None,                 ("Jabu Jabu's Belly",))),
    ("Jabu Jabus Belly MQ Second Room Upper Chest",         ("Chest",       0x02,  0x07, None,                 ("Jabu Jabu's Belly",))),
    ("Jabu Jabus Belly MQ Near Boss Chest",                 ("Chest",       0x02,  0x0A, None,                 ("Jabu Jabu's Belly",))),
    ("Jabu Jabus Belly MQ Cow",                             ("RepeatNPC2",  0x02,  0x15, None,                 ("Jabu Jabu's Belly", "Cow",))),
    ("Jabu Jabus Belly MQ GS Boomerang Chest Room",         ("GS Token",    0x02,  0x01, None,                 ("Jabu Jabu's Belly", "Skulltulas",))),
    ("Jabu Jabus Belly MQ GS Tailpasaran Room",             ("GS Token",    0x02,  0x04, None,                 ("Jabu Jabu's Belly", "Skulltulas",))),
    ("Jabu Jabus Belly MQ GS Invisible Enemies Room",       ("GS Token",    0x02,  0x08, None,                 ("Jabu Jabu's Belly", "Skulltulas",))),
    ("Jabu Jabus Belly MQ GS Near Boss",                    ("GS Token",    0x02,  0x02, None,                 ("Jabu Jabu's Belly", "Skulltulas",))),
    # Jabu Jabu's Belly shared
    ("Jabu Jabus Belly Barinade Heart",                     ("BossHeart",   0x13,  0x4F, None,                 ("Jabu Jabu's Belly",))),

    # Bottom of the Well vanilla
    ("Bottom of the Well Front Left Fake Wall Chest",       ("Chest",       0x08,  0x08, None,                 ("Bottom of the Well",))),
    ("Bottom of the Well Front Center Bombable Chest",      ("Chest",       0x08,  0x02, None,                 ("Bottom of the Well",))),
    ("Bottom of the Well Back Left Bombable Chest",         ("Chest",       0x08,  0x04, None,                 ("Bottom of the Well",))),
    ("Bottom of the Well Underwater Left Chest",            ("Chest",       0x08,  0x09, None,                 ("Bottom of the Well",))),
    ("Bottom of the Well Freestanding Key",                 ("Collectable", 0x08,  0x01, None,                 ("Bottom of the Well",))),
    ("Bottom of the Well Compass Chest",                    ("Chest",       0x08,  0x01, None,                 ("Bottom of the Well",))),
    ("Bottom of the Well Center Skulltula Chest",           ("Chest",       0x08,  0x0E, None,                 ("Bottom of the Well",))),
    ("Bottom of the Well Right Bottom Fake Wall Chest",     ("Chest",       0x08,  0x05, None,                 ("Bottom of the Well",))),
    ("Bottom of the Well Fire Keese Chest",                 ("Chest",       0x08,  0x0A, None,                 ("Bottom of the Well",))),
    ("Bottom of the Well Like Like Chest",                  ("Chest",       0x08,  0x0C, None,                 ("Bottom of the Well",))),
    ("Bottom of the Well Map Chest",                        ("Chest",       0x08,  0x07, None,                 ("Bottom of the Well",))),
    ("Bottom of the Well Underwater Front Chest",           ("Chest",       0x08,  0x10, None,                 ("Bottom of the Well",))),
    ("Bottom of the Well Invisible Chest",                  ("Chest",       0x08,  0x14, None,                 ("Bottom of the Well",))),
    ("Bottom of the Well Lens of Truth Chest",              ("Chest",       0x08,  0x03, None,                 ("Bottom of the Well",))),
    ("Bottom of the Well GS West Inner Room",               ("GS Token",    0x08,  0x04, None,                 ("Bottom of the Well", "Skulltulas",))),
    ("Bottom of the Well GS East Inner Room",               ("GS Token",    0x08,  0x02, None,                 ("Bottom of the Well", "Skulltulas",))),
    ("Bottom of the Well GS Like Like Cage",                ("GS Token",    0x08,  0x01, None,                 ("Bottom of the Well", "Skulltulas",))),

    # Bottom of the Well MQ
    ("Bottom of the Well MQ Map Chest",                     ("Chest",       0x08,  0x03, None,                 ("Bottom of the Well",))),
    ("Bottom of the Well MQ East Inner Room Freestanding Key",("Collectable", 0x08,  0x01, None,               ("Bottom of the Well",))),
    ("Bottom of the Well MQ Compass Chest",                 ("Chest",       0x08,  0x02, None,                 ("Bottom of the Well",))),
    ("Bottom of the Well MQ Dead Hand Freestanding Key",    ("Collectable", 0x08,  0x02, None,                 ("Bottom of the Well",))),
    ("Bottom of the Well MQ Lens of Truth Chest",           ("Chest",       0x08,  0x01, None,                 ("Bottom of the Well",))),
    ("Bottom of the Well MQ GS Coffin Room",                ("GS Token",    0x08,  0x04, None,                 ("Bottom of the Well", "Skulltulas",))),
    ("Bottom of the Well MQ GS West Inner Room",            ("GS Token",    0x08,  0x02, None,                 ("Bottom of the Well", "Skulltulas",))),
    ("Bottom of the Well MQ GS Basement",                   ("GS Token",    0x08,  0x01, None,                 ("Bottom of the Well", "Skulltulas",))),

    # Forest Temple vanilla
    ("Forest Temple First Room Chest",                      ("Chest",       0x03,  0x03, None,                 ("Forest Temple",))),
    ("Forest Temple First Stalfos Chest",                   ("Chest",       0x03,  0x00, None,                 ("Forest Temple",))),
    ("Forest Temple Raised Island Courtyard Chest",         ("Chest",       0x03,  0x05, None,                 ("Forest Temple",))),
    ("Forest Temple Map Chest",                             ("Chest",       0x03,  0x01, None,                 ("Forest Temple",))),
    ("Forest Temple Well Chest",                            ("Chest",       0x03,  0x09, None,                 ("Forest Temple",))),
    ("Forest Temple Eye Switch Chest",                      ("Chest",       0x03,  0x04, None,                 ("Forest Temple",))),
    ("Forest Temple Boss Key Chest",                        ("Chest",       0x03,  0x0E, None,                 ("Forest Temple",))),
    ("Forest Temple Floormaster Chest",                     ("Chest",       0x03,  0x02, None,                 ("Forest Temple",))),
    ("Forest Temple Red Poe Chest",                         ("Chest",       0x03,  0x0D, None,                 ("Forest Temple",))),
    ("Forest Temple Bow Chest",                             ("Chest",       0x03,  0x0C, None,                 ("Forest Temple",))),
    ("Forest Temple Blue Poe Chest",                        ("Chest",       0x03,  0x0F, None,                 ("Forest Temple",))),
    ("Forest Temple Falling Ceiling Room Chest",            ("Chest",       0x03,  0x07, None,                 ("Forest Temple",))),
    ("Forest Temple Basement Chest",                        ("Chest",       0x03,  0x0B, None,                 ("Forest Temple",))),
    ("Forest Temple GS First Room",                         ("GS Token",    0x03,  0x02, None,                 ("Forest Temple", "Skulltulas",))),
    ("Forest Temple GS Lobby",                              ("GS Token",    0x03,  0x08, None,                 ("Forest Temple", "Skulltulas",))),
    ("Forest Temple GS Raised Island Courtyard",            ("GS Token",    0x03,  0x01, None,                 ("Forest Temple", "Skulltulas",))),
    ("Forest Temple GS Level Island Courtyard",             ("GS Token",    0x03,  0x04, None,                 ("Forest Temple", "Skulltulas",))),
    ("Forest Temple GS Basement",                           ("GS Token",    0x03,  0x10, None,                 ("Forest Temple", "Skulltulas",))),
    # Forest Temple MQ
    ("Forest Temple MQ First Room Chest",                   ("Chest",       0x03,  0x03, None,                 ("Forest Temple",))),
    ("Forest Temple MQ Wolfos Chest",                       ("Chest",       0x03,  0x00, None,                 ("Forest Temple",))),
    ("Forest Temple MQ Well Chest",                         ("Chest",       0x03,  0x09, None,                 ("Forest Temple",))),
    ("Forest Temple MQ Raised Island Courtyard Lower Chest",("Chest",       0x03,  0x01, None,                 ("Forest Temple",))),
    ("Forest Temple MQ Raised Island Courtyard Upper Chest",("Chest",       0x03,  0x05, None,                 ("Forest Temple",))),
    ("Forest Temple MQ Boss Key Chest",                     ("Chest",       0x03,  0x0E, None,                 ("Forest Temple",))),
    ("Forest Temple MQ Redead Chest",                       ("Chest",       0x03,  0x02, None,                 ("Forest Temple",))),
    ("Forest Temple MQ Map Chest",                          ("Chest",       0x03,  0x0D, None,                 ("Forest Temple",))),
    ("Forest Temple MQ Bow Chest",                          ("Chest",       0x03,  0x0C, None,                 ("Forest Temple",))),
    ("Forest Temple MQ Compass Chest",                      ("Chest",       0x03,  0x0F, None,                 ("Forest Temple",))),
    ("Forest Temple MQ Falling Ceiling Room Chest",         ("Chest",       0x03,  0x06, None,                 ("Forest Temple",))),
    ("Forest Temple MQ Basement Chest",                     ("Chest",       0x03,  0x0B, None,                 ("Forest Temple",))),
    ("Forest Temple MQ GS First Hallway",                   ("GS Token",    0x03,  0x02, None,                 ("Forest Temple", "Skulltulas",))),
    ("Forest Temple MQ GS Raised Island Courtyard",         ("GS Token",    0x03,  0x01, None,                 ("Forest Temple", "Skulltulas",))),
    ("Forest Temple MQ GS Level Island Courtyard",          ("GS Token",    0x03,  0x04, None,                 ("Forest Temple", "Skulltulas",))),
    ("Forest Temple MQ GS Well",                            ("GS Token",    0x03,  0x08, None,                 ("Forest Temple", "Skulltulas",))),
    ("Forest Temple MQ GS Block Push Room",                 ("GS Token",    0x03,  0x10, None,                 ("Forest Temple", "Skulltulas",))),
    # Forest Temple shared
    ("Forest Temple Phantom Ganon Heart",                   ("BossHeart",   0x14,  0x4F, None,                 ("Forest Temple",))),

    # Fire Temple vanilla
    ("Fire Temple Near Boss Chest",                         ("Chest",       0x04,  0x01, None,                 ("Fire Temple",))),
    ("Fire Temple Flare Dancer Chest",                      ("Chest",       0x04,  0x00, None,                 ("Fire Temple",))),
    ("Fire Temple Boss Key Chest",                          ("Chest",       0x04,  0x0C, None,                 ("Fire Temple",))),
    ("Fire Temple Big Lava Room Lower Open Door Chest",     ("Chest",       0x04,  0x04, None,                 ("Fire Temple",))),
    ("Fire Temple Big Lava Room Blocked Door Chest",        ("Chest",       0x04,  0x02, None,                 ("Fire Temple",))),
    ("Fire Temple Boulder Maze Lower Chest",                ("Chest",       0x04,  0x03, None,                 ("Fire Temple",))),
    ("Fire Temple Boulder Maze Side Room Chest",            ("Chest",       0x04,  0x08, None,                 ("Fire Temple",))),
    ("Fire Temple Map Chest",                               ("Chest",       0x04,  0x0A, None,                 ("Fire Temple",))),
    ("Fire Temple Boulder Maze Shortcut Chest",             ("Chest",       0x04,  0x0B, None,                 ("Fire Temple",))),
    ("Fire Temple Boulder Maze Upper Chest",                ("Chest",       0x04,  0x06, None,                 ("Fire Temple",))),
    ("Fire Temple Scarecrow Chest",                         ("Chest",       0x04,  0x0D, None,                 ("Fire Temple",))),
    ("Fire Temple Compass Chest",                           ("Chest",       0x04,  0x07, None,                 ("Fire Temple",))),
    ("Fire Temple Megaton Hammer Chest",                    ("Chest",       0x04,  0x05, None,                 ("Fire Temple",))),
    ("Fire Temple Highest Goron Chest",                     ("Chest",       0x04,  0x09, None,                 ("Fire Temple",))),
    ("Fire Temple GS Boss Key Loop",                        ("GS Token",    0x04,  0x02, None,                 ("Fire Temple", "Skulltulas",))),
    ("Fire Temple GS Song of Time Room",                    ("GS Token",    0x04,  0x01, None,                 ("Fire Temple", "Skulltulas",))),
    ("Fire Temple GS Boulder Maze",                         ("GS Token",    0x04,  0x04, None,                 ("Fire Temple", "Skulltulas",))),
    ("Fire Temple GS Scarecrow Climb",                      ("GS Token",    0x04,  0x10, None,                 ("Fire Temple", "Skulltulas",))),
    ("Fire Temple GS Scarecrow Top",                        ("GS Token",    0x04,  0x08, None,                 ("Fire Temple", "Skulltulas",))),
    # Fire Temple MQ
    ("Fire Temple MQ Map Room Side Chest",                  ("Chest",       0x04,  0x02, None,                 ("Fire Temple",))),
    ("Fire Temple MQ Megaton Hammer Chest",                 ("Chest",       0x04,  0x00, None,                 ("Fire Temple",))),
    ("Fire Temple MQ Map Chest",                            ("Chest",       0x04,  0x0C, None,                 ("Fire Temple",))),
    ("Fire Temple MQ Near Boss Chest",                      ("Chest",       0x04,  0x07, None,                 ("Fire Temple",))),
    ("Fire Temple MQ Big Lava Room Blocked Door Chest",     ("Chest",       0x04,  0x01, None,                 ("Fire Temple",))),
    ("Fire Temple MQ Boss Key Chest",                       ("Chest",       0x04,  0x04, None,                 ("Fire Temple",))),
    ("Fire Temple MQ Lizalfos Maze Side Room Chest",        ("Chest",       0x04,  0x08, None,                 ("Fire Temple",))),
    ("Fire Temple MQ Compass Chest",                        ("Chest",       0x04,  0x0B, None,                 ("Fire Temple",))),
    ("Fire Temple MQ Lizalfos Maze Upper Chest",            ("Chest",       0x04,  0x06, None,                 ("Fire Temple",))),
    ("Fire Temple MQ Lizalfos Maze Lower Chest",            ("Chest",       0x04,  0x03, None,                 ("Fire Temple",))),
    ("Fire Temple MQ Freestanding Key",                     ("Collectable", 0x04,  0x1C, None,                 ("Fire Temple",))),
    ("Fire Temple MQ Chest On Fire",                        ("Chest",       0x04,  0x05, None,                 ("Fire Temple",))),
    ("Fire Temple MQ GS Big Lava Room Open Door",           ("GS Token",    0x04,  0x01, None,                 ("Fire Temple", "Skulltulas",))),
    ("Fire Temple MQ GS Skull On Fire",                     ("GS Token",    0x04,  0x04, None,                 ("Fire Temple", "Skulltulas",))),
    ("Fire Temple MQ GS Fire Wall Maze Center",             ("GS Token",    0x04,  0x08, None,                 ("Fire Temple", "Skulltulas",))),
    ("Fire Temple MQ GS Fire Wall Maze Side Room",          ("GS Token",    0x04,  0x10, None,                 ("Fire Temple", "Skulltulas",))),
    ("Fire Temple MQ GS Above Fire Wall Maze",              ("GS Token",    0x04,  0x02, None,                 ("Fire Temple", "Skulltulas",))),
    # Fire Temple shared
    ("Fire Temple Volvagia Heart",                          ("BossHeart",   0x15,  0x4F, None,                 ("Fire Temple",))),

    # Water Temple vanilla
    ("Water Temple Compass Chest",                          ("Chest",       0x05,  0x09, None,                 ("Water Temple",))),
    ("Water Temple Map Chest",                              ("Chest",       0x05,  0x02, None,                 ("Water Temple",))),
    ("Water Temple Cracked Wall Chest",                     ("Chest",       0x05,  0x00, None,                 ("Water Temple",))),
    ("Water Temple Torches Chest",                          ("Chest",       0x05,  0x01, None,                 ("Water Temple",))),
    ("Water Temple Boss Key Chest",                         ("Chest",       0x05,  0x05, None,                 ("Water Temple",))),
    ("Water Temple Central Pillar Chest",                   ("Chest",       0x05,  0x06, None,                 ("Water Temple",))),
    ("Water Temple Central Bow Target Chest",               ("Chest",       0x05,  0x08, None,                 ("Water Temple",))),
    ("Water Temple Longshot Chest",                         ("Chest",       0x05,  0x07, None,                 ("Water Temple",))),
    ("Water Temple River Chest",                            ("Chest",       0x05,  0x03, None,                 ("Water Temple",))),
    ("Water Temple Dragon Chest",                           ("Chest",       0x05,  0x0A, None,                 ("Water Temple",))),
    ("Water Temple GS Behind Gate",                         ("GS Token",    0x05,  0x01, None,                 ("Water Temple", "Skulltulas",))),
    ("Water Temple GS Near Boss Key Chest",                 ("GS Token",    0x05,  0x08, None,                 ("Water Temple", "Skulltulas",))),
    ("Water Temple GS Central Pillar",                      ("GS Token",    0x05,  0x04, None,                 ("Water Temple", "Skulltulas",))),
    ("Water Temple GS Falling Platform Room",               ("GS Token",    0x05,  0x02, None,                 ("Water Temple", "Skulltulas",))),
    ("Water Temple GS River",                               ("GS Token",    0x05,  0x10, None,                 ("Water Temple", "Skulltulas",))),
    # Water Temple MQ
    ("Water Temple MQ Longshot Chest",                      ("Chest",       0x05,  0x00, None,                 ("Water Temple",))),
    ("Water Temple MQ Map Chest",                           ("Chest",       0x05,  0x02, None,                 ("Water Temple",))),
    ("Water Temple MQ Compass Chest",                       ("Chest",       0x05,  0x01, None,                 ("Water Temple",))),
    ("Water Temple MQ Central Pillar Chest",                ("Chest",       0x05,  0x06, None,                 ("Water Temple",))),
    ("Water Temple MQ Boss Key Chest",                      ("Chest",       0x05,  0x05, None,                 ("Water Temple",))),
    ("Water Temple MQ Freestanding Key",                    ("Collectable", 0x05,  0x01, None,                 ("Water Temple",))),
    ("Water Temple MQ GS Lizalfos Hallway",                 ("GS Token",    0x05,  0x01, None,                 ("Water Temple", "Skulltulas",))),
    ("Water Temple MQ GS Before Upper Water Switch",        ("GS Token",    0x05,  0x04, None,                 ("Water Temple", "Skulltulas",))),
    ("Water Temple MQ GS River",                            ("GS Token",    0x05,  0x02, None,                 ("Water Temple", "Skulltulas",))),
    ("Water Temple MQ GS Freestanding Key Area",            ("GS Token",    0x05,  0x08, None,                 ("Water Temple", "Skulltulas",))),
    ("Water Temple MQ GS Triple Wall Torch",                ("GS Token",    0x05,  0x10, None,                 ("Water Temple", "Skulltulas",))),
    # Water Temple shared
    ("Water Temple Morpha Heart",                           ("BossHeart",   0x16,  0x4F, None,                 ("Water Temple",))),

    # Shadow Temple vanilla
    ("Shadow Temple Map Chest",                             ("Chest",       0x07,  0x01, None,                 ("Shadow Temple",))),
    ("Shadow Temple Hover Boots Chest",                     ("Chest",       0x07,  0x07, None,                 ("Shadow Temple",))),
    ("Shadow Temple Compass Chest",                         ("Chest",       0x07,  0x03, None,                 ("Shadow Temple",))),
    ("Shadow Temple Early Silver Rupee Chest",              ("Chest",       0x07,  0x02, None,                 ("Shadow Temple",))),
    ("Shadow Temple Invisible Blades Visible Chest",        ("Chest",       0x07,  0x0C, None,                 ("Shadow Temple",))),
    ("Shadow Temple Invisible Blades Invisible Chest",      ("Chest",       0x07,  0x16, None,                 ("Shadow Temple",))),
    ("Shadow Temple Falling Spikes Lower Chest",            ("Chest",       0x07,  0x05, None,                 ("Shadow Temple",))),
    ("Shadow Temple Falling Spikes Upper Chest",            ("Chest",       0x07,  0x06, None,                 ("Shadow Temple",))),
    ("Shadow Temple Falling Spikes Switch Chest",           ("Chest",       0x07,  0x04, None,                 ("Shadow Temple",))),
    ("Shadow Temple Invisible Spikes Chest",                ("Chest",       0x07,  0x09, None,                 ("Shadow Temple",))),
    ("Shadow Temple Freestanding Key",                      ("Collectable", 0x07,  0x01, None,                 ("Shadow Temple",))),
    ("Shadow Temple Wind Hint Chest",                       ("Chest",       0x07,  0x15, None,                 ("Shadow Temple",))),
    ("Shadow Temple After Wind Enemy Chest",                ("Chest",       0x07,  0x08, None,                 ("Shadow Temple",))),
    ("Shadow Temple After Wind Hidden Chest",               ("Chest",       0x07,  0x14, None,                 ("Shadow Temple",))),
    ("Shadow Temple Spike Walls Left Chest",                ("Chest",       0x07,  0x0A, None,                 ("Shadow Temple",))),
    ("Shadow Temple Boss Key Chest",                        ("Chest",       0x07,  0x0B, None,                 ("Shadow Temple",))),
    ("Shadow Temple Invisible Floormaster Chest",           ("Chest",       0x07,  0x0D, None,                 ("Shadow Temple",))),
    ("Shadow Temple GS Like Like Room",                     ("GS Token",    0x07,  0x08, None,                 ("Shadow Temple", "Skulltulas",))),
    ("Shadow Temple GS Falling Spikes Room",                ("GS Token",    0x07,  0x02, None,                 ("Shadow Temple", "Skulltulas",))),
    ("Shadow Temple GS Single Giant Pot",                   ("GS Token",    0x07,  0x01, None,                 ("Shadow Temple", "Skulltulas",))),
    ("Shadow Temple GS Near Ship",                          ("GS Token",    0x07,  0x10, None,                 ("Shadow Temple", "Skulltulas",))),
    ("Shadow Temple GS Triple Giant Pot",                   ("GS Token",    0x07,  0x04, None,                 ("Shadow Temple", "Skulltulas",))),
    # Shadow Temple MQ
    ("Shadow Temple MQ Early Gibdos Chest",                 ("Chest",       0x07,  0x03, None,                 ("Shadow Temple",))),
    ("Shadow Temple MQ Map Chest",                          ("Chest",       0x07,  0x02, None,                 ("Shadow Temple",))),
    ("Shadow Temple MQ Near Ship Invisible Chest",          ("Chest",       0x07,  0x0E, None,                 ("Shadow Temple",))),
    ("Shadow Temple MQ Compass Chest",                      ("Chest",       0x07,  0x01, None,                 ("Shadow Temple",))),
    ("Shadow Temple MQ Hover Boots Chest",                  ("Chest",       0x07,  0x07, None,                 ("Shadow Temple",))),
    ("Shadow Temple MQ Invisible Blades Invisible Chest",   ("Chest",       0x07,  0x16, None,                 ("Shadow Temple",))),
    ("Shadow Temple MQ Invisible Blades Visible Chest",     ("Chest",       0x07,  0x0C, None,                 ("Shadow Temple",))),
    ("Shadow Temple MQ Beamos Silver Rupees Chest",         ("Chest",       0x07,  0x0F, None,                 ("Shadow Temple",))),
    ("Shadow Temple MQ Falling Spikes Lower Chest",         ("Chest",       0x07,  0x05, None,                 ("Shadow Temple",))),
    ("Shadow Temple MQ Falling Spikes Upper Chest",         ("Chest",       0x07,  0x06, None,                 ("Shadow Temple",))),
    ("Shadow Temple MQ Falling Spikes Switch Chest",        ("Chest",       0x07,  0x04, None,                 ("Shadow Temple",))),
    ("Shadow Temple MQ Invisible Spikes Chest",             ("Chest",       0x07,  0x09, None,                 ("Shadow Temple",))),
    ("Shadow Temple MQ Stalfos Room Chest",                 ("Chest",       0x07,  0x10, None,                 ("Shadow Temple",))),
    ("Shadow Temple MQ Wind Hint Chest",                    ("Chest",       0x07,  0x15, None,                 ("Shadow Temple",))),
    ("Shadow Temple MQ After Wind Hidden Chest",            ("Chest",       0x07,  0x14, None,                 ("Shadow Temple",))),
    ("Shadow Temple MQ After Wind Enemy Chest",             ("Chest",       0x07,  0x08, None,                 ("Shadow Temple",))),
    ("Shadow Temple MQ Boss Key Chest",                     ("Chest",       0x07,  0x0B, None,                 ("Shadow Temple",))),
    ("Shadow Temple MQ Spike Walls Left Chest",             ("Chest",       0x07,  0x0A, None,                 ("Shadow Temple",))),
    ("Shadow Temple MQ Freestanding Key",                   ("Collectable", 0x07,  0x06, None,                 ("Shadow Temple",))),
    ("Shadow Temple MQ Bomb Flower Chest",                  ("Chest",       0x07,  0x0D, None,                 ("Shadow Temple",))),
    ("Shadow Temple MQ GS Falling Spikes Room",             ("GS Token",    0x07,  0x02, None,                 ("Shadow Temple", "Skulltulas",))),
    ("Shadow Temple MQ GS Wind Hint Room",                  ("GS Token",    0x07,  0x01, None,                 ("Shadow Temple", "Skulltulas",))),
    ("Shadow Temple MQ GS After Wind",                      ("GS Token",    0x07,  0x08, None,                 ("Shadow Temple", "Skulltulas",))),
    ("Shadow Temple MQ GS After Ship",                      ("GS Token",    0x07,  0x10, None,                 ("Shadow Temple", "Skulltulas",))),
    ("Shadow Temple MQ GS Near Boss",                       ("GS Token",    0x07,  0x04, None,                 ("Shadow Temple", "Skulltulas",))),
    # Shadow Temple shared
    ("Shadow Temple Bongo Bongo Heart",                     ("BossHeart",   0x18,  0x4F, None,                 ("Shadow Temple",))),

    # Spirit Temple shared
    # Vanilla and MQ locations are mixed to ensure the positions of Silver Gauntlets/Mirror Shield chests are correct for both versions
    ("Spirit Temple Child Bridge Chest",                    ("Chest",       0x06,  0x08, None,                 ("Spirit Temple",))),
    ("Spirit Temple Child Early Torches Chest",             ("Chest",       0x06,  0x00, None,                 ("Spirit Temple",))),
    ("Spirit Temple Child Climb North Chest",               ("Chest",       0x06,  0x06, None,                 ("Spirit Temple",))),
    ("Spirit Temple Child Climb East Chest",                ("Chest",       0x06,  0x0C, None,                 ("Spirit Temple",))),
    ("Spirit Temple Map Chest",                             ("Chest",       0x06,  0x03, None,                 ("Spirit Temple",))),
    ("Spirit Temple Sun Block Room Chest",                  ("Chest",       0x06,  0x01, None,                 ("Spirit Temple",))),
    ("Spirit Temple MQ Entrance Front Left Chest",          ("Chest",       0x06,  0x1A, None,                 ("Spirit Temple",))),
    ("Spirit Temple MQ Entrance Back Right Chest",          ("Chest",       0x06,  0x1F, None,                 ("Spirit Temple",))),
    ("Spirit Temple MQ Entrance Front Right Chest",         ("Chest",       0x06,  0x1B, None,                 ("Spirit Temple",))),
    ("Spirit Temple MQ Entrance Back Left Chest",           ("Chest",       0x06,  0x1E, None,                 ("Spirit Temple",))),
    ("Spirit Temple MQ Map Chest",                          ("Chest",       0x06,  0x00, None,                 ("Spirit Temple",))),
    ("Spirit Temple MQ Map Room Enemy Chest",               ("Chest",       0x06,  0x08, None,                 ("Spirit Temple",))),
    ("Spirit Temple MQ Child Climb North Chest",            ("Chest",       0x06,  0x06, None,                 ("Spirit Temple",))),
    ("Spirit Temple MQ Child Climb South Chest",            ("Chest",       0x06,  0x0C, None,                 ("Spirit Temple",))),
    ("Spirit Temple MQ Compass Chest",                      ("Chest",       0x06,  0x03, None,                 ("Spirit Temple",))),
    ("Spirit Temple MQ Silver Block Hallway Chest",         ("Chest",       0x06,  0x1C, None,                 ("Spirit Temple",))),
    ("Spirit Temple MQ Sun Block Room Chest",               ("Chest",       0x06,  0x01, None,                 ("Spirit Temple",))),
    ("Spirit Temple Silver Gauntlets Chest",                ("Chest",       0x5C,  0x0B, None,                 ("Spirit Temple", "Desert Colossus"))),

    ("Spirit Temple Compass Chest",                         ("Chest",       0x06,  0x04, None,                 ("Spirit Temple",))),
    ("Spirit Temple Early Adult Right Chest",               ("Chest",       0x06,  0x07, None,                 ("Spirit Temple",))),
    ("Spirit Temple First Mirror Left Chest",               ("Chest",       0x06,  0x0D, None,                 ("Spirit Temple",))),
    ("Spirit Temple First Mirror Right Chest",              ("Chest",       0x06,  0x0E, None,                 ("Spirit Temple",))),
    ("Spirit Temple Statue Room Northeast Chest",           ("Chest",       0x06,  0x0F, None,                 ("Spirit Temple",))),
    ("Spirit Temple Statue Room Hand Chest",                ("Chest",       0x06,  0x02, None,                 ("Spirit Temple",))),
    ("Spirit Temple Near Four Armos Chest",                 ("Chest",       0x06,  0x05, None,                 ("Spirit Temple",))),
    ("Spirit Temple Hallway Right Invisible Chest",         ("Chest",       0x06,  0x14, None,                 ("Spirit Temple",))),
    ("Spirit Temple Hallway Left Invisible Chest",          ("Chest",       0x06,  0x15, None,                 ("Spirit Temple",))),
    ("Spirit Temple MQ Child Hammer Switch Chest",          ("Chest",       0x06,  0x1D, None,                 ("Spirit Temple",))),
    ("Spirit Temple MQ Statue Room Lullaby Chest",          ("Chest",       0x06,  0x0F, None,                 ("Spirit Temple",))),
    ("Spirit Temple MQ Statue Room Invisible Chest",        ("Chest",       0x06,  0x02, None,                 ("Spirit Temple",))),
    ("Spirit Temple MQ Leever Room Chest",                  ("Chest",       0x06,  0x04, None,                 ("Spirit Temple",))),
    ("Spirit Temple MQ Symphony Room Chest",                ("Chest",       0x06,  0x07, None,                 ("Spirit Temple",))),
    ("Spirit Temple MQ Beamos Room Chest",                  ("Chest",       0x06,  0x19, None,                 ("Spirit Temple",))),
    ("Spirit Temple MQ Chest Switch Chest",                 ("Chest",       0x06,  0x18, None,                 ("Spirit Temple",))),
    ("Spirit Temple MQ Boss Key Chest",                     ("Chest",       0x06,  0x05, None,                 ("Spirit Temple",))),
    ("Spirit Temple Mirror Shield Chest",                   ("Chest",       0x5C,  0x09, None,                 ("Spirit Temple", "Desert Colossus"))),

    ("Spirit Temple Boss Key Chest",                        ("Chest",       0x06,  0x0A, None,                 ("Spirit Temple",))),
    ("Spirit Temple Topmost Chest",                         ("Chest",       0x06,  0x12, None,                 ("Spirit Temple",))),
    ("Spirit Temple MQ Mirror Puzzle Invisible Chest",      ("Chest",       0x06,  0x12, None,                 ("Spirit Temple",))),

    ("Spirit Temple GS Metal Fence",                        ("GS Token",    0x06,  0x10, None,                 ("Spirit Temple", "Skulltulas",))),
    ("Spirit Temple GS Sun on Floor Room",                  ("GS Token",    0x06,  0x08, None,                 ("Spirit Temple", "Skulltulas",))),
    ("Spirit Temple GS Hall After Sun Block Room",          ("GS Token",    0x06,  0x01, None,                 ("Spirit Temple", "Skulltulas",))),
    ("Spirit Temple GS Lobby",                              ("GS Token",    0x06,  0x04, None,                 ("Spirit Temple", "Skulltulas",))),
    ("Spirit Temple GS Boulder Room",                       ("GS Token",    0x06,  0x02, None,                 ("Spirit Temple", "Skulltulas",))),
    ("Spirit Temple MQ GS Sun Block Room",                  ("GS Token",    0x06,  0x01, None,                 ("Spirit Temple", "Skulltulas",))),
    ("Spirit Temple MQ GS Leever Room",                     ("GS Token",    0x06,  0x02, None,                 ("Spirit Temple", "Skulltulas",))),
    ("Spirit Temple MQ GS Symphony Room",                   ("GS Token",    0x06,  0x08, None,                 ("Spirit Temple", "Skulltulas",))),
    ("Spirit Temple MQ GS Nine Thrones Room West",          ("GS Token",    0x06,  0x04, None,                 ("Spirit Temple", "Skulltulas",))),
    ("Spirit Temple MQ GS Nine Thrones Room North",         ("GS Token",    0x06,  0x10, None,                 ("Spirit Temple", "Skulltulas",))),

    ("Spirit Temple Twinrova Heart",                        ("BossHeart",   0x17,  0x4F, None,                 ("Spirit Temple",))),

    # Ice Cavern vanilla
    ("Ice Cavern Map Chest",                                ("Chest",       0x09,  0x00, None,                 ("Ice Cavern",))),
    ("Ice Cavern Compass Chest",                            ("Chest",       0x09,  0x01, None,                 ("Ice Cavern",))),
    ("Ice Cavern Freestanding PoH",                         ("Collectable", 0x09,  0x01, None,                 ("Ice Cavern",))),
    ("Ice Cavern Iron Boots Chest",                         ("Chest",       0x09,  0x02, None,                 ("Ice Cavern",))),
    ("Ice Cavern GS Spinning Scythe Room",                  ("GS Token",    0x09,  0x02, None,                 ("Ice Cavern", "Skulltulas",))),
    ("Ice Cavern GS Heart Piece Room",                      ("GS Token",    0x09,  0x04, None,                 ("Ice Cavern", "Skulltulas",))),
    ("Ice Cavern GS Push Block Room",                       ("GS Token",    0x09,  0x01, None,                 ("Ice Cavern", "Skulltulas",))),
    # Ice Cavern MQ
    ("Ice Cavern MQ Map Chest",                             ("Chest",       0x09,  0x01, None,                 ("Ice Cavern",))),
    ("Ice Cavern MQ Compass Chest",                         ("Chest",       0x09,  0x00, None,                 ("Ice Cavern",))),
    ("Ice Cavern MQ Freestanding PoH",                      ("Collectable", 0x09,  0x01, None,                 ("Ice Cavern",))),
    ("Ice Cavern MQ Iron Boots Chest",                      ("Chest",       0x09,  0x02, None,                 ("Ice Cavern",))),
    ("Ice Cavern MQ GS Red Ice",                            ("GS Token",    0x09,  0x02, None,                 ("Ice Cavern", "Skulltulas",))),
    ("Ice Cavern MQ GS Ice Block",                          ("GS Token",    0x09,  0x04, None,                 ("Ice Cavern", "Skulltulas",))),
    ("Ice Cavern MQ GS Scarecrow",                          ("GS Token",    0x09,  0x01, None,                 ("Ice Cavern", "Skulltulas",))),

    # Gerudo Training Grounds vanilla
    ("Gerudo Training Grounds Lobby Left Chest",            ("Chest",       0x0B,  0x13, None,                 ("Gerudo Training Grounds",))),
    ("Gerudo Training Grounds Lobby Right Chest",           ("Chest",       0x0B,  0x07, None,                 ("Gerudo Training Grounds",))),
    ("Gerudo Training Grounds Stalfos Chest",               ("Chest",       0x0B,  0x00, None,                 ("Gerudo Training Grounds",))),
    ("Gerudo Training Grounds Before Heavy Block Chest",    ("Chest",       0x0B,  0x11, None,                 ("Gerudo Training Grounds",))),
    ("Gerudo Training Grounds Heavy Block First Chest",     ("Chest",       0x0B,  0x0F, None,                 ("Gerudo Training Grounds",))),
    ("Gerudo Training Grounds Heavy Block Second Chest",    ("Chest",       0x0B,  0x0E, None,                 ("Gerudo Training Grounds",))),
    ("Gerudo Training Grounds Heavy Block Third Chest",     ("Chest",       0x0B,  0x14, None,                 ("Gerudo Training Grounds",))),
    ("Gerudo Training Grounds Heavy Block Fourth Chest",    ("Chest",       0x0B,  0x02, None,                 ("Gerudo Training Grounds",))),
    ("Gerudo Training Grounds Eye Statue Chest",            ("Chest",       0x0B,  0x03, None,                 ("Gerudo Training Grounds",))),
    ("Gerudo Training Grounds Near Scarecrow Chest",        ("Chest",       0x0B,  0x04, None,                 ("Gerudo Training Grounds",))),
    ("Gerudo Training Grounds Hammer Room Clear Chest",     ("Chest",       0x0B,  0x12, None,                 ("Gerudo Training Grounds",))),
    ("Gerudo Training Grounds Hammer Room Switch Chest",    ("Chest",       0x0B,  0x10, None,                 ("Gerudo Training Grounds",))),
    ("Gerudo Training Grounds Freestanding Key",            ("Collectable", 0x0B,  0x01, None,                 ("Gerudo Training Grounds",))),
    ("Gerudo Training Grounds Maze Right Central Chest",    ("Chest",       0x0B,  0x05, None,                 ("Gerudo Training Grounds",))),
    ("Gerudo Training Grounds Maze Right Side Chest",       ("Chest",       0x0B,  0x08, None,                 ("Gerudo Training Grounds",))),
    ("Gerudo Training Grounds Underwater Silver Rupee Chest", ("Chest",     0x0B,  0x0D, None,                 ("Gerudo Training Grounds",))),
    ("Gerudo Training Grounds Beamos Chest",                ("Chest",       0x0B,  0x01, None,                 ("Gerudo Training Grounds",))),
    ("Gerudo Training Grounds Hidden Ceiling Chest",        ("Chest",       0x0B,  0x0B, None,                 ("Gerudo Training Grounds",))),
    ("Gerudo Training Grounds Maze Path First Chest",       ("Chest",       0x0B,  0x06, None,                 ("Gerudo Training Grounds",))),
    ("Gerudo Training Grounds Maze Path Second Chest",      ("Chest",       0x0B,  0x0A, None,                 ("Gerudo Training Grounds",))),
    ("Gerudo Training Grounds Maze Path Third Chest",       ("Chest",       0x0B,  0x09, None,                 ("Gerudo Training Grounds",))),
    ("Gerudo Training Grounds Maze Path Final Chest",       ("Chest",       0x0B,  0x0C, None,                 ("Gerudo Training Grounds",))),
    # Gerudo Training Grounds MQ                             
    ("Gerudo Training Grounds MQ Lobby Left Chest",         ("Chest",       0x0B,  0x13, None,                 ("Gerudo Training Grounds",))),
    ("Gerudo Training Grounds MQ Lobby Right Chest",        ("Chest",       0x0B,  0x07, None,                 ("Gerudo Training Grounds",))),
    ("Gerudo Training Grounds MQ First Iron Knuckle Chest", ("Chest",       0x0B,  0x00, None,                 ("Gerudo Training Grounds",))),
    ("Gerudo Training Grounds MQ Before Heavy Block Chest", ("Chest",       0x0B,  0x11, None,                 ("Gerudo Training Grounds",))),
    ("Gerudo Training Grounds MQ Heavy Block Chest",        ("Chest",       0x0B,  0x02, None,                 ("Gerudo Training Grounds",))),
    ("Gerudo Training Grounds MQ Eye Statue Chest",         ("Chest",       0x0B,  0x03, None,                 ("Gerudo Training Grounds",))),
    ("Gerudo Training Grounds MQ Ice Arrows Chest",         ("Chest",       0x0B,  0x04, None,                 ("Gerudo Training Grounds",))),
    ("Gerudo Training Grounds MQ Second Iron Knuckle Chest",("Chest",       0x0B,  0x12, None,                 ("Gerudo Training Grounds",))),
    ("Gerudo Training Grounds MQ Flame Circle Chest",       ("Chest",       0x0B,  0x0E, None,                 ("Gerudo Training Grounds",))),
    ("Gerudo Training Grounds MQ Maze Right Central Chest", ("Chest",       0x0B,  0x05, None,                 ("Gerudo Training Grounds",))),
    ("Gerudo Training Grounds MQ Maze Right Side Chest",    ("Chest",       0x0B,  0x08, None,                 ("Gerudo Training Grounds",))),
    ("Gerudo Training Grounds MQ Underwater Silver Rupee Chest", ("Chest",  0x0B,  0x0D, None,                 ("Gerudo Training Grounds",))),
    ("Gerudo Training Grounds MQ Dinolfos Chest",           ("Chest",       0x0B,  0x01, None,                 ("Gerudo Training Grounds",))),
    ("Gerudo Training Grounds MQ Hidden Ceiling Chest",     ("Chest",       0x0B,  0x0B, None,                 ("Gerudo Training Grounds",))),
    ("Gerudo Training Grounds MQ Maze Path First Chest",    ("Chest",       0x0B,  0x06, None,                 ("Gerudo Training Grounds",))),
    ("Gerudo Training Grounds MQ Maze Path Third Chest",    ("Chest",       0x0B,  0x09, None,                 ("Gerudo Training Grounds",))),
    ("Gerudo Training Grounds MQ Maze Path Second Chest",   ("Chest",       0x0B,  0x0A, None,                 ("Gerudo Training Grounds",))),

    # Ganon's Castle vanilla                                
    ("Ganons Castle Forest Trial Chest",                    ("Chest",       0x0D,  0x09, None,                 ("Ganon's Castle",))),
    ("Ganons Castle Water Trial Left Chest",                ("Chest",       0x0D,  0x07, None,                 ("Ganon's Castle",))),
    ("Ganons Castle Water Trial Right Chest",               ("Chest",       0x0D,  0x06, None,                 ("Ganon's Castle",))),
    ("Ganons Castle Shadow Trial Front Chest",              ("Chest",       0x0D,  0x08, None,                 ("Ganon's Castle",))),
    ("Ganons Castle Shadow Trial Golden Gauntlets Chest",   ("Chest",       0x0D,  0x05, None,                 ("Ganon's Castle",))),
    ("Ganons Castle Light Trial First Left Chest",          ("Chest",       0x0D,  0x0C, None,                 ("Ganon's Castle",))),
    ("Ganons Castle Light Trial Second Left Chest",         ("Chest",       0x0D,  0x0B, None,                 ("Ganon's Castle",))),
    ("Ganons Castle Light Trial Third Left Chest",          ("Chest",       0x0D,  0x0D, None,                 ("Ganon's Castle",))),
    ("Ganons Castle Light Trial First Right Chest",         ("Chest",       0x0D,  0x0E, None,                 ("Ganon's Castle",))),
    ("Ganons Castle Light Trial Second Right Chest",        ("Chest",       0x0D,  0x0A, None,                 ("Ganon's Castle",))),
    ("Ganons Castle Light Trial Third Right Chest",         ("Chest",       0x0D,  0x0F, None,                 ("Ganon's Castle",))),
    ("Ganons Castle Light Trial Invisible Enemies Chest",   ("Chest",       0x0D,  0x10, None,                 ("Ganon's Castle",))),
    ("Ganons Castle Light Trial Lullaby Chest",             ("Chest",       0x0D,  0x11, None,                 ("Ganon's Castle",))),
    ("Ganons Castle Spirit Trial Crystal Switch Chest",     ("Chest",       0x0D,  0x12, None,                 ("Ganon's Castle",))),
    ("Ganons Castle Spirit Trial Invisible Chest",          ("Chest",       0x0D,  0x14, None,                 ("Ganon's Castle",))),
    ("Ganons Castle Deku Scrub Left",                       ("RepeatNPC2",  0x0D,  0x3A, None,                 ("Ganon's Castle", "Deku Scrub",))),
    ("Ganons Castle Deku Scrub Center-Left",                ("RepeatNPC2",  0x0D,  0x37, None,                 ("Ganon's Castle", "Deku Scrub",))),
    ("Ganons Castle Deku Scrub Center-Right",               ("RepeatNPC2",  0x0D,  0x33, None,                 ("Ganon's Castle", "Deku Scrub",))),
    ("Ganons Castle Deku Scrub Right",                      ("RepeatNPC2",  0x0D,  0x39, None,                 ("Ganon's Castle", "Deku Scrub",))),
    # Ganon's Castle MQ
    ("Ganons Castle MQ Forest Trial Freestanding Key",      ("Collectable", 0x0D,  0x01, None,                 ("Ganon's Castle",))),
    ("Ganons Castle MQ Forest Trial Eye Switch Chest",      ("Chest",       0x0D,  0x02, None,                 ("Ganon's Castle",))),
    ("Ganons Castle MQ Forest Trial Frozen Eye Switch Chest", ("Chest",     0x0D,  0x03, None,                 ("Ganon's Castle",))),
    ("Ganons Castle MQ Water Trial Chest",                  ("Chest",       0x0D,  0x01, None,                 ("Ganon's Castle",))),
    ("Ganons Castle MQ Shadow Trial Bomb Flower Chest",     ("Chest",       0x0D,  0x00, None,                 ("Ganon's Castle",))),
    ("Ganons Castle MQ Shadow Trial Eye Switch Chest",      ("Chest",       0x0D,  0x05, None,                 ("Ganon's Castle",))),
    ("Ganons Castle MQ Light Trial Lullaby Chest",          ("Chest",       0x0D,  0x04, None,                 ("Ganon's Castle",))),
    ("Ganons Castle MQ Spirit Trial First Chest",           ("Chest",       0x0D,  0x0A, None,                 ("Ganon's Castle",))),
    ("Ganons Castle MQ Spirit Trial Invisible Chest",       ("Chest",       0x0D,  0x14, None,                 ("Ganon's Castle",))),
    ("Ganons Castle MQ Spirit Trial Sun Front Left Chest",  ("Chest",       0x0D,  0x09, None,                 ("Ganon's Castle",))),
    ("Ganons Castle MQ Spirit Trial Sun Back Left Chest",   ("Chest",       0x0D,  0x08, None,                 ("Ganon's Castle",))),
    ("Ganons Castle MQ Spirit Trial Sun Back Right Chest",  ("Chest",       0x0D,  0x07, None,                 ("Ganon's Castle",))),
    ("Ganons Castle MQ Spirit Trial Golden Gauntlets Chest",("Chest",       0x0D,  0x06, None,                 ("Ganon's Castle",))),
    ("Ganons Castle MQ Deku Scrub Left",                    ("RepeatNPC2",  0x0D,  0x3A, None,                 ("Ganon's Castle", "Deku Scrub",))),
    ("Ganons Castle MQ Deku Scrub Center-Left",             ("RepeatNPC2",  0x0D,  0x37, None,                 ("Ganon's Castle", "Deku Scrub",))),
    ("Ganons Castle MQ Deku Scrub Center",                  ("RepeatNPC2",  0x0D,  0x33, None,                 ("Ganon's Castle", "Deku Scrub",))),
    ("Ganons Castle MQ Deku Scrub Center-Right",            ("RepeatNPC2",  0x0D,  0x39, None,                 ("Ganon's Castle", "Deku Scrub",))),
    ("Ganons Castle MQ Deku Scrub Right",                   ("RepeatNPC2",  0x0D,  0x30, None,                 ("Ganon's Castle", "Deku Scrub",))),
    # Ganon's Castle shared
    ("Ganons Tower Boss Key Chest",                         ("Chest",       0x0A,  0x0B, None,                 ("Ganon's Castle",))),

    ## Events and Drops
    ("Pierre",                                          ("Event",       None,  None, None,                     None)),
    ("Deliver Rutos Letter",                            ("Event",       None,  None, None,                     None)),
    ("Master Sword Pedestal",                           ("Event",       None,  None, None,                     None)),
    ("Market Mask Shop Keaton Mask":                    ("Event",       None,  None, None,                     ("the Market", "Market",)),
    ("Market Mask Shop Skull Mask":                     ("Event",       None,  None, None,                     ("the Market", "Market",)),
    ("Market Mask Shop Spooky Mask":                    ("Event",       None,  None, None,                     ("the Market", "Market",)),
    ("Market Mask Shop Bunny Hood":                     ("Event",       None,  None, None,                     ("the Market", "Market",)),
    ("Market Mask Shop Zora Mask":                      ("Event",       None,  None, None,                     ("the Market", "Market",)),
    ("Market Mask Shop Goron Mask":                     ("Event",       None,  None, None,                     ("the Market", "Market",)),
    ("Market Mask Shop Gerudo Mask":                    ("Event",       None,  None, None,                     ("the Market", "Market",)),
    ("Market Mask Shop Mask of Truth":                  ("Event",       None,  None, None,                     ("the Market", "Market",)),

    ("Granny Blue Potion":                              ("Event",       0x4E,  None, None,                     ("Kakariko Village", "Kakariko",)), # RepeatNPC
    ("Market Poe Sale":                                 ("Event",       None,  None, None,                     ("the Market", "Hyrule Castle",)), # RepeatNPC
    ("Market Big Poe Sale":                             ("Event",       None,  None, None,                     ("the Market", "Hyrule Castle",)), # NPC
    ("Market Bug Sale":                                 ("Event",       None,  None, None,                     ("the Market", "Market",)), # RepeatNPC
    ("Market Fish Sale":                                ("Event",       None,  None, None,                     ("the Market", "Market",)), # RepeatNPC
    ("Market Blue Fire Sale":                           ("Event",       None,  None, None,                     ("the Market", "Market",)), # RepeatNPC
    ("Kak Bug Sale":                                    ("Event",       None,  None, None,                     ("Kakariko Village", "Kakariko",)), # RepeatNPC
    ("Kak Fish Sale":                                   ("Event",       None,  None, None,                     ("Kakariko Village", "Kakariko",)), # RepeatNPC
    ("Kak Blue Fire Sale":                              ("Event",       None,  None, None,                     ("Kakariko Village", "Kakariko",)), # RepeatNPC
    ("Kak Keaton Mask Sale":                            ("Event",       None,  None, None,                     ("Kakariko Village", "Kakariko",)), # NPC
    ("LW Skull Mask Sale":                              ("Event",       None,  None, None,                     ("the Lost Woods", "Forest",)), # NPC
    ("Graveyard Spooky Mask Sale":                      ("Event",       None,  None, None,                     ("the Graveyard", "Kakariko",)), # NPC
    ("HF Bunny Hood Sale":                              ("Event",       None,  None, None,                     ("Hyrule Field",)), # NPC

    ("Deku Baba Sticks",                                ("Drop",        None,  None, None,                     None)),
    ("Deku Baba Nuts",                                  ("Drop",        None,  None, None,                     None)),
    ("Stick Pot",                                       ("Drop",        None,  None, None,                     None)),
    ("Nut Pot",                                         ("Drop",        None,  None, None,                     None)),
    ("Nut Crate",                                       ("Drop",        None,  None, None,                     None)),
    ("Blue Fire",                                       ("Drop",        None,  None, None,                     None)),
    ("Lone Fish",                                       ("Drop",        None,  None, None,                     None)),
    ("Fish Group",                                      ("Drop",        None,  None, None,                     None)),
    ("Bug Rock",                                        ("Drop",        None,  None, None,                     None)),
    ("Bug Shrub",                                       ("Drop",        None,  None, None,                     None)),
    ("Wandering Bugs",                                  ("Drop",        None,  None, None,                     None)),
    ("Fairy Pot",                                       ("Drop",        None,  None, None,                     None)),
    ("Free Fairies",                                    ("Drop",        None,  None, None,                     None)),
    ("Wall Fairy",                                      ("Drop",        None,  None, None,                     None)),
    ("Butterfly Fairy",                                 ("Drop",        None,  None, None,                     None)),
    ("Gossip Stone Fairy",                              ("Drop",        None,  None, None,                     None)),
    ("Bean Plant Fairy",                                ("Drop",        None,  None, None,                     None)),
    ("Fairy Pond",                                      ("Drop",        None,  None, None,                     None)),
    ("Poe Kill",                                        ("Drop",        None,  None, None,                     None)),
    ("Big Poe Kill",                                    ("Drop",        None,  None, None,                     None)),

    ## Hints
    # These are not actual locations, but are filler spots used for hint reachability.
    # Hint location types must start with 'Hint'.
    ("DMC Gossip Stone",                                ("HintStone",   None,  None, None,                     None)),
    ("DMT Gossip Stone",                                ("HintStone",   None,  None, None,                     None)),
    ("Colossus Gossip Stone",                           ("HintStone",   None,  None, None,                     None)),
    ("Dodongos Cavern Gossip Stone",                    ("HintStone",   None,  None, None,                     None)),
    ("GV Gossip Stone",                                 ("HintStone",   None,  None, None,                     None)),
    ("GC Maze Gossip Stone",                            ("HintStone",   None,  None, None,                     None)),
    ("GC Medigoron Gossip Stone",                       ("HintStone",   None,  None, None,                     None)),
    ("Graveyard Gossip Stone",                          ("HintStone",   None,  None, None,                     None)),
    ("HC Malon Gossip Stone",                           ("HintStone",   None,  None, None,                     None)),
    ("HC Rock Wall Gossip Stone",                       ("HintStone",   None,  None, None,                     None)),
    ("HC Storms Grotto Gossip Stone",                   ("HintStone",   None,  None, None,                     None)),
    ("HF Cow Grotto Gossip Stone",                      ("HintStone",   None,  None, None,                     None)),
    ("KF Deku Tree Gossip Stone (Left)",                ("HintStone",   None,  None, None,                     None)),
    ("KF Deku Tree Gossip Stone (Right)",               ("HintStone",   None,  None, None,                     None)),
    ("KF Gossip Stone",                                 ("HintStone",   None,  None, None,                     None)),
    ("LH Lab Gossip Stone",                             ("HintStone",   None,  None, None,                     None)),
    ("LH Gossip Stone (Southeast)",                     ("HintStone",   None,  None, None,                     None)),
    ("LH Gossip Stone (Southwest)",                     ("HintStone",   None,  None, None,                     None)),
    ("LW Gossip Stone",                                 ("HintStone",   None,  None, None,                     None)),
    ("SFM Maze Gossip Stone (Lower)",                   ("HintStone",   None,  None, None,                     None)),
    ("SFM Maze Gossip Stone (Upper)",                   ("HintStone",   None,  None, None,                     None)),
    ("SFM Saria Gossip Stone",                          ("HintStone",   None,  None, None,                     None)),
    ("ToT Gossip Stone (Left)",                         ("HintStone",   None,  None, None,                     None)),
    ("ToT Gossip Stone (Left-Center)",                  ("HintStone",   None,  None, None,                     None)),
    ("ToT Gossip Stone (Right)",                        ("HintStone",   None,  None, None,                     None)),
    ("ToT Gossip Stone (Right-Center)",                 ("HintStone",   None,  None, None,                     None)),
    ("ZD Gossip Stone",                                 ("HintStone",   None,  None, None,                     None)),
    ("ZF Fairy Gossip Stone",                           ("HintStone",   None,  None, None,                     None)),
    ("ZF Jabu Gossip Stone",                            ("HintStone",   None,  None, None,                     None)),
    ("ZR Near Grottos Gossip Stone",                    ("HintStone",   None,  None, None,                     None)),
    ("ZR Near Domain Gossip Stone",                     ("HintStone",   None,  None, None,                     None)),

    ("HF Near Market Grotto Gossip Stone",              ("HintStone",   None,  None, None,                     None)),
    ("HF Southeast Grotto Gossip Stone",                ("HintStone",   None,  None, None,                     None)),
    ("HF Open Grotto Gossip Stone",                     ("HintStone",   None,  None, None,                     None)),
    ("Kak Open Grotto Gossip Stone",                    ("HintStone",   None,  None, None,                     None)),
    ("ZR Open Grotto Gossip Stone",                     ("HintStone",   None,  None, None,                     None)),
    ("KF Storms Grotto Gossip Stone",                   ("HintStone",   None,  None, None,                     None)),
    ("LW Near Shortcuts Grotto Gossip Stone",           ("HintStone",   None,  None, None,                     None)),
    ("DMT Storms Grotto Gossip Stone",                  ("HintStone",   None,  None, None,                     None)),
    ("DMC Upper Grotto Gossip Stone",                   ("HintStone",   None,  None, None,                     None)),

    ("Ganondorf Hint",                                  ("Hint",        None,  None, None,                     None)),
])

location_sort_order = {
    loc: i for i, loc in enumerate(location_table.keys())
}

# Business Scrub Details
business_scrubs = [
    # id   price  text   text replacement
    (0x30, 20,   0x10A0, ["Deku Nuts", "a \x05\x42mysterious item\x05\x40"]),
    (0x31, 15,   0x10A1, ["Deku Sticks", "a \x05\x42mysterious item\x05\x40"]),
    (0x3E, 10,   0x10A2, ["Piece of Heart", "\x05\x42mysterious item\x05\x40"]),
    (0x33, 40,   0x10CA, ["\x05\x41Deku Seeds", "a \x05\x42mysterious item"]),
    (0x34, 50,   0x10CB, ["\x41Deku Shield", "\x42mysterious item"]),
    (0x37, 40,   0x10CC, ["\x05\x41Bombs", "a \x05\x42mysterious item"]),
    (0x38, 00,   0x10CD, ["\x05\x41Arrows", "a \x05\x42mysterious item"]),  # unused
    (0x39, 40,   0x10CE, ["\x05\x41Red Potion", "\x05\x42mysterious item"]),
    (0x3A, 40,   0x10CF, ["Green Potion", "mysterious item"]),
    (0x77, 40,   0x10DC, ["enable you to pick up more\x01\x05\x41Deku Sticks", "sell you a \x05\x42mysterious item"]),
    (0x79, 40,   0x10DD, ["enable you to pick up more \x05\x41Deku\x01Nuts", "sell you a \x05\x42mysterious item"]),
]

dungeons = ('Deku Tree', 'Dodongo\'s Cavern', 'Jabu Jabu\'s Belly', 'Forest Temple', 'Fire Temple', 'Water Temple', 'Spirit Temple', 'Shadow Temple', 'Ice Cavern', 'Bottom of the Well', 'Gerudo Training Grounds', 'Ganon\'s Castle')
location_groups = {
    'Song': [name for (name, data) in location_table.items() if data[0] == 'Song'],
    'Chest': [name for (name, data) in location_table.items() if data[0] == 'Chest'],
    'Collectable': [name for (name, data) in location_table.items() if data[0] == 'Collectable'],
    'BossHeart': [name for (name, data) in location_table.items() if data[0] == 'BossHeart'],
    'CollectableLike': [name for (name, data) in location_table.items() if data[0] in ('Collectable', 'BossHeart', 'GS Token')],
    'CanSee': [name for (name, data) in location_table.items()
               if data[0] in ('Collectable', 'BossHeart', 'GS Token', 'Shop')
               # Treasure Box Shop, Bombchu Bowling, Hyrule Field (OoT), Lake Hylia (RL/FA)
               or data[0:1] in [['Chest', 0x10], ['NPC', 0x4B], ['NPC', 0x51], ['NPC', 0x57]]],
    'Dungeon': [name for (name, data) in location_table.items() if data[4] is not None and any(dungeon in data[4] for dungeon in dungeons)],
}


def location_is_viewable(loc_name, correct_chest_sizes):
    return correct_chest_sizes and loc_name in location_groups['Chest'] or loc_name in location_groups['CanSee']


# Function to run exactly once after after placing items in drop locations for each world
# Sets all Drop locations to a unique name in order to avoid name issues and to identify locations in the spoiler
def set_drop_location_names(world):
    for location in world.get_locations():
        if location.type == 'Drop':
            location.name = location.parent_region.name + " " + location.name
