#ifndef TEXT_H
#define TEXT_H

#include "z64.h"

void text_init();
int text_print(z64_disp_buf_t* db, const char* s, int left, int top);
int text_print_size(z64_disp_buf_t* db, const char* s, int left, int top, int width, int height);
int draw_int(z64_disp_buf_t* db, int32_t number, int16_t left, int16_t top, colorRGBA8_t color);
int draw_int_size(z64_disp_buf_t* db, int32_t number, int16_t left, int16_t top, colorRGBA8_t color, int16_t width, int16_t height);

#endif
