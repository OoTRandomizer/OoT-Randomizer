#include <stdint.h>
#include "heart_colors.h"

extern colorRGB16_t CFG_HEART_COLOR;

colorRGB16_t defaultHeart   = { 0xFF, 0x46, 0x32 };
colorRGB16_t defaultDDHeart = { 0xC8, 0x00, 0x00 };

colorRGB16_t* beating_no_dd    = (colorRGB16_t*)0x801D8B92;
colorRGB16_2_t* normal_no_dd   = (colorRGB16_2_t*)0x801D8B9E;
colorRGB16_t* beating_dd       = (colorRGB16_t*)0x8011BD38;
colorRGB16_t* normal_dd        = (colorRGB16_t*)0x8011BD50;

void update_heart_colors() {
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
}