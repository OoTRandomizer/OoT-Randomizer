camera_init:
    ; initialize camera->waterCamSetting at 1 instead of -1
    addiu   t0, $zero, 0x0001
    sw      t0, 0x011C(s0)

    ; Displaed code
    jr      ra
    lh      t2, 0x014C(s0)
