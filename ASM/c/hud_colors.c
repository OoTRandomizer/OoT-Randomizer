#include <stdint.h>
#include "hud_colors.h"

#define MIN(a, b) (((a) < (b)) ? (a) : (b))

extern colorRGB16_t CFG_HEART_COLOR;
extern colorRGB16_t CFG_A_BUTTON_COLOR;
extern colorRGB16_t CFG_B_BUTTON_COLOR;
extern colorRGB16_t CFG_C_BUTTON_COLOR;
extern colorRGB16_t CFG_A_NOTE_COLOR;
extern colorRGB16_t CFG_C_NOTE_COLOR;
extern colorRGB16_t CFG_TEXT_CURSOR_COLOR;

const colorRGB16_t defaultHeart   = { 0xFF, 0x46, 0x32 };
const colorRGB16_t defaultDDHeart = { 0xC8, 0x00, 0x00 };

colorRGB16_t* beating_no_dd    = (colorRGB16_t*)0x801D8B92;
colorRGB16_2_t* normal_no_dd   = (colorRGB16_2_t*)0x801D8B9E;
colorRGB16_t* beating_dd       = (colorRGB16_t*)0x8011BD38;
colorRGB16_t* normal_dd        = (colorRGB16_t*)0x8011BD50;

colorRGB16_t* a_button        = (colorRGB16_t*)0x801C7950;
colorRGB16_t* b_button        = (colorRGB16_t*)0x801C767A;
colorRGB16_t* c_button        = (colorRGB16_t*)0x801C7672;

uint16_t* a_note_r  = (uint16_t*)0x8012BE10;
uint16_t* a_note_g  = (uint16_t*)0x8012BE14;
uint16_t* a_note_b  = (uint16_t*)0x8012BE12;

uint16_t* c_note_r  = (uint16_t*)0x8012BE1C;
uint16_t* c_note_g  = (uint16_t*)0x8012BE20;
uint16_t* c_note_b  = (uint16_t*)0x8012BE1E;

colorRGB16_t* a_note_glow_base       = (colorRGB16_t*)0x801131E0;
colorRGB16_t* a_note_glow_max        = (colorRGB16_t*)0x801131E6;
colorRGB16_t* a_note_font_glow_base  = (colorRGB16_t*)0x801131EC;
colorRGB16_t* a_note_font_glow_max   = (colorRGB16_t*)0x801131F2;
colorRGB16_t* c_note_glow_base       = (colorRGB16_t*)0x801131F8;
colorRGB16_t* c_note_glow_max        = (colorRGB16_t*)0x801131FE;
colorRGB16_t* c_note_font_glow_base  = (colorRGB16_t*)0x80113204;
colorRGB16_t* c_note_font_glow_max   = (colorRGB16_t*)0x8011320A;

colorRGB16_t* text_cursor_inner_base  = (colorRGB16_t*)0x80112F08;
colorRGB16_t* text_cursor_inner_max   = (colorRGB16_t*)0x80112F0E;
colorRGB16_t* text_cursor_border_base  = (colorRGB16_t*)0x80112F14;
colorRGB16_t* text_cursor_border_max   = (colorRGB16_t*)0x80112F1A;

void update_hud_colors() {
  colorRGB16_t heartColor = CFG_HEART_COLOR;

  (*beating_no_dd)   = heartColor;

  (*normal_no_dd).r1 = heartColor.r;
  (*normal_no_dd).g1 = heartColor.g;
  (*normal_no_dd).b1 = heartColor.b;

  if (heartColor.r == defaultHeart.r &&
      heartColor.g == defaultHeart.g &&
      heartColor.b == defaultHeart.b) {
    heartColor = defaultDDHeart;
  }

  (*beating_dd) = heartColor;
  (*normal_dd)  = heartColor;

  (*a_button) = CFG_A_BUTTON_COLOR;
  (*b_button) = CFG_B_BUTTON_COLOR;
  (*c_button) = CFG_C_BUTTON_COLOR;

  (*a_note_r) = CFG_A_NOTE_COLOR.r;
  (*a_note_g) = CFG_A_NOTE_COLOR.g;
  (*a_note_b) = CFG_A_NOTE_COLOR.b;

  (*c_note_r) = CFG_C_NOTE_COLOR.r;
  (*c_note_g) = CFG_C_NOTE_COLOR.g;
  (*c_note_b) = CFG_C_NOTE_COLOR.b;

  (*a_note_glow_base) = CFG_A_NOTE_COLOR;
  (*c_note_glow_base) = CFG_C_NOTE_COLOR;
  colorRGB16_t a_note_glow_color = {
    MIN(CFG_A_NOTE_COLOR.r + 0x32, 0xFF),
    MIN(CFG_A_NOTE_COLOR.g + 0x32, 0xFF),
    MIN(CFG_A_NOTE_COLOR.b + 0x32, 0xFF),
  };
  colorRGB16_t c_note_glow_color = {
    MIN(CFG_C_NOTE_COLOR.r + 0x32, 0xFF),
    MIN(CFG_C_NOTE_COLOR.g + 0x32, 0xFF),
    MIN(CFG_C_NOTE_COLOR.b + 0x32, 0xFF),
  };
  (*a_note_glow_max) = a_note_glow_color;
  (*c_note_glow_max) = c_note_glow_color;
  (*a_note_font_glow_max) = CFG_A_NOTE_COLOR;
  (*c_note_font_glow_max) = CFG_C_NOTE_COLOR;

  (*text_cursor_inner_base) = CFG_TEXT_CURSOR_COLOR;
  colorRGB16_t text_cursor_glow_color = {
    MIN(CFG_TEXT_CURSOR_COLOR.r + 0x32, 0xFF),
    MIN(CFG_TEXT_CURSOR_COLOR.g + 0x32, 0xFF),
    MIN(CFG_TEXT_CURSOR_COLOR.b + 0x32, 0xFF),
  };
  (*text_cursor_inner_max) = text_cursor_glow_color;
  (*text_cursor_border_max) = text_cursor_glow_color;
}

const colorRGB8_t rupee_colors[4] = {
  { 0xC8, 0xFF, 0x64 }, // Base Wallet (Green)
  { 0x82, 0x82, 0xFF }, // Adult's Wallet (Blue)
  { 0xFF, 0x64, 0x64 }, // Giant's Wallet (Red)
  { 0xFF, 0x5A, 0xFF }, // Tycoon's Wallet (Purple)
};

uint32_t rupee_hud_color() {
  colorRGB8_t current_color = rupee_colors[z64_file.wallet];
  return (current_color.r << 24) +  (current_color.g << 16) +  (current_color.b << 8);
}
