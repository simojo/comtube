for d in comic*/ ; do
    rm -rf $d
done
echo 'removed all comic*/ directories'
for d in frames*/ ; do
    rm -rf $d
done
echo 'removed all frames*/ directories'
for f in *.mp4 ; do
    rm $f
done
echo 'removed all *.mp4 files'