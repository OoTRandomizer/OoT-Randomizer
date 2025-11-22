#!/bin/sh
for file in *.aiff; do
	echo "Processing file: $file"
	filename_without_ext="${file%.*}"
	echo "without extension: $filename_without_ext"
	./sampleconv vadpcm $file $filename_without_ext.aifc
done


