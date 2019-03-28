CHUNKS_DIR="content"
OUTPUT_DIR="videos"
mkdir $OUTPUT_DIR
for episode in `ls $CHUNKS_DIR`; do echo "gluing $episode"; cat $CHUNKS_DIR/$episode/*.ts > $OUTPUT_DIR/$episode.m2ts; done
