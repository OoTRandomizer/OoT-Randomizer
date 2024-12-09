#include <string.h>
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <getopt.h>
#include "vadpcm.h"

int vadpcm_enc_wrapper(u8* inBytes, s32 nFrames, u8* outBuffer);
s32 vadpcm_encode(s32 nFrames, u8* inBytes, u8* outBuffer, s32 ***coefTable, s32 order, s32* state, s32 npredictors);

// Wrapper designed to be called from python using c_types
// inBytes - raw input 16-bit big endian samples
// nFrames - number of samples
// outBuffer - buffer that will contain the adpcm compressed data - compressed using the vanilla voice codebook. Preallocate a buffer that's the same size as the input
// return - number of bytes written to outBuffer
int vadpcm_enc_wrapper(u8* inBytes, s32 nFrames, u8* outBuffer)
{
    s32 ***coefTable = NULL;
    s32 *state;
    s32 order;
    s32 npredictors;

    // Read vanilla codebook from file
    FILE * fhandle = fopen("adpcm/shared_pred.tbl", "r");
    if (readcodebook(fhandle, &coefTable, &order, &npredictors) != 0)
    {
        fprintf(stderr, "Error reading codebook\n");
        exit(1);
    }

    // Allocate state structure which is used during compression
    state = malloc(16 * sizeof(s32));
    for (int i = 0; i < 16; i++)
    {
        state[i] = 0;
    }

    // Encode the data
    s32 outSize = vadpcm_encode(nFrames, inBytes, outBuffer, coefTable, order, state, npredictors);
    // Seek back to start of the SSND chunk to write the chunk header
    
    return outSize;
}


// Modified version of the vadpcm_encode program that is part of sdk-tools
// Only meant to encode voice SFX using the vanilla code book
s32 vadpcm_encode(s32 nFrames, u8* inBytes, u8* outBuffer, s32 ***coefTable, s32 order, s32* state, s32 npredictors) {
    u8* pOut = outBuffer;
    s32 currentPos = 0;
    s16* inBuffer = malloc(16 * sizeof(s16));
    s32 nBytes = 0;
    s16 ts;
    s32 nsam;
    // Loop through the data
    while (currentPos < nFrames)
    {
        if (nFrames - currentPos < 16) // handle the last few bytes
        {
            nsam = nFrames - currentPos;
        }
        else
        {
            nsam = 16; // process data in 16 sample chunks
        }

        // Copy 16 samples (32 bytes) from inBytes
        memcpy(inBuffer, inBytes, 16 * sizeof(s16));

        inBytes += 16 * sizeof(s16);
        BSWAP16_MANY(inBuffer, nsam) // Swap inBuffer so we can do calculations
        pOut = vencodeframe(pOut, inBuffer, state, coefTable, order, npredictors, nsam); // encode the samples
        currentPos += nsam;
        nBytes += 9;
    }

    // Add an extra 0 if we're not a multiple of 2
    if (nBytes % 2)
    {
        nBytes++;
        ts = 0;
        *pOut++ = 0;
        //fwrite(&ts, 1, 1, ofile);
    }
    return pOut - outBuffer;
}