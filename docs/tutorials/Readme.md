Creation of screen capture  gif files
-------------------------------------
1. Capture the screen (type really slow)
   `ffmpeg -y -f gdigrab -i desktop -s 664x220 -r 3 -c:v png capture.mp4`
2. Convert the video to .gif
   `ffmpeg -y -i capture.mp4 -r 3 capture.gif`
3. Compress the gif (take every 8th frame)
   ```
   gifsicle -f -U capture.gif `seq -f "#%g" 0 8 10000` -O10 -o capture2.gif
   ```

