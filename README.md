# CMP - Command Music Player
A simple command line music player

Developed by:
```shell
▄▄▄  ▄• ▄▌·▄▄▄·▄▄▄ ▄▄▄▄·  ▄• ▄▌·▄▄▄·▄▄▄
▀▄ █·█▪██▌▐▄▄·▐▄▄· ▐█ ▀█▪ █▪██▌▐▄▄·▐▄▄·
▐▀▀▄ █▌▐█▌██▪ ██▪  ▐█▀▀█▄ █▌▐█▌██▪ ██▪ 
▐█•█▌▐█▄█▌██▌.██▌ .██▄▪▐█ ▐█▄█▌██▌.██▌.
.▀  ▀ ▀▀▀ ▀▀▀ ▀▀▀  ·▀▀▀▀   ▀▀▀ ▀▀▀ ▀▀▀ 
```

## Installation
1: `git clone https://github.com/ruffbuff/cmp-py`
<br/>
2: `cd cmp-py`
<br/>
3: `mv ~/path/to/your/clone/conf_example.py ~/path/to/your/clone/conf.py`
<br/>
4: Go to `conf.py` and change API_KEY & MUSIC_PATH to your own.
<br/>
5: `nano ~/.config/cmp/cmp.sh`
<br/>
6.0: Then add this bash script, and make it executable:
<br/>

```bash
#!/bin/bash

source /path/to/your/clone/.venv/bin/activate

restore_padding() {
  if [[ -n "$KITTY_PID" ]]; then
    kitty @ set-spacing padding=default
  fi
}

if [[ -n "$KITTY_PID" ]]; then
  kitty @ set-spacing padding=0
fi

trap restore_padding EXIT

python3 /path/to/your/clone/main.py

restore_padding
```

6.1: `chmod +x ~/.config/cmp/cmp.sh`
<br/>
7: Last thing: `cd` to your terminal framework config like `~/.zshrc` for `zsh`, and find lines with `Helpful aliases`,<br/>
add `alias cmp='~/.config/cmp/cmp.sh'`, then `ctrl+o` + `Enter` to save, and `ctrl+x` to exit.
<br/>
8: Start your terminal and write `cmp`

## License
**[CC-BY-SA-4.0](LICENSE)**
<br/>

[Link](https://choosealicense.com/licenses/cc-by-sa-4.0/#)