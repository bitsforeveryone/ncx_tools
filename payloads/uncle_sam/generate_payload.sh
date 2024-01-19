mkdir -p payload_build
cp libuncle_sam.so payload_build/libuncle_sam.so
cp uncle_sam_daemon payload_build/uncle_sam_daemon
cp uncle_sam_startup.sh payload_build/uncle_sam_startup.sh
chmod +x payload_build/uncle_sam_daemon
chmod +x payload_build/uncle_sam_startup.sh
makeself --noprogress --nocrc --nomd5 --gzip --nox11 payload_build uncle_sam.run "DELIVERING FREEDOM TO THE MASSES!!!" ./uncle_sam_startup.sh