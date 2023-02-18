#ifndef TEXT_H
#define TEXT_H

#include "z64.h"

void text_init();
int text_print(const char *s, int left, int top);
int text_print_size(const char *s, int left, int top, int width);
void text_flush(z64_disp_buf_t *db);
void text_flush_size(z64_disp_buf_t *db, int width, int height, int hoffset, int voffset);

#endif
