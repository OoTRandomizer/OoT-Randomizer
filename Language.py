import importlib.util
import os
import ListE
from Utils import data_path as dataPath
def getLang(world, set, name=None):
    if world.settings.language_selection == "extra":
        Path = world.settings.lang_path
        dan = os.path.join(Path, "ListX.py")
        data = os.path.join(Path, "data")
        
        get = importlib.util.spec_from_file_location("ListX", dan)
        lang = importlib.util.module_from_spec(get)
        get.loader.exec_module(lang)

        if set == "items":
            if name is None:
                return lang.NEW_ITEMS_X
            else:
                return lang.NEW_ITEMS_X[name]
        elif set == "navi":
            if name is None:
                return lang.NAVI_X
            else:
                return lang.NAVI_X[name]
        elif set == "shop":
            if name is None:
                return lang.SHOP_X
            else:
                return lang.SHOP_X[name]
        elif set == "misc":
            if name is None:
                return lang.MISC_X
            else:
                return lang.MISC_X[name]
        elif set == "text":
            if name is None:
                return lang.textTableX
            else:
                return lang.textTableX[name]
        elif set == "special":
            if name is None:
                return lang.specialTableX
            else:
                return lang.specialTableX[name]
        elif set == "reward text":
            if name is None:
                return lang.reward_text_X
            else:
                return lang.reward_text_X[name]
        elif set == "reward list":
            if name is None:
                return lang.reward_list_X
            else:
                return lang.reward_list_X[name]
        elif set == "dungeon list":
            if name is None:
                return lang.dungeon_list_X
            else:
                return lang.dungeon_list_X[name]
        elif set == "hint":
            if name is None:
                return lang.hintTableX
            else:
                return lang.hintTableX[name]
        elif set == "trial":
            if name is None:
                return lang.trial_X
            else:
                return lang.trial_X[name]
        elif set == "goal":
            if name is None:
                return lang.goalTableX
            else:
                return lang.goalTableX[name]
        elif set == "return":
            if name is None:
                return lang.retX
            else:
                return lang.retX[name]
        elif set == "data":
            if name is None:
                return data
            else:
                x = os.path.join(data, name)
                return x
    elif world.settings.language_selection != "extra":
        lang = ListE
        if set == "items":
            if name is None:
                return lang.NEW_ITEMS_X
            else:
                return lang.NEW_ITEMS_X[name]
        elif set == "navi":
            if name is None:
                return lang.NAVI_X
            else:
                return lang.NAVI_X[name]
        elif set == "shop":
            if name is None:
                return lang.SHOP_X
            else:
                return lang.SHOP_X[name]
        elif set == "misc":
            if name is None:
                return lang.MISC_X
            else:
                return lang.MISC_X[name]
        elif set == "text":
            if name is None:
                return lang.textTableX
            else:
                return lang.textTableX[name]
        elif set == "special":
            if name is None:
                return lang.specialTableX
            else:
                return lang.specialTableX[name]
        elif set == "reward text":
            if name is None:
                return lang.reward_text_X
            else:
                return lang.reward_text_X[name]
        elif set == "reward list":
            if name is None:
                return lang.reward_list_X
            else:
                return lang.reward_list_X[name]
        elif set == "dungeon list":
            if name is None:
                return lang.dungeon_list_X
            else:
                return lang.dungeon_list_X[name]
        elif set == "hint":
            if name is None:
                return lang.hintTableX
            else:
                return lang.hintTableX[name]
        elif set == "goal":
            if name is None:
                return lang.goalTableX
            else:
                return lang.goalTableX[name]
        elif set == "trial":
            if name is None:
                return lang.trial_X
            else:
                return lang.trial_X[name]
        elif set == "return":
            if name is None:
                return lang.retX
            else:
                return lang.retX[name]
        elif set == "data":
            if name is None:
                return dataPath()
            else:
                return dataPath(name)

#   DataName:                               AddressStart        #AddressEnd  
dataList = {
    "title":                                0x01795300,         # 0x017AE300
    "continue_JP":                          0x00862000,         # 0x00862980
    "continue_EN":                          0x00862980,         # 0x00863300
    "IDTTitle_JP":                          0x00864000,         # 0x00864600
    "DDCTitle_JP":                          0x00864600,         # 0x00864C00
    "JJBTitle_JP":                          0x00864C00,         # 0x00865200
    "FoTTitle_JP":                          0x00865200,         # 0x00865800
    "FiTTitle_JP":                          0x00865800,         # 0x00865E00
    "WaTTitle_JP":                          0x00865E00,         # 0x00866400
    "SpTTitle_JP":                          0x00866400,         # 0x00866A00
    "ShTTitle_JP":                          0x00866A00,         # 0x00867000
    "BoWTitle_JP":                          0x00867000,         # 0x00867600
    "IcCTitle_JP":                          0x00867600,         # 0x00867C00
    "To_Equip_JP":                          0x00867C00,         # 0x00867F80
    "To_Decide_JP":                         0x00867F80,         # 0x00868380
    "To_Play_M_JP":                         0x00868380,         # 0x00868880
    "To_Select_I_JP":                       0x00868880,         # 0x00869080
    "To_Map_JP":                            0x00869080,         # 0x00869880
    "To_Quest_Stat_JP":                     0x00869880,         # 0x0086A080
    "To_Equip_JP":                          0x0086A080,         # 0x0086A880
    "Save_Text_JP":                         0x0086A880,         # 0x0086B200
    "Saved_Text_JP":                        0x0086B200,         # 0x0086BB80
    "Yes_JP":                               0x0086BB80,         # 0x0086BE80
    "No_JP":                                0x0086BE80,         # 0x0086C180
    "Cur_Pos_JP":                           0x0086C180,         # 0x0086C280
    "Equip_1,0_JP":                         0x0086C280,         # 0x0086CC80
    "Select_I_0,0_JP":                      0x0086CC80,         # 0x0086D680
    "Select_I_1,0_JP":                      0x0086D680,         # 0x0086E080
    "Select_I_2,0_JP":                      0x0086E080,         # 0x0086EA80
    "Map_1,0_JP":                           0x0086EA80,         # 0x0086F480
    "Quest_Stat_0,0_JP":                    0x0086F480,         # 0x0086FE80
    "Quest_Status_1,0_JP":                  0x0086FE80,         # 0x00870880
    "Quest_Status_2,0_JP":                  0x00870880,         # 0x00871280
    "Save_1,0_JP":                          0x00871280,         # 0x00872000
    "IDTTitle_EN":                          0x00872000,         # 0x00872600
    "DDCTitle_EN":                          0x00872600,         # 0x00872C00
    "JJBTitle_EN":                          0x00873C00,         # 0x00873200
    "FoTTitle_EN":                          0x00873200,         # 0x00873800
    "FiTTitle_EN":                          0x00873800,         # 0x00873E00
    "WaTTitle_EN":                          0x00873E00,         # 0x00874400
    "SpTTitle_EN":                          0x00874400,         # 0x00874A00
    "ShTTitle_EN":                          0x00874A00,         # 0x00875000
    "BoWTitle_EN":                          0x00875000,         # 0x00875600
    "IcCTitle_EN":                          0x00875600,         # 0x00875C00
    "To_Equip_EN":                          0x00875C00,         # 0x00875F80
    "To_Decide_EN":                         0x00875F80,         # 0x00876380
    "To_Play_M_EN":                         0x00876380,         # 0x00876880
    "To_Select_I_EN":                       0x00876880,         # 0x00877080
    "To_Map_EN":                            0x00877080,         # 0x00877880
    "To_Quest_Stat_EN":                     0x00877880,         # 0x00878080
    "To_Equip_EN":                          0x00878080,         # 0x00878880
    "Save_Text_EN":                         0x00878880,         # 0x00879200
    "Saved_Text_EN":                        0x00879200,         # 0x00879B80
    "Yes_EN":                               0x00879B80,         # 0x00879E80
    "No_EN":                                0x00879E80,         # 0x0087A180
    "Cur_Pos_EN":                           0x0087A180,         # 0x0087A280
    "Equip_1,0_EN":                         0x0087A280,         # 0x0087AC80
    "Select_I_0,0_EN":                      0x0087AC80,         # 0x0087B680
    "Select_I_1,0_EN":                      0x0087B680,         # 0x0087C080
    "Select_I_2,0_EN":                      0x0087C080,         # 0x0087CA80
    "Map_1,0_EN":                           0x0087CA80,         # 0x0087D480
    "Quest_Stat_0,0_EN":                    0x0087D480,         # 0x0087DE80
    "Quest_Status_1,0_EN":                  0x0087DE80,         # 0x0087E880
    "Quest_Status_2,0_EN":                  0x0087E880,         # 0x0087F280
    "Save_1,0_EN":                          0x0087F280,         # 0x00880000
    "Stick_JP":			            0x00880000, 	# 0x00880400
    "Nut_JP":			            0x00880400, 	# 0x00880800
    "Bomb_JP":			            0x00880800, 	# 0x00880C00
    "Bow_JP":			            0x00880C00, 	# 0x00881000
    "Fire_Arrow_JP":			    0x00881000, 	# 0x00881400
    "Din_Fire_JP":			    0x00881400, 	# 0x00881800
    "Slingshot_JP":			    0x00881800,     	# 0x00881C00
    "FOcarina_JP":			    0x00881C00,		# 0x00882000
    "TOcarina_JP":			    0x00882000,     	# 0x00882400
    "Bombchu_JP":			    0x00882400,     	# 0x00882800
    "Hookshot_JP":			    0x00882800,     	# 0x00882C00
    "Longshot_JP":			    0x00882C00,     	# 0x00883000
    "Ice_Arrow_JP":			    0x00883000,     	# 0x00883400
    "Farore_Wind_JP":			    0x00883400,     	# 0x00883800
    "Boomerang_JP":			    0x00883800,     	# 0x00883C00
    "LoTruth_JP":			    0x00883C00,     	# 0x00884000
    "Beans_JP":			            0x00884000,		# 0x00884400
    "Hammer_JP":			    0x00884400,		# 0x00884800
    "Light_Arrow_JP":			    0x00884800,     	# 0x00884C00
    "Nayru_Love_JP":			    0x00884C00,		# 0x00885000
    "Bottle_JP":			    0x00885000,		# 0x00885400
    "Red_Potion_JP":			    0x00885400,		# 0x00885800
    "Green_Potion_JP":			    0x00885800,		# 0x00885C00
    "Blue_Potion_JP":			    0x00885C00,		# 0x00886000
    "Fairy_JP":			            0x00886000,		# 0x00886400
    "Fish_JP":			            0x00886400,		# 0x00886800
    "Milk_JP":			            0x00886800,		# 0x00886C00
    "RLetter_JP":			    0x00886C00,		# 0x00887000
    "Blue_Fire_JP":			    0x00887000,		# 0x00887400
    "Bug_JP":			            0x00887400,		# 0x00887800
    "B_Poe_JP":			            0x00887800,		# 0x00887C00
    "Milk_H_JP":			    0x00887C00,		# 0x00888000
    "Poe_JP":			            0x00888000,		# 0x00888400
    "Weird_Egg_JP":			    0x00888400,		# 0x00888800
    "Cucco_JP":			            0x00888800,		# 0x00888C00
    "ZLetter_JP":			    0x00888C00,		# 0x00889000
    "Keaton_JP":			    0x00889000,		# 0x00889400
    "Skull_JP":			            0x00889400,		# 0x00889800
    "Spook_JP":			            0x00889800,		# 0x00889C00
    "Bunny_JP":			            0x00889C00,		# 0x0088A000
    "Goron_JP":			            0x0088A000,		# 0x0088A400
    "Zora_JP":			            0x0088A400,		# 0x0088A800
    "Gerudo_JP":			    0x0088A800, 	# 0x0088AC00
    "MoTruth_JP":			    0x0088AC00,     	# 0x0088B000
    "SOLD_OUT_JP":			    0x0088B000,		# 0x0088B400
    "Pocket_Egg_JP":			    0x0088B400,		# 0x0088B800
    "Pocket_Cucco_JP":			    0x0088B800,		# 0x0088BC00
    "Cojiro_JP":			    0x0088BC00,		# 0x0088C000
    "Mushroom_JP":			    0x0088C000,		# 0x0088C400
    "OPotion_JP":			    0x0088C400,		# 0x0088C800
    "Saw_JP":			            0x0088C800,		# 0x0088CC00
    "GoronSB_JP":			    0x0088CC00,		# 0x0088D000
    "Prescription_JP":			    0x0088D000,		# 0x0088D400
    "Frog_JP":			            0x0088D400,		# 0x0088D800
    "Eye_Drop_JP":			    0x0088D800,		# 0x0088DC00
    "Claim_JP":			            0x0088DC00,		# 0x0088EC00
    "KSword_JP":			    0x0088EC00,		# 0x0088F000
    "MSword_JP":			    0x0088F000,		# 0x0088F400
    "BKnife_JP":			    0x0088F400,		# 0x0088F800
    "DekuS_JP":			            0x0088F800,		# 0x0088FC00
    "HylianS_JP":			    0x0088FC00,		# 0x00890000
    "MirrorS_JP":			    0x00890000,		# 0x00890400
    "KTunic_JP":			    0x00890400,		# 0x00890800
    "GTunic_JP":			    0x00890800,		# 0x00890C00
    "ZTunic_JP":			    0x00890C00,		# 0x00891000
    "KBoots_JP":			    0x00891000,		# 0x00891400
    "IBoots_JP":			    0x00891400,		# 0x00891800
    "HBoots_JP":			    0x00891800,		# 0x00891C00
    "BuBag30_JP":			    0x00891C00,		# 0x00892000
    "BuBag40_JP":			    0x00892000,		# 0x00892400
    "BuBag50_JP":			    0x00892400,		# 0x00892800
    "Quiver30_JP":			    0x00892800,		# 0x00892C00
    "Quiver40_JP":			    0x00892C00,		# 0x00893000
    "Quiver50_JP":			    0x00893000,		# 0x00893400
    "BombBag20_JP":			    0x00893400,		# 0x00893800
    "BombBag30_JP":			    0x00893800,		# 0x00893C00
    "BombBag40_JP":			    0x00893C00,		# 0x00894000
    "GoronBracelet_JP":			    0x00894000,		# 0x00894400
    "SilverGauntlets_JP":		    0x00894400,		# 0x00894800
    "GoldenGauntlets_JP":	            0x00894800,		# 0x00894C00
    "SilverScale_JP":			    0x00894C00,		# 0x00895000
    "GoldenScale_JP":			    0x00895000,		# 0x00895400
    "GiantsKnife B_JP":			    0x00895400,		# 0x00895800
    "AdultsWallet_JP":			    0x00895800,		# 0x00895C00
    "GiantsWallet_JP":			    0x00895C00,		# 0x00896000
    "DekuSeeds_JP":			    0x00896000,		# 0x00896400
    "FishPole_JP":			    0x00896400,		# 0x00896800
    "MoF_JP":			            0x00896800,		# 0x00896C00
    "BoF_JP":			            0x00896C00,     	# 0x00897000
    "SoW_JP":			            0x00897000, 	# 0x00897400
    "RoS_JP":			            0x00897400, 	# 0x00897800
    "NoS_JP":			            0x00897800,     	# 0x00897C00
    "PoL_JP":			            0x00897C00,		# 0x00898000
    "ZeL_JP":			            0x00898000,		# 0x00898400
    "EpS_JP":			            0x00898400,		# 0x00898800
    "SaS_JP":			            0x00898800,		# 0x00898C00
    "SunS_JP":			            0x00898C00,		# 0x00899000
    "SoT_JP":			            0x00899000,		# 0x00899400
    "SoS_JP":			            0x00899400,		# 0x00899800
    "ForMedal_JP":			    0x00899800,		# 0x00899C00
    "FirMedal_JP":			    0x00899C00,		# 0x0089A000
    "WatMedal_JP":			    0x0089A000,		# 0x0089A400
    "SpiMedal_JP":			    0x0089A400,		# 0x0089A800
    "ShaMedal_JP":			    0x0089A800,		# 0x0089AC00
    "LigMedal_JP":			    0x0089AC00,		# 0x0089B000
    "Emerald_JP":			    0x0089B000,		# 0x0089B400
    "Ruby_JP":			            0x0089B400,		# 0x0089B800
    "Sapphire_JP":			    0x0089B800,		# 0x0089BC00
    "Agony_JP":			            0x0089BC00,		# 0x0089C000
    "Gerudo_Card_JP":			    0x0089C000,		# 0x0089C400
    "GS_JP":			            0x0089C400,		# 0x0089C800
    "HContainer_JP":			    0x0089C800,		# 0x0089D000
    "Boss_Key_JP":			    0x0089D000,		# 0x0089D400
    "Compass_JP":			    0x0089D400,		# 0x0089D800
    "Dungeon_Map_JP":			    0x0089D800,		# 0x0089E800
    "BSword_JP":			    0x0089E800,		# 0x0089EC00
    "Stick_EN":			            0x0089EC00,		# 0x0089F000
    "Nut_EN":			            0x0089F000,		# 0x0089F400
    "Bomb_EN":			            0x0089F400,		# 0x0089F800
    "Bow_EN":			            0x0089F800,		# 0x0089FC00
    "Fire_Arrow_EN":			    0x0089FC00,		# 0x008A0000
    "Din_Fire_EN":			    0x008A0000,		# 0x008A0400
    "Slingshot_EN":			    0x008A0400,		# 0x008A0800
    "FOcarina_EN":			    0x008A0800,		# 0x008A0C00
    "TOcarina_EN":			    0x008A0C00,		# 0x008A1000
    "Bombchu_EN":			    0x008A1000,		# 0x008A1400
    "Hookshot_EN":			    0x008A1400,		# 0x008A1800
    "Longshot_EN":			    0x008A1800,		# 0x008A1C00
    "Ice_Arrow_EN":			    0x008A1C00,		# 0x008A2000
    "Farore_Wind_EN":			    0x008A2000,		# 0x008A2400
    "Boomerang_EN":			    0x008A2400,		# 0x008A2800
    "LoTruth_EN":			    0x008A2800,		# 0x008A2C00
    "Beans_EN":			            0x008A2C00,		# 0x008A3000
    "Hammer_EN":			    0x008A3000,		# 0x008A3400
    "Light_Arrow_EN":			    0x008A3400,		# 0x008A3800
    "Nayru_Love_EN":			    0x008A3800,		# 0x008A3C00
    "Bottle_EN":			    0x008A3C00,		# 0x008A4000
    "Red_Potion_EN":			    0x008A4000,		# 0x008A4400
    "Green_Potion_EN":			    0x008A4400,		# 0x008A4800
    "Blue_Potion_EN":			    0x008A4800,		# 0x008A4C00
    "Fairy_EN":			            0x008A4C00,		# 0x008A5000
    "Fish_EN":			            0x008A5000,		# 0x008A5400
    "Milk_EN":			            0x008A5400,		# 0x008A5800
    "RLetter_EN":			    0x008A5800,		# 0x008A5C00
    "Blue_Fire_EN":			    0x008A5C00,		# 0x008A6000
    "Bug_EN":			            0x008A6000,		# 0x008A6400
    "B_Poe_EN":			            0x008A6400,		# 0x008A6800
    "Milk_H_EN":			    0x008A6800,		# 0x008A6C00
    "Poe_EN":			            0x008A6C00,		# 0x008A7000
    "Weird_Egg_EN":			    0x008A7000,		# 0x008A7400
    "Cucco_EN":			            0x008A7400,		# 0x008A7800
    "ZLetter_EN":			    0x008A7800,		# 0x008A7C00
    "Keaton_EN":			    0x008A7C00,		# 0x008A8000
    "Skull_EN":			            0x008A8000,		# 0x008A8400
    "Spook_EN":			            0x008A8400,		# 0x008A8800
    "Bunny_EN":			            0x008A8800,		# 0x008A8C00
    "Goron_EN":			            0x008A8C00,		# 0x008A9000
    "Zora_EN":			            0x008A9000,		# 0x008A9400
    "Gerudo_EN":			    0x008A9400,		# 0x008A9800
    "MoTruth_EN":			    0x008A9800,		# 0x008A9C00
    "SOLD_OUT_EN":			    0x008A9C00,		# 0x008AA000
    "Pocket_Egg_EN":			    0x008AA000,		# 0x008AA400
    "Pocket_Cucco_EN":			    0x008AA400,		# 0x008AA800
    "Cojiro_EN":			    0x008AA800,		# 0x008AAC00
    "Mushroom_EN":			    0x008AAC00,		# 0x008AB000
    "OPotion_EN":			    0x008AB000,		# 0x008AB400
    "Saw_EN":			            0x008AB400,		# 0x008AB800
    "GoronSB_EN":			    0x008AB800,		# 0x008ABC00
    "Prescription_EN":			    0x008ABC00,		# 0x008AC000
    "Frog_EN":			            0x008AC000,		# 0x008AC400
    "Eye_Drop_EN":			    0x008AC400,		# 0x008AC800
    "Claim_EN":			            0x008AC800,		# 0x008AD800
    "KSword_EN":			    0x008AD800,		# 0x008ADC00
    "MSword_EN":			    0x008ADC00,		# 0x008AE000
    "BKnife_EN":			    0x008AE000,		# 0x008AE400
    "DekuS_EN":			            0x008AE400,		# 0x008AE800
    "HylianS_EN":			    0x008AE800,		# 0x008AEC00
    "MirrorS_EN":			    0x008AEC00,		# 0x008AF000
    "KTunic_EN":			    0x008AF000,		# 0x008AF400
    "GTunic_EN":			    0x008AF400,		# 0x008AF800
    "ZTunic_EN":			    0x008AF800,		# 0x008AFC00
    "KBoots_EN":			    0x008AFC00,		# 0x008B0000
    "IBoots_EN":			    0x008B0000,		# 0x008B0400
    "HBoots_EN":			    0x008B0400,		# 0x008B0800
    "BuBag30_EN":			    0x008B0800,		# 0x008B0C00
    "BuBag40_EN":			    0x008B0C00,		# 0x008B1000
    "BuBag50_EN":			    0x008B1000,		# 0x008B1400
    "Quiver30_EN":			    0x008B1400,		# 0x008B1800
    "Quiver40_EN":			    0x008B1800,     	# 0x008B1C00
    "Quiver50_EN":			    0x008B1C00,		# 0x008B2000
    "BombBag20_EN":			    0x008B2000,     	# 0x008B2400
    "BombBag30_EN":			    0x008B2400,		# 0x008B2800
    "BombBag40_EN":			    0x008B2800,     	# 0x008B2C00
    "GoronBracelet_EN":			    0x008B2C00,		# 0x008B3000
    "SilverGauntlets_EN":		    0x008B3000,     	# 0x008B3400
    "GoldenGauntlets_EN":		    0x008B3400,		# 0x008B3800
    "SilverScale_EN":			    0x008B3800,     	# 0x008B3C00
    "GoldenScale_EN":			    0x008B3C00,		# 0x008B4000
    "GiantsKnife B_EN":			    0x008B4000,     	# 0x008B4400
    "AdultsWallet_EN":			    0x008B4400,		# 0x008B4800
    "GiantsWallet_EN":			    0x008B4800,     	# 0x008B4C00
    "DekuSeeds_EN":			    0x008B4C00,		# 0x008B5000
    "FishPole_EN":			    0x008B5000,		# 0x008B5400
    "MoF_EN":			            0x008B5400,		# 0x008B5800
    "BoF_EN":			            0x008B5800,		# 0x008B5C00
    "SoW_EN":			            0x008B5C00,		# 0x008B6000
    "RoS_EN":			            0x008B6000,		# 0x008B6400
    "NoS_EN":			            0x008B6400,		# 0x008B6800
    "PoL_EN":			            0x008B6800,		# 0x008B6C00
    "ZeL_EN":			            0x008B6C00,		# 0x008B7000
    "EpS_EN":			            0x008B7000,     	# 0x008B7400
    "SaS_EN":			            0x008B7400,		# 0x008B7800
    "SunS_EN":			            0x008B7800,     	# 0x008B7C00
    "SoT_EN":			            0x008B7C00,		# 0x008B8000
    "SoS_EN":			            0x008B8000,     	# 0x008B8400
    "ForMedal_EN":			    0x008B8400,		# 0x008B8800
    "FirMedal_EN":			    0x008B8800,     	# 0x008B8C00
    "WatMedal_EN":			    0x008B8C00,		# 0x008B9000
    "SpiMedal_EN":			    0x008B9000,		# 0x008B9400
    "ShaMedal_EN":			    0x008B9400,		# 0x008B9800
    "LigMedal_EN":			    0x008B9800,		# 0x008B9C00
    "Emerald_EN":			    0x008B9C00,		# 0x008BA000
    "Ruby_EN":			            0x008BA000,		# 0x008BA400
    "Sapphire_EN":			    0x008BA400,		# 0x008BA800
    "Agony_EN":			            0x008BA800,		# 0x008BAC00
    "Gerudo_Card_EN":			    0x008BAC00,		# 0x008BB000
    "GS_EN":			            0x008BB000,		# 0x008BB400
    "HContainer_EN":			    0x008BB400,		# 0x008BBC00
    "Boss_Key_EN":			    0x008BBC00,		# 0x008BC000
    "Compass_EN":			    0x008BC000,		# 0x008BC400
    "Dungeon_Map_EN":			    0x008BC400,		# 0x008BD400
    "BSword_EN":			    0x008BD400,         # 0x008BD800
    "Wasteland_JP":                         0x008BE000,         # 0x008BE400
    "Fortress_JP":                          0x008BE400,         # 0x008BE800
    "Valley_JP":                            0x008BE800,         # 0x008BEC00
    "Lakeside_JP":                          0x008BEC00,         # 0x008BF000
    "LLR_JP":                               0x008BF000,         # 0x008BF400
    "Market_JP":                            0x008BF400,         # 0x008BF800
    "Field_JP":                             0x008BF800,         # 0x008BFC00
    "Mountain_JP":                          0x008BFC00,         # 0x008C0000
    "Village_JP":                           0x008C0000,         # 0x008C0400
    "Woods_JP":                             0x008C0400,         # 0x008C0800
    "Forest_JP":                            0x008C0800,         # 0x008C0C00
    "Domain_JP":                            0x008C0C00,         # 0x008C1000
    "Wasteland_EN":                         0x008C1000,         # 0x008C1400
    "Fortress_EN":                          0x008C1400,         # 0x008C1800
    "Valley_EN":                            0x008C1800,         # 0x008C1C00
    "Lakeside_EN":                          0x008C1C00,         # 0x008C2000
    "LLR_EN":                               0x008C2000,         # 0x008C2400
    "Market_EN":                            0x008C2400,         # 0x008C2800
    "Field_EN":                             0x008C2800,         # 0x008C2C00
    "Mountain_EN":                          0x008C2C00,         # 0x008C3000
    "Village_EN":                           0x008C3000,         # 0x008C3400
    "Woods_EN":                             0x008C3400,         # 0x008C3800
    "Forest_EN":                            0x008C3800,         # 0x008C3C00
    "Domain_EN":                            0x008C3C00,         # 0x008E0000
    "Attack_JP":                            0x008E0000,         # 0x008E0180
    "Check_JP":                             0x008E0180,         # 0x008E0300
    "Enter_JP":                             0x008E0300,         # 0x008E0480
    "Return_JP":                            0x008E0480,         # 0x008E0600
    "Open_JP":                              0x008E0600,         # 0x008E0780
    "Jump_JP":                              0x008E0780,         # 0x008E0900
    "Decide_JP":                            0x008E0900,         # 0x008E0A80
    "Dive_JP":                              0x008E0A80,         # 0x008E0C00
    "Faster_JP":                            0x008E0C00,         # 0x008E0D80
    "Throw_JP":                             0x008E0D80,         # 0x008E0F00
    "Climb_JP":                             0x008E1080,         # 0x008E1200
    "Drop_JP":                              0x008E1200,         # 0x008E1380
    "Down_JP":                              0x008E1380,         # 0x008E1500
    "Save_JP":                              0x008E1500,         # 0x008E1680
    "Speak_JP":                             0x008E1680,         # 0x008E1800
    "Next_JP":                              0x008E1800,         # 0x008E1980
    "Grab_JP":                              0x008E1980,         # 0x008E1B00
    "Stop_JP":                              0x008E1B00,         # 0x008E1C80
    "PutAway_JP":                           0x008E1C80,         # 0x008E1E00
    "Reel_JP":                              0x008E1E00,         # 0x008E1F80
    "Attack_EN":                            0x008E2B80,         # 0x008E2D00
    "Check_EN":                             0x008E2D00,         # 0x008E2E80
    "Enter_EN":                             0x008E2E80,         # 0x008E3000
    "Return_EN":                            0x008E3000,         # 0x008E3180
    "Open_EN":                              0x008E3180,         # 0x008E3300
    "Jump_EN":                              0x008E3300,         # 0x008E3480
    "Decide_EN":                            0x008E3480,         # 0x008E3600
    "Dive_EN":                              0x008E3600,         # 0x008E3780
    "Faster_EN":                            0x008E3780,         # 0x008E3900
    "Throw_EN":                             0x008E3900,         # 0x008E3A80
    "Climb_EN":                             0x008E3C00,         # 0x008E3D80
    "Drop_EN":                              0x008E3D80,         # 0x008E3F00
    "Down_EN":                              0x008E3F00,         # 0x008E4080
    "Save_EN":                              0x008E4080,         # 0x008E4200
    "Speak_EN":                             0x008E4200,         # 0x008E4380
    "Next_EN":                              0x008E4380,         # 0x008E4500
    "Grab_EN":                              0x008E4500,         # 0x008E4680
    "Stop_EN":                              0x008E4680,         # 0x008E4800
    "PutAway_EN":                           0x008E4800,         # 0x008E4980
    "Reel_EN":                              0x008E4980,         # 0x008E4B00
}
