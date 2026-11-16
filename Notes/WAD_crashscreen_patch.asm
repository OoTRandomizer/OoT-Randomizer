# WiiVC crash draw and patches, for the Ocarina of Time Randomizer WAD 00000001.app
# powerpc-gekko-as.exe -a32 -mbig -mregnames -mgekko wiivc-crashdraw.asm
# ported from the Majora's Mask Randomizer patch
#=======================================================================
#Addr    - Free
#0x05F0 - 0xD0 xx common data
#0x06C8 - 0xF8 xx-- crashReport
#0x0810 - 0xB0 xxxx
#0x08F8 - 0xC8 xxxx
#0x09F8 - 0xC8 xx--
#0x0AF8 - 0xC8 xxx-
#0x0BF8 - 0xC8 xxxx
#0x0CF8 - 0xC8 xx--
#0x0DF8 - 0xC8 xxxx
#0x0EF8 - 0x2C8 xx-- drawchar and printVA
#0x11F8 - 0xC8 xx-- printStr
#0x12F8 - 0xC8 xx-- N64Regspage
#0x13F8 - 0xC8 xxx-
#0x1550 - 0x70 xxxx
#0x1630 - 0x90 xxxx
#0x1730 - 0x90 xxx-
#0x1830 - 0x90 xxxx
#0x18F8 - 0xC8 xxxx
#0x19F8 - 0x1C8 xxxx N64Stack
#0x1BF8 - 0xC8 xxxx
#0x1CF8 - 0x4C8 xx-- strings
#0x21F8 - 0xC8 xxx- pollController
#0x22F8 - 0xC8 x--- hooks
#0x23F8 - 0xC8 xxx- hooks
#
#=======================================================================

.set chunk0RAM, 0x4000
.set chunk0ROM, 0x0100
.set chunk1RAM, 0x7020
.set chunk1ROM, 0x25E0

.set chunk0offset, chunk0RAM - chunk0ROM
.set chunk1offset, chunk1RAM - chunk1ROM

.set ButtonA,     0x00000001
.set ButtonB,     0x00000002
.set ButtonX,     0x00000004
.set ButtonY,     0x00000008
.set ButtonStart, 0x00000020
.set ShoulderL,   0x00000080
.set ShoulderR,   0x00000100
.set ButtonZ,     0x00000600
.set CLeft,       0x00008000
.set CRight,      0x00010000
.set Cdown,       0x00020000
.set CUp,         0x00040000
.set DPadLeft,    0x00080000
.set DPadRight,   0x00100000
.set DpadDown,    0x00200000
.set DpadUp,      0x00400000

# systemClass {
# 0x10 = *cpu, 
# 0x18 = *ramclass(0x4=*ram), 
# 0x68 = *controllerheap?, (0xBC,0xCC = button bitfields)
# 0x1C = *romstuff?(0x20=*rom), 
# }

#for errorDisplayPrintMessage
#startUpStr {
#0x00 = *strStruct
#}
#strStruct {
#0x00 = word (hash?)
#0x04 = word (string count)
#0x08 = *string
#}

#.set FrameList, 0x00178320     #framebuffer pointers (+0x04)

#==========================================================
# OoT US sets
#==========================================================

.set memcpy, 0x00004338        #(*dest, *src, int size)
.set __fill_mem, 0x00004388    #(*dest, int fillbyte, int size)

.set cpuExecuteUpdate, 0x00032BB4
.set cpuExecuteCall, 0x00039DC0
.set cpuFindFunction, 0x0003DC68

.set updateControllerInput, 0x00062484 #(*controllerheap)

.set errorDisplayPrintMessage, 0x00063A64  #(**startUpStr string, int Y 78, ldarg, RGBA8* colour)
.set errorDisplayPrint, 0x00063B8C
.set errorDisplayShow, 0x00063E08

.set xlFileGet, 0x000801F4
.set PPCHalt, 0x000893F0 #JP = 000893E4
.set DCStoreRange, 0x0008B690  #(*dest, int size)
.set OSDumpContext, 0x0008BF74
.set UnhandledException, 0x0008C6E4
.set OSUEhookend, UnhandledException + 0x18
.set OSGetTime, 0x00093674
.set OSGetTick, 0x0009368C
.set GXAbortFrame, 0x0009FAC8
.set GXSetCullMode, 0x000A0614

.set __save_gpr, 0x000152E30   #(r14)-0x48
.set __restore_gpr, 0x00152E7C #(r14)-0x48

.set sStringDraw, 0x001746E8
.set WVCLoadLogoStrStruct, 0x1749A8 + 0x34

.set WVCLoadLogoStrPointer, 0x001746bc + 8  #set at load-time
.set WVCLoadLogoStrCount, 0x001746bc + 0x4
.set WVCLoadLogoStrVAarg, 0x001749A8 + 0x38

.set WadMainThreadAddr, 0x801DCD98

.set smallDataArea, 0x002647C0    #r13
.set systemClass, 0x0025D0E0      #r13 -0x76E0

.set outputFBptr, 0x0025D974      #r13 -0x6E4C current framebuffer scanout
.set outputFBptr0, 0x0025D978      #r13 -0x6E48 frame 0?
.set outputFBptr1, 0x0025D97C      #r13 -0x6E44 frame 1?

.set cpustructHigh, 0x0010        #for some cpu struct reads
.set loadUpStrCompare, 0x48A8


#==========================================================
# OoT JP sets
#==========================================================

#.set memcpy, 0x00004338        #(*dest, *src, int size)
#.set __fill_mem, 0x00004388    #(*dest, int fillbyte, int size)
#
#.set cpuExecuteUpdate, 0x00032B98
#.set cpuExecuteCall, 0x00039DA4
#.set cpuFindFunction, 0x0003DC4C
#
#.set updateControllerInput, 0x000623F4 #(*controllerheap)
#
#.set errorDisplayPrintMessage, 0x000639D4  #(**startUpStr string, int Y 78, ldarg, RGBA8* colour)
#.set errorDisplayPrint, 0x00063AFC
#.set errorDisplayShow, 0x00063D78
#
#.set xlFileGet, 0x000801E8
#.set PPCHalt, 0x000893E4
#.set DCStoreRange, 0x0008B684  #(*dest, int size)
#.set OSDumpContext, 0x0008BF68
#.set UnhandledException, 0x0008C6D8
#.set OSUEhookend, UnhandledException + 0x18
#.set OSGetTime, 0x00093668
#.set OSGetTick, 0x00093680
#.set GXAbortFrame, 0x0009FABC
#.set GXSetCullMode, 0x000A0608
#
#.set __save_gpr, 0x00152E24   #(r14)-0x48
#.set __restore_gpr, 0x00152E70 #(r14)-0x48
#
#.set sStringDraw, 0x001746E8 - 0x60
#.set WVCLoadLogoStrStruct, 0x001749A8 + 0x34 - 0x60
#
#.set WVCLoadLogoStrPointer, 0x001746bc + 8 - 0x60
#.set WVCLoadLogoStrCount, 0x001746bc + 0x4 - 0x60
#.set WVCLoadLogoStrVAarg, 0x001749A8 + 0x38 - 0x60
#
#.set WadMainThreadAddr, 0x801DCC98
#
#.set smallDataArea, 0x002647C0 - 0x100    #r13
#.set systemClass, 0x0025D0E0 - 0x100      #r13 -0x76E0
#
#.set outputFBptr, 0x0025D874      #r13 -0x6E4C current framebuffer scanout
#.set outputFBptr0, 0x0025D878      #r13 -0x6E48 frame 0?
#.set outputFBptr1, 0x0025D87C      #r13 -0x6E44 frame 1?
#
#.set cpustructHigh, 0x0001        #for some cpu struct reads
#.set loadUpStrCompare, 0x4848


#====================================================
.org 0x44F0 - chunk0offset      #0x05F0
faultctxt:
FBpointer: .long 0x90000820
N64Fontpointer: .long 0x00104C18 #105258 = US1.2
FBSizeX: .short 0x0500
FBSizeY: .short 0x03C0
XStart: .short 0x0058
XEnd: .short 0x04A4
YStart: .short 0x0030
YEnd: .short 0x037C
CursorX: .short 0x0058           #cursorX
CursorY: .short 0x0030           #cursorY
FontColorFG: .short 0xFF80           #YUVwhite
FontColorBG: .short 0x1F80           #YUVblack
FontPadding: .short 0x0000           #signed
ExceptionID: .short 0x0000
N64cpuPointer: .long 0x009F6D64   #gets overwritten
CrashSSR0: .long 0x00000000
CrashLR: .long 0x00000000
CrashDAR: .long 0x00000000
ControllerPollTime: .long 0x00
CrashNote0: .long 0x00
CrashNote1: .long 0x00
CrashThread: .long 0x00
N64Stackpointer: .long 0x00
Timer: .long 0x00
N64RAM: .long 0x80F64120
LastBadN64Inst: .long 0x00000000
CrashArgHeap: .long 0x00000000
CrashGPRBuffer: .long 0x00000000
CrashN64RegBuffer: .long 0x00000000
CrashN64StackBuffer: .long 0x00000000
CrashWiiStackBuffer: .long 0x00000000
CrashMiscBuffer: .long 0x00000000
CrashRAMViewBuffer: .long 0x00000000
MBLoaded: .long 0x00000000
CrashPageCurrent: .byte 0x00
CrashPage1Status: .byte 0x00 #signed
CrashPage2Status: .byte 0x00 #signed
CrashPage3Status: .byte 0x00 #signed
CrashPage4Status: .byte 0x00 #signed
CrashPage5Status: .byte 0x00 #signed
AcceptInput: .byte 0x00
CtxtEnd: .byte 0xFF
StartupTimer: .long 0x00
#.align 2

#=======================================
.org 0x45C8 - chunk0offset     #0x06C8
crashReport:
stwu sp, -0x20(sp)
mflr r0
stw r0, 0x24(sp)

bl GXAbortFrame - chunk0offset - $

lis r31, 0x8000

lwz r4, chunk0offset + CrashThread@l(r31)
cmpi 0, r4, 0
bne crashReportSetUpDone
lwz r3, -0x76E0(r13)  #gSystem
mr r4, r26            #thread
bl crashSaveGPR

crashReportSetUpDone:
lbz r4, chunk0offset + CrashPageCurrent@l(r31)
cmpi 0, r4, 1
stw r4, 0x08(sp)
blt crashReportSplash

bl printBGRec
addi r4, sp, 0x08
addi r3, r31, chunk0offset + strPressA@l
bl printStr

lbz r4, chunk0offset + CrashPageCurrent@l(r31)
cmpi 0, r4, 1
beq crashReportCheckPage1
cmpi 0, r4, 2
beq crashReportCheckPage2
cmpi 0, r4, 3
beq crashReportCheckPage3
cmpi 0, r4, 4
beq crashReportCheckPage4
cmpi 0, r4, 5
beq crashReportCheckPage5

crashReportSplash:
bl crashSplash
b crashReportSetUpDone

crashReportCheckPage1:

bl crashReportN64Rregs
b crashReportSetUpDone

crashReportCheckPage2:
bl crashReportN64Stack
b crashReportSetUpDone

crashReportCheckPage3:
bl crashReportWiiGPR
b crashReportSetUpDone

crashReportCheckPage4:
bl crashReportWiiStack
b crashReportSetUpDone

crashReportCheckPage5:
bl crashReportWiiMisc
b crashReportSetUpDone

bl PPCHalt - chunk0offset - $

lwz r0, 0x24(sp)
mtlr r0
addi sp, sp, 0x20
blr
#====================================================
.org 0x4710 - chunk0offset     #0x0810
printNewline: #()
lhz r4, chunk0offset + XStart@l(r31)
lhz r5, chunk0offset + CursorY@l(r31)
sth r4, chunk0offset + CursorX@l(r31)
addi r5, r5, 0x10
sth r5, chunk0offset + CursorY@l(r31)
blr
#=============================
printResetCursor: #()
lhz r3, chunk0offset + XStart@l(r31)
lhz r4, chunk0offset + YStart@l(r31)
sth r3, chunk0offset + CursorX@l(r31)
sth r4, chunk0offset + CursorY@l(r31)
blr
#====================================
printClearPad: #()
li r3, 0
#fall through to setpad
#=============================
printSetPad: #(half-signed)
sth r3, chunk0offset + FontPadding@l(r31)
blr
#=============================
printHex32: #()
li r4, 8
b printNibble
#==================
printHex16:
li r4, 4
slwi r3, r3, 16
b printNibble
#==================
printHex8:
li r4, 2
slwi r3, r3, 24
#fall through to printNibble
#==================
printNibble:      #dont directly call this
stwu sp, -0x10(sp)
mflr r0
stw r0, 0x14(sp)
stw r29, 0x0C(sp)
stw r28, 0x08(sp)

mr r29, r3
mr r28, r4

printNibble_loop:
srwi r3, r29, 28
bl drawChar
slwi r29, r29, 4
addi r28, r28, -1
cmpi 0, r28, 0
bgt 0, printNibble_loop

lwz r28, 0x08(sp)
lwz r29, 0x0C(sp)
lwz r0, 0x14(sp)
mtlr r0
addi sp, sp, 0x10
blr
#=============================
.org 0x47F8 - chunk0offset    #0x08F8
printBGRec: #()
stwu sp, -0x20(sp)
mflr r0
stw r0, 0x24(sp)

lhz r3, chunk0offset + FontColorBG@l(r31)
slwi r4, r3, 16
or r5, r3, r4

lwz r3, chunk0offset + FBpointer@l(r31)
addi r6, r3, 0x6E00
addi r6, r6, 0x6E50

li r4, 400                 #Ylines

CSRYloop:
li r3, 286                 #Xlines

CSRXloop:
stw r5, 0(r6)
addi r6, r6, 4
addi r3, r3, -1
cmpi 0, r3, 0
bgt CSRXloop


addi r4, r4, -1
addi r6, r6, 136
cmpi 0, r4, 0
bgt CSRYloop

bl printResetCursor
bl printClearPad

lwz r0, 0x24(sp)
mtlr r0
addi sp, sp, 0x20
blr
#====================================
flushScreen:
stwu sp, -0x10(sp)
mflr r0
stw r0, 0x14(sp)

lwz r3, chunk0offset + FBpointer@l(r31)
lis r4, 0x0009
ori r4, r4, 0x6000
bl DCStoreRange - chunk0offset - $

lwz r0, 0x14(sp)
mtlr r0
addi sp, sp, 0x10
blr
#====================================
crashReportSetArgBuffer: #(*frame)
lwz r5, -0x6E48(r13)
cmpw 0, r3, r5
bne crsab_setHeap
lwz r5, -0x6E44(r13)

crsab_setHeap:
stw r5, chunk0offset + CrashArgHeap@l(r31)
blr
#=============================
.org 0x48F8 - chunk0offset     #0x9F8
crashReportWiiGPR:
stwu sp, -0x10(sp)
mflr r0
stw r0, 0x14(sp)

lbz r4, chunk0offset + CrashPage3Status@l(r31)
extsb r6, r4
cmpi 0, r6, 0
bge processWiiGPR
blt noWiiGPR


processWiiGPR:
li r5, -1
stb r5, chunk0offset + CrashPage3Status@l(r31)

li r3, -2
bl printSetPad

lwz r4, chunk0offset + CrashGPRBuffer@l(r31)
addi r3, r31, chunk0offset + strWiiGPRPage@l
bl printStr
bl flushScreen

li r4, 1
stb r4, chunk0offset + CrashPage3Status@l(r31)
li r3, 12
b crashReportWiiGPRfinish

noWiiGPR:
addi r3, r31, chunk0offset + strWiiGPRBroke@l
li r4, 0
bl printStr
bl flushScreen
li r3, 6


crashReportWiiGPRfinish:
li r4, 1
bl crashTimer

li r3, 4
stb r3, chunk0offset + CrashPageCurrent@l(r31)

lwz r0, 0x14(sp)
mtlr r0
addi sp, sp, 0x10
blr
#============================
.org 0x49F8 - chunk0offset      #0x0AF8
crashTimer: #(int seconds, int drawToggle)
stwu sp, -0x20(sp)
mflr r0
stw r0, 0x24(sp)
stw r30, 0x08(sp)
stw r29, 0x0C(sp)

mr r30, r3
mr r29, r4

li r6, 0x0030
sth r6, chunk0offset + CursorY@l(r31)

crashTimerLoop:
li r5, 0x0424
sth r5, chunk0offset + CursorX@l(r31)    #set timer pos

cmpi 0, r29, 0
beq crashTimerSkipDraw

bl drawChar
bl flushScreen

crashTimerSkipDraw:

crashTimerCount:
bl OSGetTime - chunk0offset - $
slwi r3, r3, 10
srwi r4, r4, 22
or r3, r3, r4

bl PollController
cmpi 0, r4, 0
bne crashTimerExit

lwz r5, chunk0offset + Timer@l(r31)
srwi r3, r3, 4
cmp 0, r3, r5
ble crashTimerCount

stw r3, chunk0offset + Timer@l(r31)

addi r30, r30, -1
cmpi 0, r30, 0
ble crashTimerExit
mr r3, r30
b crashTimerLoop


crashTimerExit:

lwz r29, 0x0C(sp)
lwz r30, 0x08(sp)
lwz r0, 0x24(sp)
mtlr r0
addi sp, sp, 0x20
blr
#=======================================
.org 0x4AF8 - chunk0offset         #0x0BF8
crashSaveGPR: #(*gSystem, *thread)
stwu sp, -0x10(sp)
mflr r0
stw r0, 0x14(sp)

mr r30, r4
stw r4, chunk0offset + CrashThread@l(r31)
lwz r5, 0x0018(r3)
lwz r7, 0x0010(r3)
lwz r6, 0x0004(r5)
stw r7, chunk0offset + N64cpuPointer@l(r31)
stw r6, chunk0offset + N64RAM@l(r31)
lwz r3, -0x6FF4(r13)
stw r3, chunk0offset + FBpointer@l(r31)

bl crashReportSetArgBuffer

mfspr r6, dar
lwz r4, 0x0198(r30) #SRR0
lwz r5, 0x0084(r30) #LR
stw r6, chunk0offset + CrashDAR@l(r31)
stw r4, chunk0offset + CrashSSR0@l(r31)
stw r5, chunk0offset + CrashLR@l(r31)

bl checkSetN64Stack

lwz r3, chunk0offset + CrashArgHeap@l(r31)
li r4, 0
li r5, 0x5000
bl __fill_mem - chunk0offset - $

lwz r11, chunk0offset + CrashArgHeap@l(r31)
li r10, 4
stw r30, 0x00(r11)
addi r30, r30, -4

#saving the Wii GPRs here in case another crash occurs and changes the saved values

gprLoop:
lwzx r6, r10, r30
stwx r6, r10, r11
addi r10, r10, 4
cmpi 0, r10, 32*4
blt gprLoop

lwz r4, chunk0offset + CrashSSR0@l(r31)
lwz r5, chunk0offset + CrashLR@l(r31)
lwz r6, chunk0offset + CrashDAR@l(r31)

stw r4, 0x84(r11)
stw r5, 0x88(r11)
stw r6, 0x8C(r11)

stw r11, chunk0offset + CrashGPRBuffer@l(r31)
addi r30, r11, 0x90
stw r30, chunk0offset + CrashArgHeap@l(r31)

#WiiGPRPage size 0x90
lwz r0, 0x14(sp)
mtlr r0
addi sp, sp, 0x10
blr
#=======================================
.org 0x4BF8 - chunk0offset         #0x0CF8
crashSplash:
stwu sp, -0x10(sp)
mflr r0
stw r0, 0x14(sp)

li r5, 0x01C8
li r4, 0x0080
sth r5, chunk0offset + XStart@l(r31)
sth r4, chunk0offset + YStart@l(r31)
bl printResetCursor

addi r3, r31, chunk0offset + strCrashSplash@l
li r4, 0
bl printStr

bl flushScreen

li r5, 0x0058
li r4, 0x0030
sth r5, chunk0offset + XStart@l(r31)
sth r4, chunk0offset + YStart@l(r31)
bl printResetCursor

li r3, 4
li r4, 0
bl crashTimer

li r5, 1
stb r5, chunk0offset + CrashPageCurrent@l(r31)

li r3, 1
stb r3, chunk0offset + AcceptInput@l(r31)

lwz r0, 0x14(sp)
mtlr r0
addi sp, sp, 0x10
blr
#=====================================
.org 0x4CF8 - chunk0offset         #0x0DF8
N64RegArgs:
#CrashN64RegBuffer
lwz r11, chunk0offset + CrashArgHeap@l(r31)

lhz r3, chunk0offset + ExceptionID@l(r31)
lwz r4, chunk0offset + CrashThread@l(r31)
lwz r5, chunk0offset + CrashSSR0@l(r31)
lwz r6, chunk0offset + CrashLR@l(r31)
lwz r7, chunk0offset + CrashDAR@l(r31)

stw r11, chunk0offset + CrashN64RegBuffer@l(r31)
stw r3, 0x00(r11)
stw r4, 0x04(r11)
stw r5, 0x08(r11)
stw r6, 0x0C(r11)

lwz r10, chunk0offset + N64cpuPointer@l(r31)
stw r7, 0x10(r11)
lwz r3, 0(r10)     #status
lwz r4, 0x20(r10)  #last function jumped
lwz r5, 0x30(r10)  #last RA set

stw r3, 0x14(r11)
stw r4, 0x18(r11)
stw r5, 0x1C(r11)

li r7, 0
addi r8, r10, 0x54  #cpu
addi r9, r11, 0x20  #argbuffer

N64RegLoop:
lwz r3, 0(r8)
stw r3, 0(r9)
addi r7, r7, 1
addi r8, r8, 0x08
addi r9, r9, 0x04
cmpi 0, r7, 31
blt N64RegLoop

lwz r6, 0x2C(r10)  #node
lwz r3, 0x04(r6)   #ppc addr
lwz r4, 0x10(r6)   #n64 start
lwz r5, 0x14(r6)   #n64 end

stw r6, 0x9C(r11)
stw r3, 0xA0(r11)
stw r4, 0xA4(r11)
stw r5, 0xA8(r11)

lwz r3, 0x24(r6)
lwz r4, 0x2C(r6)

addi r8, r11, 0xB4

stw r3, 0xAC(r11)
stw r4, 0xB0(r11)

stw r8, chunk0offset + CrashArgHeap@l(r31)

blr
#=====================================
.org 0x4DF8 - chunk0offset     #0x0EF8
drawChar: #(char)
stwu sp, -0x30(sp)
mflr r0
stw r0, 0x34(sp)

addi r11, sp, 0x30
bl __save_gpr + 0x28 - chunk0offset - $

lwz r0, chunk0offset + FBpointer@l(r31)
lhz r4, chunk0offset + CursorX@l(r31)
lhz r5, chunk0offset + CursorY@l(r31)
add r0, r4, r0
mulli r5, r5, 1280       #cursor Y x framebufferX size for Y position
nop
add r30, r5, r0          #framebuffer target for tile


lwz r11, chunk0offset + N64Fontpointer@l(r31)
lwz r6, chunk0offset + N64RAM@l(r31)
andi. r9, r3, 0x0004
add r11, r11, r6
add r11, r9, r11         #add shift
andi. r5, r3, 0x00FF
srwi r9, r5, 3           #tile >>3
slwi r4, r9, 6           #<<6
add r29, r4, r11         #final tilepointer


andi. r0, r3, 0x0003     #mask amount
li r4, 1
slw r5, r4, r0
slwi r28, r5, 28          #final tile mask

lhz r27, chunk0offset + FontColorFG@l(r31)
lhz r26, chunk0offset + FontColorBG@l(r31)
li r25, 0x0008           #outloop count

mr r7, r30               #work framebuffer target

drawChar_outerloopstart:
lwz r8, 0x0000(r29)      #tileword
mr r6, r28               #work mask
li r24, 0x0008           #inloop count

drawChar_innerloopstart:
and r0, r8, r6
cmpi 0, r0, 0
beq 0, drawChar_drawblack
drawChar_drawwhite:
sth r27, 0(r7)
sth r27, 2(r7)
sth r27, 1280(r7)
sth r27, 1282(r7)
b drawChar_afterdraw

drawChar_drawblack:
sth r26, 0(r7)
sth r26, 2(r7)
sth r26, 1280(r7)
sth r26, 1282(r7)

drawChar_afterdraw:
srwi r6, r6, 4           #shift mask
addi r24, r24, -1        #decrement inloop
addi r7, r7, 0x0004      #advance workfbX
cmpi 0, r24, 0
bgt drawChar_innerloopstart

addi r25, r25, -1        #decrement outloop
addi r29, r29, 0x0008    #advance tile pointer
addi r30, r30, 2560        #advance framebuffer line pointer
mr r7, r30
cmpi 0, r25, 0
bgt drawChar_outerloopstart

lhz r4, chunk0offset + CursorX@l(r31)
lha r6, chunk0offset + FontPadding@l(r31)
addi r5, r4, 0x0020
add r5, r5, r6
sth r5, chunk0offset + CursorX@l(r31)      #advance cursor X

addi r11, sp, 0x30
bl __restore_gpr + 0x28 - chunk0offset - $

lwz r0, 0x34(sp)
mtlr r0
addi sp, sp, 0x30
blr

#====================================
printVA: #(argchar, *argarray, int argcount)
stwu sp, -0x30(sp)
mflr r0
stw r0, 0x34(sp)

cmpi 0, r3, 0x78 # x
beq printVA_hex

cmpi 0, r3, 0x6C # l
beq printVA_hex

cmpi 0, r3, 0x68 # h
beq printVA_half

cmpi 0, r3, 0x62 # b
beq printVA_byte

cmpi 0, r3, 0x73 # s
beq printVA_str

cmpi 0, r3, 0x70 # p
beq printVA_pad

cmpi 0, r3, 0x25 # %
bne printVA_finish
bl drawChar
b printVA_finish

printVA_pad:
cmpi 0, r4, 0
beq printVA_finish
slwi r6, r5, 2
lwzx r3, r4, r6
bl printSetPad
b printVA_finish

printVA_hex:
cmpi 0, r4, 0
beq printVA_finish
slwi r6, r5, 2
lwzx r3, r4, r6
bl printHex32
b printVA_finish

printVA_half:
cmpi 0, r4, 0
beq printVA_finish
slwi r6, r5, 2
lwzx r3, r4, r6
bl printHex16
b printVA_finish

printVA_byte:
cmpi 0, r4, 0
beq printVA_finish
slwi r6, r5, 2
lwzx r3, r4, r6
bl printHex8
b printVA_finish

printVA_str:
cmpi 0, r4, 0
beq printVA_finish
slwi r6, r5, 2
lwzx r3, r4, r6
li r4, 0
bl printStr

printVA_finish:
lwz r0, 0x34(sp)
mtlr r0
addi sp, sp, 0x30
blr


#====================================
.org 0x50F8 - chunk0offset #0x11F8
printStr: #(*str, *argarray)
stwu sp, -0x30(sp)
mflr r0
stw r0, 0x34(sp)

addi r11, sp, 0x30
bl __save_gpr + 0x34 - chunk0offset - $

mr r30, r3
mr r29, r4
li r28, 0    #arg incrementer

printStr_loop:
lbz r3, 0(r30)
cmpi 0, r3, 0
beq printStr_finish

cmpi 0, r3, 0x0A      #newLine byte
beq printStr_newLine

cmpi 0, r3, 0x25     # % byte
bne printStr_char

lbz r3, 0x01(r30)
mr r4, r29
mr r5, r28
bl printVA
addi r30, r30, 1
addi r28, r28, 1
b printStr_increment

printStr_char:
bl drawChar
b printStr_increment


printStr_newLine:
bl printNewline


printStr_increment:
addi r30, r30, 1
b printStr_loop

printStr_finish:

addi r11, sp, 0x30
bl __restore_gpr + 0x34 - chunk0offset - $

lwz r0, 0x34(sp)
mtlr r0
addi sp, sp, 0x30
blr
#=====================================
.org 0x51F8 - chunk0offset #0x12F8
crashReportN64Rregs:
stwu sp, -0x10(sp)
mflr r0
stw r0, 0x14(sp)

lbz r4, chunk0offset + CrashPage1Status@l(r31)
extsb r6, r4
cmpi 0, r6, 0
blt N64RegsBroken
bgt N64RegsPrint

li r5, -1
stb r5, chunk0offset + CrashPage1Status@l(r31)
bl N64RegArgs

N64RegsPrint:
li r3, -2
bl printSetPad
lwz r4, chunk0offset + CrashN64RegBuffer@l(r31)
addi r3, r31, chunk0offset + strN64RegistersPage@l
bl printStr
bl flushScreen
li r5, 1
stb r5, chunk0offset + CrashPage1Status@l(r31)
li r3, 12
b N64Regsfinish

N64RegsBroken:
addi r3, r31, chunk0offset + strN64RegisterBroke@l
li r4, 0
bl printStr
bl flushScreen
li r3, 6

N64Regsfinish:
li r4, 1
bl crashTimer
li r5, 2
stb r5, chunk0offset + CrashPageCurrent@l(r31)

lwz r0, 0x14(sp)
mtlr r0
addi sp, sp, 0x10
blr
#=======================================
.org 0x52F8 - chunk0offset #0x13F8
crashWiiStack:
stwu sp, -0x20(sp)
mflr r0
stw r0, 0x24(sp)
stw r30, 0x08(sp)
stw r29, 0x0C(sp)

addi r3, r31, chunk0offset + strWiiStack@l
li r4, 0
bl printStr

lwz r5, chunk0offset + CrashGPRBuffer@l(r31)
li r29, 0
lwz r30, 0x08(r5)
#lwz r30, chunk0offset + CrashThread@l(r31)
li r29, 0

crashWiiStackLoop:
mr r3, r30
bl printHex32
li r3, 0x20
bl drawChar

lwz r3, 0x00(r30)
bl printHex32
li r3, 0x20
bl drawChar

lwz r3, 0x04(r30)
bl printHex32
bl printNewline

lwz r5, 0x00(r30)
li r4, -1
cmpw r5, r4
beq crashWiiStackfinish
mr r30, r5
addi r29, r29, 1
cmpi 0, r29, 13
blt crashWiiStackLoop


crashWiiStackfinish:
lwz r29, 0x0C(sp)
lwz r30, 0x08(sp)
lwz r0, 0x24(sp)
mtlr r0
addi sp, sp, 0x20
blr
#=====================================
.org 0x5450 - chunk0offset #0x1550
crashReportWiiStack:
stwu sp, -0x10(sp)
mflr r0
stw r0, 0x14(sp)

lbz r4, chunk0offset + CrashPage4Status@l(r31)
extsb r6, r4
cmpi 0, r6, 0
blt WiiStackBroken

li r5, -1
stb r5, chunk0offset + CrashPage4Status@l(r31)
bl crashWiiStack
li r5, 1
stb r5, chunk0offset + CrashPage4Status@l(r31)
li r3, 12
b WiiStackfinish

WiiStackBroken:
addi r3, r31, chunk0offset + strWiiStackBroke@l
li r4, 0
bl printStr
bl flushScreen
li r3, 6

WiiStackfinish:
li r4, 1
bl crashTimer

li r3, 5
stb r3, chunk0offset + CrashPageCurrent@l(r31)

lwz r0, 0x14(sp)
mtlr r0
addi sp, sp, 0x10
blr


#=======================================
.org 0x5530 - chunk0offset #0x1630
crashReportN64Stack:
stwu sp, -0x10(sp)
mflr r0
stw r0, 0x14(sp)

lbz r4, chunk0offset + CrashPage2Status@l(r31)
extsb r6, r4
cmpi 0, r6, 0
blt N64StackBroken

li r5, -1
stb r5, chunk0offset + CrashPage2Status@l(r31)
bl crashN64Stack
li r5, 1
stb r5, chunk0offset + CrashPage2Status@l(r31)
li r3, 12
b N64Stackfinish

N64StackBroken:
addi r3, r31, chunk0offset + strN64StackBroke@l
li r4, 0
bl printStr
bl flushScreen
li r3, 6

N64Stackfinish:
li r4, 1
bl crashTimer
li r5, 3
stb r5, chunk0offset + CrashPageCurrent@l(r31)

lwz r0, 0x14(sp)
mtlr r0
addi sp, sp, 0x10
blr
#=======================================
.org 0x5630 - chunk0offset #0x1730
checkSetN64Stack: #() return int N64stack
lwz r4, chunk0offset + CrashSSR0@l(r31)
lwz r5, chunk0offset + N64cpuPointer@l(r31)
lis r6, 0x801D
ori r6, r6, 0xCD98      #the main thread
cmp 0, r4, r5
ble CNSstackFromCPU

lwz r3, 0x7C(r6)
b CNSsetStack

CNSstackFromCPU:
lwz r3, 0x0134(r5)

CNSsetStack:
stw r3, chunk0offset + N64Stackpointer@l(r31)

blr
#=======================================
getN64TraceStart:#() return int N64addr
lwz r7, chunk0offset + N64cpuPointer@l(r31)
lwz r6, 0x002C(r7)      #get recompnode
lwz r3, 0x0030(r7)      #get RA
lwz r4, 0x0010(r6)       #nodestartaddr
lwz r5, 0x0014(r6)       #nodeendaddr
cmp 0, r3, r4          #cmp cpuRA, nodestart
blt GNTSusefunc
cmp 0, r3, r5          #cmp cpuRA, nodeEnd
blt GNTSfinish

GNTSusefunc:
lwz r3, 0x0020(r7)      #get cpu start

GNTSfinish:
blr
#=======================================
.org 0x5730 - chunk0offset #0x1830 CHECK
getN64RAfromrecomp: #(*ppcHeapAddr) return N64Addr or zero
lwz r5, chunk0offset + N64cpuPointer@l(r31)
addis r6, r5, cpustructHigh    #cpu's aidevice differs between US and JP
lwz r4, 0x0F60(r6)      #recompheapstart
cmp 0, r3, r4
blt GNRFRreturnzero
lwz r5, chunk0offset + N64RAM@l(r31)
cmp 0, r3, r5
bgt GNRFRreturnzero
andi. r6, r3, 0x0003
cmpi 0, r6, 0
bne GNRFRreturnzero


GNRFRoriscan:
lwz r5, 0(r3)
srwi r6, r5, 16
cmpi 0, r6, 0x60E7    #is ori r7 r7?
addi r3, r3, -4
bne GNRFRoriscan
andi. r7, r5, 0xFFFF

GNRFRlisscan:
lwz r5, 0(r3)
srwi r6, r5, 16
cmpi 0, r6, 0x3CE0    #is lis r7?
addi r3, r3, -4
bne GNRFRlisscan
slwi r8, r5, 16

or r3, r7, r8
cmpw 0, r3, r31
addis r4, r31, 0x0080
blt GNRFRreturnzero
cmpw 0, r3, r4
bge GNRFRreturnzero
andi. r6, r3, 0x0003
cmpi 0, r6, 0
bne GNRFRreturnzero

b GNRFRfinish

GNRFRreturnzero:
li r3, 0

GNRFRfinish:
blr
#=======================================
.org 0x57F8 - chunk0offset #0x18F8
N64StackValidAddr: #(unused, int n64Addr) return true/false, N64Addr
addis r5, r31, 0x0080
cmpw 0, r4, r31
blt N64SVAreturnZero
cmpw 0, r4, r5
bge N64SVAreturnZero

andi. r6, r4, 0x0003
cmpi 0, r6, 0
bne N64SVAreturnZero
li r3, 1
b N64SVAfinish

N64SVAreturnZero:
li r3, 0

N64SVAfinish:
blr
#=======================================
crashReportWiiMisc:
stwu sp, -0x10(sp)
mflr r0
stw r0, 0x14(sp)

lbz r4, chunk0offset + CrashPage5Status@l(r31)
extsb r6, r4
cmpi 0, r6, 0
blt ReportWiiMiscBroken
bgt ReportWiiMiscPrint

li r5, -1
stb r5, chunk0offset + CrashPage5Status@l(r31)
bl WiiMiscArgs

ReportWiiMiscPrint:
li r3, -2
bl printSetPad
lwz r4, chunk0offset + CrashMiscBuffer@l(r31)
addi r3, r31, chunk0offset + strMiscInfo@l
bl printStr
bl flushScreen
li r5, 1
stb r5, chunk0offset + CrashPage5Status@l(r31)
li r3, 12
b ReportWiiMiscfinish

ReportWiiMiscBroken:
addi r3, r31, chunk0offset + strMiscInfoBroke@l
li r4, 0
bl printStr
bl flushScreen
li r3, 6

ReportWiiMiscfinish:
li r4, 1
bl crashTimer
li r5, 1
stb r5, chunk0offset + CrashPageCurrent@l(r31)

lwz r0, 0x14(sp)
mtlr r0
addi sp, sp, 0x10
blr
#=======================================
.org 0x58F8 - chunk0offset     #0x19F8
crashN64Stack:

.set rMaxlines, 30
.set rHoldJrRa, 29
.set rN64RamStart, 28
.set r8000, 27
.set rJrRaHex, 26
.set rRAHighwordHex, 25
.set rDoDelaySlot, 24
.set rHoldJumpAddr, 23
.set rHoldStack, 22
.set rHoldN64Addr, 21

stwu sp, -0x70(sp)
mflr r0
stw r0, 0x74(sp)

addi r11, sp, 0x70
bl __save_gpr - chunk0offset - $

addi r3, r31, chunk0offset + strN64StackTrace@l  #header
li r4, 0
bl printStr

lwz r3, chunk0offset + N64Stackpointer@l(r31)
mr rHoldStack, r3

bl printHex32
li r3, 0x0020
bl drawChar

bl getN64TraceStart     #returns n64pntr
mr rHoldN64Addr, r3

bl printHex32
bl printNewline


mr r4, rHoldN64Addr
lwz r3, chunk0offset + N64cpuPointer@l(r31)
li rMaxlines, 21              #max lines printed
lwz rHoldJrRa, 0x50(r3)        #prefill RA in case it doesn't get encountered
#li rHoldJrRa, 0               #hold jrra
lwz rN64RamStart, chunk0offset + N64RAM@l(r31)
addis rN64RamStart, rN64RamStart, 0x8000      #mask out 0x80000000 from RAM pointer
lis rJrRaHex, 0x03E0
ori rJrRaHex, rJrRaHex, 0x0008    #JR RA hex
lis rRAHighwordHex, 0x8FBF 
srwi rRAHighwordHex, rRAHighwordHex, 16       #lw sp 0xXX(ra) highword hex
lis r8000, 0x8000

CNSstartscan:

li rDoDelaySlot, 0               #do delay slot
li rHoldJumpAddr, 0               #hold jump addr
bl N64StackValidAddr
cmpi 0, r3, 0
beq CNSprintdud


CNSreadinst:
lwzx r3, r4, rN64RamStart
nop
cmp 0, r3, rJrRaHex          #is jrra?
beq CNSreadyjrra

srwi r5, r3, 16
cmpi 0, r5, 0x27BD      # is SP add?
beq CNSaddtosp

cmp 0, r5, rRAHighwordHex          # is lw ra,sp?
beq CNSsetreturnaddr

srwi r5, r3, 24
cmpi 0, r5, 0x0008      # is J?
beq CNSreadyjump

b CNScheckdelay

CNSreadyjump:
slwi r5, r3, 8
srwi r3, r5, 6
add rHoldJumpAddr, r3, r8000        #place n64 j addr
li rDoDelaySlot, 1               #set delay
b CNSnextinst


CNSsetreturnaddr:
slwi r5, r3, 16
srawi r5, r5, 16
add r6, rN64RamStart, rHoldStack
lwzx r3, r6, r5
lis r7, 0x8000
ori r7, r7, 0x2D20     #start of n64 thread
cmp 0, r3, r7
beq CNSfinish
mr rHoldN64Addr, r4
bl getN64RAfromrecomp
cmpi 0, r3, 0
beq CNSprintdud
mr rHoldJrRa, r3
mr r4, rHoldN64Addr
b CNSnextinst


CNSaddtosp:
slwi r5, r3, 16
srawi r5, r5, 16
add rHoldStack, r5, rHoldStack
b CNScheckdelay

CNSreadyjrra:
li rDoDelaySlot, 1              #set delay
b CNSnextinst


CNScheckdelay:
cmpi 0, rDoDelaySlot, 0
beq CNSnextinst
li rDoDelaySlot, 0              #clear delay
cmpi 0, rHoldJumpAddr, 0         #is there jump?
bne CNSjumptoaddr
mr rHoldN64Addr, rHoldJrRa
b CNSprintnext

CNSjumptoaddr:
mr rHoldN64Addr, rHoldJumpAddr
li rHoldJumpAddr, 0               #clear j
b CNSprintnext


CNSnextinst:
addi r4, r4, 0x04
b CNSreadinst

CNSprintnext:

mr r3, rHoldStack
bl printHex32
li r3, 0x0020
bl drawChar

mr r3, rHoldN64Addr
bl printHex32
bl printNewline


mr r4, rHoldN64Addr
addi rMaxlines, rMaxlines, -1
cmpi 0, rMaxlines, 0
ble CNSfinish
b CNSstartscan

CNSprintdud:
mr r3, rHoldStack
bl printHex32
addi r3, r31, chunk0offset + strN64StackUnk@l
bl printStr

CNSfinish:
addi r11, sp, 0x70
bl __restore_gpr - chunk0offset - $

lwz r0, 0x74(sp)
mtlr r0
addi sp, sp, 0x70
blr
#========================================================
.org 0x5AF8 - chunk0offset         #0x1BF8
WiiMiscArgs:

.set MiscArgsHeap, 11
.set MiscArgsTreeandBlock, 10
.set MiscArgsCPUl, 9
.set MiscArgsCPUh, 8


stwu sp, -0x20(sp)
mflr r0
stw r0, 0x24(sp)

lwz MiscArgsHeap, chunk0offset + CrashArgHeap@l(r31)
lwz r3, chunk0offset + LastBadN64Inst@l(r31)

addi r4, MiscArgsHeap, 0x20
stw r4, chunk0offset + CrashArgHeap@l(r31)
stw MiscArgsHeap, chunk0offset + CrashMiscBuffer@l(r31)

lwz MiscArgsCPUl, chunk0offset + N64cpuPointer@l(r31)

addis MiscArgsCPUh, MiscArgsCPUl, cpustructHigh
stw r3, 0(MiscArgsHeap)

lwz MiscArgsTreeandBlock, 0x1494(MiscArgsCPUh)  #tree
lhz r3, 0(MiscArgsTreeandBlock)                 #count
stw MiscArgsTreeandBlock, 0x0C(MiscArgsHeap)
stw r3, 0x10(MiscArgsHeap)

lwz r4, 0x04(MiscArgsTreeandBlock)              #size
lwz r5, 0x68(MiscArgsTreeandBlock)              #codeNodeRoot
lwz r3, 0x6C(MiscArgsTreeandBlock)              #ovlNodeRoot
stw r4, 0x14(MiscArgsHeap)
stw r5, 0x18(MiscArgsHeap)
stw r3, 0x1C(MiscArgsHeap)

addi MiscArgsTreeandBlock, MiscArgsCPUh, 0x0F68
mr r3, MiscArgsTreeandBlock
li r4, 192
bl WiiMiscBlockCount
stw r3, 0x04(MiscArgsHeap)

li r4, 13
addi r3, MiscArgsTreeandBlock, 192 * 4
bl WiiMiscBlockCount
stw r3, 0x08(MiscArgsHeap)

lwz r0, 0x24(sp)
mtlr r0
addi sp, sp, 0x20
blr
#========================================================
WiiMiscBlockCount: #(*block, blockcount) return int

.set BlockAccumulate, 9
.set BlocksDone, 8
.set BlockShift, 7


li BlockAccumulate, 0    #accumulate
li BlocksDone, 0    

BlockStartWord:
slwi r6, BlocksDone, 2
lwzx r5, r6, r3
li BlockShift, 31

BlockCheckWord:
srw r12, r5, BlockShift
andi. r12, r12, 0x0001
add BlockAccumulate, BlockAccumulate, r12
addi BlockShift, BlockShift, -1
cmpi 0, BlockShift, 0
bge BlockCheckWord

addi BlocksDone, BlocksDone, 1
cmpw 0, BlocksDone, r4
blt BlockStartWord


mr r3, BlockAccumulate
blr
#========================================================
.org 0x5BF8 - chunk0offset      #0x1CF8
strOOTRando: .string "OoTRando"
strPressA: .string "(A) = Next page  Page %b of 5

"

strCrashSplash: .string "************
Oh! MY GOD!!
************"

strN64RegistersPage:  .string "Exception %b Thread:%x
SRR0:%x LR:%x DAR:%x

N64 CPU State %h
Func:%x RA:%x

AT:%x V0:%x V1:%x
A0:%x A1:%x A2:%x
A3:%x T0:%x T1:%x
T2:%x T3:%x T4:%x
T5:%x T6:%x T7:%x
S0:%x S1:%x S2:%x
S3:%x S4:%x S5:%x
S6:%x S7:%x T8:%x
T9:%x K0:%x K1:%x
GP:%x SP:%x FP:%x
RA:%x

Recomp Node:%x PPC:%x
Start:%x End:%x
Chksum:%x Size:%x"

strN64RegisterBroke: .string "N64 CPU unavailable?? HOW?? WHY"

strWiiGPRPage: .string "Wii GP Registers

Thread:%x
 r0:%x  r1:%x
 r2:%x  r3:%x
 r4:%x  r5:%x
 r6:%x  r7:%x
 r8:%x  r9:%x
r10:%x r11:%x
r12:%x r13:%x
r14:%x r15:%x
r16:%x r17:%x
r18:%x r19:%x
r20:%x r21:%x
r22:%x r23:%x
r24:%x r25:%x
r26:%x r27:%x
r28:%x r29:%x
r30:%x r31:%x

SRR0:%x LR:%x DAR:%x"

strWiiGPRBroke: .string "Wii GP Registers unavailable"

strN64StackTrace: .string "N64 STACK TRACE

"
strN64StackBroke: .string "N64 Stack unavailable"
strN64StackUnk: .string " ????????"

strWiiStack: .string "Wii Back chain

Address  BackChain  LR
"
strWiiStackBroke: .string "Wii Back chain unavailable"

strMiscInfo: .string "VC Misc

Last bad inst:%x

S code block:%x
L code block:%x

Tree:%x
Count:%h Size:%x
Left node start:%x
Right node start:%x"

strMiscInfoBroke: .string "VC Misc info unavailable"

strLoadInROM: .string "Loading: %ld %"

strPatchDate: .string "
OoTR US VC Rev 1"

#strPatchDate: .string "
#OoTR JP VC Rev 1"

.align 2
#=====================================
.org 0x60F8 - chunk0offset     #0x21F8
PollController: #(int timer) return timer, bool skip
stwu sp, -0x10(sp)
mflr r0
stw r0, 0x14(sp)


lbz r5, chunk0offset + AcceptInput@l(r31)
cmpi 0, r5, 0
beq PollControllerSkip

lwz r4, chunk0offset + ControllerPollTime@l(r31)
cmplw 0, r3, r4
ble PollControllerSkip
stw r3, chunk0offset + ControllerPollTime@l(r31)

stw r30, 0x08(sp)
mr r30, r3

lwz r4, -0x76E0(r13)    #gSystem
lwz r3, 0x68(r4)        #*controller
li r5, 1
stw r5, 0x220(r3)
bl updateControllerInput - chunk0offset - $
lwz r4, -0x76E0(r13)    #gSystem
lwz r7, 0x68(r4)        #*controller
mr r3, r30
lwz r30, 0x08(sp)

lwz r5, 0xBC(r7)
lwz r6, 0xCC(r7)
andi. r5, r5, ButtonA@l
andi. r6, r6, ButtonA@l
cmpw 0, r5, r6
ble PollControllerSkip

li r5, -1
srwi r5, r5, 1
stw r5, chunk0offset + Timer@l(r31)
li r4, 1
b PollControllerfinish

PollControllerSkip:
li r4, 0

PollControllerfinish:
lwz r0, 0x14(sp)
mtlr r0
addi sp, sp, 0x10
blr
#=======================================
.org 0x61F8 - chunk0offset     #0x22F8
extCallPatch:
mr r3, r28
mr r5, r29
addi r4, sp, 0x20
bl cpuExecuteUpdate - chunk0offset - $
stw r3, 0x24(sp)
li r4, 0
lwz r3, 0x0C(sp)
b cpuEChookend - chunk0offset + chunk1offset - $
nop
#============================
.org 0x62F8 - chunk0offset     #0x23F8
FindFuncFailHook:
lis r3, 0x8000
stw r18, chunk0offset + LastBadN64Inst@l(r3)        #instruction N64 address
li r3, 0
blr
#=============================
OSUEhook:
lis r25, 0x8000
sth r3, chunk0offset + ExceptionID@l(r25)
lis r31, 0x8017
b OSUEhookend - chunk0offset - $
#=======================================
RomLoadProgressHook:
lis r7, 0x80000000 + WVCLoadLogoStrVAarg@h

srwi r5, r6, 20
addi r4, r5, 1
mulli r4, r4, 100       #multiply progress by 100 then devide by 32 (MB)
li    r5, 32           
divwu r4, r4, r5 
cmpwi r4, 100           #cap at 100%
ble updateProgress
li r4, 100

updateProgress:
stw r4, WVCLoadLogoStrVAarg@l(r7)

lis r5, 0x8000
addi r4, r5, chunk0offset + strLoadInROM@l
stw r4, WVCLoadLogoStrPointer@l(r7)
li r5, 0x02
stw r5, WVCLoadLogoStrCount@l(r7)

mr r4, r30
blr
#=======================================
startupProgress:
stwu sp, -0x10(sp)
mflr r0
stw r0, 0x14(sp)

lhz r5, 0x02(r3)
cmpi 0, r5, loadUpStrCompare
bne supContinue

lis r5, 0x8000
lwz r4, chunk0offset + StartupTimer@l(r5)
addi r4, r4, 1
cmpi 0, r4, 180
stw r4, chunk0offset + StartupTimer@l(r5)

ble supContinue

li r3, 0x0B
bl errorDisplayShow - chunk0offset - $
b supFinish

supContinue:
bl errorDisplayPrint - chunk0offset - $
li r3, 0
bl GXSetCullMode - chunk0offset - $

supFinish:
lwz r0, 0x14(sp)
mtlr r0
addi sp, sp, 0x10
blr
#=======================================
# Hooks
#
# force 8MB ram
# replaces
# 
.org 0x78F0 - chunk1offset #0x2EB0 same in JP and US
nop


# cpuExecuteCall patches
#  In rare cases, the calling code's recompiled JAL assembly gets
#  mangled when the target n64 PPC code gets deleted and rebuilt.
#  Moving the tagging of the external call as retargetted after
#  cpuExecuteUpdate ought to fix this.

.org cpuExecuteCall - chunk1offset
stwu sp, -0x30(sp)
.org cpuExecuteCall + 0x08 - chunk1offset
stw r0, 0x34(sp)

.org cpuExecuteCall + 0x98 - chunk1offset   #0x035418 #0x048A14
nop
b extCallPatch + chunk0offset - chunk1offset


.org cpuExecuteCall + 0xA0 - chunk1offset
cpuEChookend:


.org cpuExecuteCall + 0x194 - chunk1offset  #0x035514 #0x048B10
nop
nop
lwz r3, 0x24(sp)
nop

.org cpuExecuteCall + 0x1B8 - chunk1offset  #0x035538 #0x048B38
lwz r0, 0x20(sp)

.org cpuExecuteCall + 0x21C - chunk1offset  #0x03559C #0x048B9C
lwz r3, 0x20(sp)

.org cpuExecuteCall + 0x220 - chunk1offset
lwz r0, 0x34(sp)
.org cpuExecuteCall + 0x238 - chunk1offset
addi sp, sp, 0x30


# findFunc(8004C930) hooks cpuFindFunction
# all replace 38600000

.org cpuFindFunction + 0x68 - chunk1offset   #0x039290
bl FindFuncFailHook + chunk0offset - chunk1offset

.org cpuFindFunction + 0x7E4 - chunk1offset   #0x039A0C
bl FindFuncFailHook + chunk0offset - chunk1offset

.org cpuFindFunction + 0x898 - chunk1offset   #0x039AC0
bl FindFuncFailHook + chunk0offset - chunk1offset

.org cpuFindFunction + 0x994 - chunk1offset   #0x039BBC
bl FindFuncFailHook + chunk0offset - chunk1offset

.org cpuFindFunction + 0x99C - chunk1offset   #0x039BC4
bl FindFuncFailHook + chunk0offset - chunk1offset


# switch in displaying load-in progress at start-up
# replaces:
# 4BFFFC49
.org errorDisplayShow + 0x13C - chunk1offset #0x05F504
bl startupProgress + chunk0offset - chunk1offset


# hook into rom loading to grab offset value for progress
# replaces:
# 7FC4F378
.org xlFileGet + 0x110 - chunk1offset  #0x07B8C4
bl RomLoadProgressHook + chunk0offset - chunk1offset

# patch OSDumpContext from scanning the back chain due to chain not ending with 0xFFFFFFFF
# replaces:
# 48000020
.org OSDumpContext + 0x208 - chunk1offset #0x08773C
.long 0x48000040

# patch OSUE to catch exception number
# replaces:
# 3FE08017
.org UnhandledException + 0x14 - chunk1offset   #0x087CB8
b OSUEhook + chunk0offset - chunk1offset


# patch OSUnhandledException end
# replaces 
# 4BFFCA39
.org UnhandledException + 0x2D4 - chunk1offset  #0x087F78
bl crashReport + chunk0offset - chunk1offset

# apply d-pad remappings
.org 0x0016BAF4 #same in JP and US
.long 0x04000000
.long 0x02000000
.long 0x01000000


# patch a string struct to change the print offset for the load-in logo
# replaces 
# 0x00780000
.org WVCLoadLogoStrStruct - chunk0offset  #0x170ADC
.short 0x0140
.short 0x0000
.long 0x00
