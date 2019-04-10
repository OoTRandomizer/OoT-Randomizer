#Accept86 working_navi

from SaveContext import SaveContext
from Hints import get_raw_text, lineWrap        
from Utils import default_output_path
from Rom import Rom

import os, os.path
                    
import re

#s = 'a (45:45) b (65:40) ccc (blah$#)'
#re.sub('\s?\(.*?\)', '', s).strip() # 'a b ccc'  

class working_navi(Rom):
    
    WORKING_NAVI_RAM = None
    WORKING_NAVI_ROM = None
    WORKING_NAVI_DATA_GENERATED_LOOKUPTABLE_ROM = None
    WORKING_NAVI_DATA_GENERATED_TEXT_ROM = None  #length about 0x1000 hex - to 0x80501700
    WORKING_NAVI_CODE_CYCLICLOGIC_RAM = None
    WORKING_NAVI_CODE_TEXTLOADLOGIC_RAM = None
    
    
    
    def __init__(self, rom):
        self.WORKING_NAVI_RAM = rom.symRAM('WORKING_NAVI_GLOBALS') #0x80410000
        self.WORKING_NAVI_ROM = rom.sym('WORKING_NAVI_GLOBALS') #0x03490000
        self.WORKING_NAVI_DATA_GENERATED_LOOKUPTABLE_ROM = rom.sym('WORKING_NAVI_DATA_GENERATED_LOOKUPTABLE_SYM') #self.WORKING_NAVI_ROM + 0x40     #TBD from .json File?
        self.WORKING_NAVI_DATA_GENERATED_TEXT_ROM = rom.sym('WORKING_NAVI_DATA_GENERATED_TEXT_SYM') #self.WORKING_NAVI_ROM + 0x800    #length about 0x1000 hex - to 0x80501700
        self.WORKING_NAVI_CODE_CYCLICLOGIC_RAM = rom.symRAM('WORKING_NAVI_DATA_CODE') #self.WORKING_NAVI_RAM + 0x300
        self.WORKING_NAVI_CODE_TEXTLOADLOGIC_RAM = rom.symRAM('WORKING_NAVI_DATA_CODE2') #self.WORKING_NAVI_RAM + 0x600
    
    
    lastUpgradeIndexes = [0,0,0,0]
    
    def Reset(self):
        lastUpgradeIndexes = [0,0,0,0]
        
    

    def getBitOffsetIndex(self, mask):
        i=0;
        for i in range(0, 31):
            if( ((mask>>i)&1)!=0 ):
                break
            
        return i
    
    #def getMaskByBitOffsetIndex(self, bitoffset):
    #    mask = 1 << bitoffset
            
    #    return mask
    
    
    def OptimizeOffsetAndMask(self, array):
        ItemByteOffset = array[0]
        ItemBitOffset = 0 #array[1]
        ItemMask = array[2]
        ItemID = array[3]
        
        maskOffset = self.getBitOffsetIndex(ItemMask)
        maskOffset8Increment = int(maskOffset/8)*8
        
        
        ItemMask = (ItemMask >> maskOffset8Increment) & 0xFFFF
        ItemBitOffset += maskOffset8Increment
        
        
        return [ItemByteOffset,ItemBitOffset,ItemMask,ItemID]
    
    
    
    def getUpgradeBitmask(self, UpgradeIndex, address, name_no_brackets ):
        # Upgrades
        #'upgrades' : {
        #    'quiver'                 : Address(0x00A0, mask=0x00000007, max=3),
        #    'bomb_bag'               : Address(0x00A0, mask=0x00000038, max=3),
        #    'strength_upgrade'       : Address(0x00A0, mask=0x000001C0, max=3),
        #    'diving_upgrade'         : Address(0x00A0, mask=0x00000E00, max=2),
        #    'wallet'                 : Address(0x00A0, mask=0x00003000, max=3),
        #    'bullet_bag'             : Address(0x00A0, mask=0x0001C000, max=3),
        #    'stick_upgrade'          : Address(0x00A0, mask=0x000E0000, max=3),
        #    'nut_upgrade'            : Address(0x00A0, mask=0x00700000, max=3),
        #},
        
        #=> bitshiftcount with 0x80 flag -> 0x84, 0x88 0x8C
        #=> if Bigger than that got item
        #-do testing for all those upgrades
        #strength: goes 0=>0x40->0x80->0xC0, no bitencoding
        #scale: 0 => 0x200 => 0x400
        #hookshot: 0xFFFF => 0xFF0A => 0xFF0B
        #Wallet:  0=>0x1000 => 0x2000
        #Bottles:bitmask 2 bytes to high, 0xFFFFFFFF=> 0xFFFF16FF => 0xFFFF161B => 0xFFFF161B 0x1E
                #green potion drunk 0x16->0x14
                #these are the Item Ids
                                
                                
        ItemByteoffset =  address[0]-address[0]%4   #Accept86 sometimes its not 32bit alligned?
        #ItemBitoffset =  0 #int(address[1]) #this is just the bitoffset of the mask how far one has to shift it
        ItemMask = int(address[2])
        RealBitOffsetAndMask = self.getActualBitOffsetAndMask(address[0], ItemMask)      
        ItemCategory = str(address[3])
        
        
        #'Progressive Strength Upgrade'
        #Progressive Scale'
        #Progressive Wallet'
        #'Progressive Hookshot'
        NameTable = [['gorons_bracelet','silver_gauntlets','golden_gauntlets'],['silver_scale','golden_scale'],['adults_wallet','giants_wallet'],['hookshot','longshot']]
        
        ItemID = int(SaveContext.item_id_map[NameTable[UpgradeIndex][self.lastUpgradeIndexes[UpgradeIndex]]])
        self.lastUpgradeIndexes[UpgradeIndex]=self.lastUpgradeIndexes[UpgradeIndex]+1
        
        
        return self.OptimizeOffsetAndMask([ItemByteoffset,RealBitOffsetAndMask[0],RealBitOffsetAndMask[1],ItemID])
    
    

    def getActualBitOffsetAndMask(self, actualAddress, ItemMask):
        bitoffset = 0
        mask = ItemMask
        if True: #( ItemMask == 0xFFFFFFFF ):
            if((actualAddress%4)!=0):
                bitoffset = int((3-actualAddress%4)*8)        #its big endianess, %4 => move to right, magic offset 0xXXA => the real value is 2 Bytes to the right mask FFFF              
            mask = int( (ItemMask << bitoffset) & 0xFFFFFFFF ) 
        #so example fire arrows is the left Byte        
        return [bitoffset,mask]



    def getSaveFileAdressAndMaskByItem(self, Item, ItemType, save_context):
        
        address = -1
    
        name_no_brackets = re.sub('\s? \(.*?\)', '', Item.name).strip()
        name_no_brackets = name_no_brackets.replace('Buy ', '')
        address = save_context.give_item_addressAndMask(name_no_brackets)
      
        if address == -1:
            address = save_context.give_item_addressAndMask(name_no_brackets+'s')
            if address == -1:
                return -1
            
            
        ItemByteoffset =  address[0]-address[0]%4   #Accept86 sometimes its not 32bit alligned?
        ItemMask = int(address[2])
        RealBitOffsetAndMask = self.getActualBitOffsetAndMask(address[0], ItemMask)    
        ItemCategory = str(address[3])
        ItemID = 0
      
            
        if (ItemCategory == 'upgrades'):
            if(name_no_brackets=='Progressive Strength Upgrade'):
                return self.getUpgradeBitmask(0, address, name_no_brackets )
            elif(name_no_brackets=='Progressive Scale'):
                return self.getUpgradeBitmask(1, address, name_no_brackets )
            elif(name_no_brackets=='Progressive Wallet'):  
                return self.getUpgradeBitmask(2, address, name_no_brackets ) 

        elif((ItemCategory == 'item_slot') and (name_no_brackets=='Progressive Hookshot')):  
            return self.getUpgradeBitmask(3, address, name_no_brackets )   
          
        elif (ItemCategory == 'magic_acquired'):
            RealBitOffsetAndMask = [0, 0x00007F00] #FF has the Problem that 0x00 counts as aquired for magic, but for deku sticks its the other way around
        
        elif (ItemCategory == 'bottle_types'):
            if name_no_brackets in SaveContext.bottle_types:
                pass #TBD
        
        elif(ItemCategory != 'quest'): 
            if ( ItemMask != 0xFFFFFFFF ):       
                RealBitOffsetAndMask = [0, int((ItemMask << 16)&0xFFFF0000)]                        

        return self.OptimizeOffsetAndMask([ItemByteoffset,RealBitOffsetAndMask[0],RealBitOffsetAndMask[1],ItemID])
       
       
       

    
    def working_navi_patch_LookUpTableItem(self, ItemByteoffset, ItemBitoffset, ItemMask, ItemID, sphere_nr, CurLookupTablePointerB, rom):
        bArray = bytearray()
        #bArray.extend(map(ord, itemid))
        bArray = ItemByteoffset.to_bytes(2, 'big')
        rom.write_bytes(CurLookupTablePointerB, bArray)
        bArray = ItemBitoffset.to_bytes(1, 'big')
        rom.write_bytes(CurLookupTablePointerB+2, bArray)
        
        bArray = ItemMask.to_bytes(2, 'big')
        rom.write_bytes(CurLookupTablePointerB+4, bArray)
        
        bArray = ItemID.to_bytes(1, 'big')
        rom.write_bytes(CurLookupTablePointerB+6, bArray)
        
        bArray = int(sphere_nr).to_bytes(1, 'big')
        rom.write_bytes(CurLookupTablePointerB+7, bArray)
        
                            
                            
    def working_navi_patch_TextTableItem(self, navi_exact_locations, CurTextPointerBaseA, locationstringexact, locationstringvague, rom):
        bArray = bytearray()
        if navi_exact_locations:
            bArray.extend(map(ord, get_raw_text(lineWrap(locationstringexact)) )) 
        if not navi_exact_locations:
            bArray.extend(map(ord, get_raw_text(lineWrap(locationstringvague)) )) 
            
        CurTextPointerA = CurTextPointerBaseA
        rom.write_bytes(CurTextPointerA, [0x05, 0x44])
        CurTextPointerA += 2
        rom.write_bytes(CurTextPointerA, bArray)
        CurTextPointerA += len(bArray)
        rom.write_bytes(CurTextPointerA, [0x20, 0x05, 0x40, 0x02])
                    
                 
                 
    def working_navi_patch_internal(self, rom, world, spoiler, save_context, outfile):
        # Save Navi Texts in Rom
        CurTextPointerBaseA = self.WORKING_NAVI_DATA_GENERATED_TEXT_ROM
             
        self.working_navi_patch_TextTableItem(world.settings.working_navi_exact, CurTextPointerBaseA, "You are doing so well, no need to bother you", "You are doing so well, no need to bother you", rom)
        CurTextPointerBaseA += 0x3C
        
        # set LookUp Table for Navi Texts        
        CurLookupTablePointerB = self.WORKING_NAVI_DATA_GENERATED_LOOKUPTABLE_ROM

        self.Reset()            
                    
        for (sphere_nr, sphere) in spoiler.playthrough.items():
            for (location) in sphere:
                if str(location) != 'Links Pocket':
                    if str(location.item.name) != 'Gold Skulltula Token':
                        adressAndMask = -1
                        
                        adressAndMask = self.getSaveFileAdressAndMaskByItem(location.item,str(location.item.type),save_context)
                        if adressAndMask == -1:
                            breakpoint = 5;
                            continue
                        
                        ItemByteoffset =  adressAndMask[0]
                        ItemBitoffset =  adressAndMask[1] 
                        ItemMask = adressAndMask[2]
                        ItemID = adressAndMask[3]
                        
                        locationexact = 'check ' + str(location)
                        locationvague = locationexact
                        if(location.filter_tags != None):
                            locationvague = 'Maybe we find something in ' + str(location.filter_tags[0])
                    
                        #get all items with this str(location.item.name) in an array
                        #for the first one, normal location output
                        #for the others, combine the locations
                        #limit string length
                    
                        self.working_navi_patch_TextTableItem(world.settings.working_navi_exact, CurTextPointerBaseA, locationexact, locationvague, rom)
                        CurTextPointerBaseA += 0x3C
                        
                        self.working_navi_patch_LookUpTableItem(ItemByteoffset, ItemBitoffset, ItemMask, ItemID, sphere_nr, CurLookupTablePointerB, rom)
                        CurLookupTablePointerB += 8
                        
                        if world.settings.create_spoiler:
                            if(outfile != None):
                                outfile.write('\n %s: %s : %s' % (sphere_nr, location, location.item ) )
                
                     
        self.working_navi_patch_TextTableItem(world.settings.working_navi_exact, CurTextPointerBaseA, "We got everything we need, lets beat ganon", "We got everything we need, lets beat ganon", rom) 
        CurTextPointerBaseA += 0x3C             
          
        #end of LookUp Table
        rom.write_bytes(CurLookupTablePointerB, [0x00, 0x00, 0x00, 0xFF, 0x00, 0x00, 0x00, 0x00])  
                        
    
 
                     
                            
    
        
    def working_navi_patch(self, rom, world, spoiler, save_context, outfilebase):
        #working navi by accept86 wNavi
        if world.settings.working_navi:
            #write global variables
            asmglobal1_Timer_initvalue = int(0)
            asmglobal2_LookupTableIndex_initvalue = int(0)
            asmglobal3_MaxTimer_initvalue = int(0xd90 * int(world.settings.working_navi_delay) ) #0xd90 = 1min TBD over UI # Write Navi Delay Time to ROM TBD TBD
            asmglobal4_FlagForAsmHack_initvalue = int(0)
            
            glob1 = list(bytearray(asmglobal1_Timer_initvalue.to_bytes(4, 'big')))
            glob2 = list(bytearray(asmglobal2_LookupTableIndex_initvalue.to_bytes(4, 'big')))
            glob3 = list(bytearray(asmglobal3_MaxTimer_initvalue.to_bytes(4, 'big')))
            glob4 = list(bytearray(asmglobal4_FlagForAsmHack_initvalue.to_bytes(4, 'big')))
            byteArray = bytearray( glob1 + glob2 + glob3 + glob4 )
            
            rom.write_bytes(self.WORKING_NAVI_ROM, byteArray)
            
            
            #hook for TextLoad
            intAddress =  int((self.WORKING_NAVI_CODE_TEXTLOADLOGIC_RAM & 0x00FFFFFF)/4)
            byteArray = list(bytearray(intAddress.to_bytes(3, 'big')))
            byteArray = [0x0C] + byteArray
            rom.write_bytes(0xB52BDC, bytearray(byteArray)) #is a JAL was a jal to DMALoad Text before
            
            #hook for cyclic call
            intAddress =  int((self.WORKING_NAVI_CODE_CYCLICLOGIC_RAM & 0x00FFFFFF)/4)
            byteArray = list(bytearray(intAddress.to_bytes(3, 'big')))
            byteArray = [0x08] + byteArray
            rom.write_bytes(0xB12A94, bytearray(byteArray)) #is a J, was a jr before, cyclic hack jumps back to previous ret address
           
            
            spoiler_path = ""     
            if world.settings.create_spoiler: 
                output_dir = default_output_path(world.settings.output_dir)      
                spoiler_path = os.path.join(output_dir, '%s_WorkingNaviSpoiler.txt' % outfilebase)
                with open(spoiler_path, 'w') as outfile:
                        outfile.write('OoT Randomizer Working Navi\n\n')
                        outfile.write('\nPlaythrough:\n\n')
                        self.working_navi_patch_internal(rom, world, spoiler, save_context, outfile)
                        
            else:
                self.working_navi_patch_internal(rom, world, spoiler, save_context, None)          
            
     
        