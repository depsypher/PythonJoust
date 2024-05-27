PythonJoust
===========

## Fork Info:
I found @StevePaget made a very nice starting point for a joust game! I'm working on fleshing it out so it plays like the arcade. Check out roadmap below to see how it's progressing.

I made it playable online using pygbag for wasm conversion:

https://depsypher.github.io/PythonJoust/

### Roadmap:
- [x] First stage needs bottom platform
- [ ] Add multiple stages with transitions between them
- [X] Show scoring when killing enemies, collecting eggs
- [ ] Add lava troll
- [ ] Make eggs hatch
- [ ] Smarter enemies with different AI/speed based on type and level
- [ ] Add attract mode with high scores and intros
- [ ] Add player 2?

### Reference material:
* Arcade specs: https://seanriddle.com/willhard.html

* Annotated assembly from the arcade:
https://github.com/historicalsource/joust
https://github.com/synamaxmusic/joust/blob/main/JOUSTRV4.ASM


* Original graphics:
https://seanriddle.com/ripper.html

To use ripper, prepare a bin file by concatenating the roms, then load the Joust Sprite list file available at the ripper site. Set palette to Joust and select Sprites view. I think you have to just screenshot to get results, didn't see a way to export an image. Anyway, this gets you a better spritesheet than the one on the site, which seems to have jpeg artifacts and is scaled. 
```
% ls -al
total 120
drwx------@ 17 ray  staff   544 18 May 08:32 .
drwx------@ 29 ray  staff   928 18 May 09:34 ..
-rw-rw-r--@  1 ray  staff  4096 24 Dec  1996 3006-13.1b
-rw-rw-r--@  1 ray  staff  4096 24 Dec  1996 3006-14.2b
-rw-rw-r--@  1 ray  staff  4096 24 Dec  1996 3006-15.3b
-rw-rw-r--@  1 ray  staff  4096 24 Dec  1996 3006-16.4b
-rw-rw-r--@  1 ray  staff  4096 24 Dec  1996 3006-17.5b
-rw-rw-r--@  1 ray  staff  4096 24 Dec  1996 3006-18.6b
-rw-rw-r--@  1 ray  staff  4096 24 Dec  1996 3006-19.7b
-rw-rw-r--@  1 ray  staff  4096 24 Dec  1996 3006-20.8b
-rw-rw-r--@  1 ray  staff  4096 24 Dec  1996 3006-21.9b
-rw-rw-r--@  1 ray  staff  4096 24 Dec  1996 3006-22.10b
-rw-rw-r--@  1 ray  staff  4096 24 Dec  1996 3006-23.11b
-rw-rw-r--@  1 ray  staff  4096 24 Dec  1996 3006-24.12b
-rw-rw-r--@  1 ray  staff   512 24 Dec  1996 decoder.4
-rw-rw-r--@  1 ray  staff   512 24 Dec  1996 decoder.6
-rw-rw-r--@  1 ray  staff  4096 24 Dec  1996 joust.snd
ray@armada joust % cat *.* > joust.bin
```


## Original Readme:
A version of Joust, the old arcade game. I'm just making this for fun, and to brush up my Pygame skills.

Requirements:

Python 3 (get the latest one from python.org)

Pygame (get the latest one from http://www.lfd.uci.edu/~gohlke/pythonlibs/#pygame )

Run joust.py and enjoy!
Feel free to fork and let me know how it goes.

