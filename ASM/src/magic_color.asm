magic_colors:
    lhu   t8, CFG_MAGIC_COLOR+0
    sh    t8, 0x0794 (t6)
    lhu   t8, CFG_MAGIC_COLOR+2
    sh    t8, 0x0796 (t6)
    lhu   t8, CFG_MAGIC_COLOR+4
    sh    t8, 0x0798 (t6)
    addu  t8, r0, t6
    jr    ra