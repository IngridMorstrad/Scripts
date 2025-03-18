source ~/.commonrc
echo "Loading ~/.zshrc"
DISABLE_MAGIC_FUNCTIONS="true"
setopt HIST_IGNORE_SPACE
alias jrnl=" jrnl"
# export PS1="%{$fg[red]%}%n%{$reset_color%}@%{$fg[blue]%}%m %{$fg[yellow]%}%~ %{$reset_color%}%% "
# export PS1="\[\033[36m\]\u\[\033[m\]@\[\033[32m\]\h:\[\033[33;1m\]\w\[\033[m\]\$ "
# This was last used:
# export PS1="%{%F{cyan}%}%n%{%f%}@%{%F{green}%}%m %{%F{yellow}%}%~ %{$%f%} % % "
# Replaced with oh-my-zsh
# PROMPT='%F{cyan}%n%f@%F{green}%m %F{yellow} %~ $%f '
# export CLICOLOR=1
# export LSCOLORS=gxBxhxDxfxhxhxhxhxcxcx

# zsh history stuff
HISTFILE=~/.zsh_history
SAVEHIST=100000 # maximum number of items for the history file
setopt appendhistory
setopt HIST_IGNORE_ALL_DUPS # do not duplicate commands
setopt HIST_SAVE_NO_DUPS # do not save dups
setopt HIST_REDUCE_BLANKS # reduce blanks
setopt HIST_IGNORE_SPACE
setopt INC_APPEND_HISTORY_TIME
setopt EXTENDED_HISTORY

cleanhist() {
    cat -n ~/.zsh_history | sort -t ';' -uk2 | sort -nk1 | cut -f2- > ~/.zsh_short_history
    mv ~/.zsh_short_history ~/.zsh_history
}

### Fix slowness of pastes with zsh-syntax-highlighting.zsh
#zstyle ':bracketed-paste-magic' active-widgets '.self-*'
pasteinit() {
  OLD_SELF_INSERT=${${(s.:.)widgets[self-insert]}[2,3]}
  zle -N self-insert url-quote-magic # I wonder if you'd need `.url-quote-magic`?
}

pastefinish() {
  zle -N self-insert $OLD_SELF_INSERT
}
zstyle :bracketed-paste-magic paste-init pasteinit
zstyle :bracketed-paste-magic paste-finish pastefinish
### Fix slowness of pastes

eval "$(starship init zsh)"

# ["$TERM" = "xterm-kitty" ] && alias ssh="kitty +kitten ssh"
echo "Done loading zshrc"
source ~/.companyrc

commands_to_check=("vi " "vim " "ssh ")

preexec() {
  local cmd="$1"
  # Check if command starts with any of the strings
  for keyword in "${commands_to_check[@]}"; do
    if [[ "$cmd" == "$keyword"* ]]; then
      return
    fi
  done

  export AUTO_NOTIFY_START_TIME=$(date +%s)
  export AUTO_NOTIFY_LOCK="true"
  export AUTO_NOTIFY_CMD="$cmd"
}

precmd() {
  # Check if AUTO_NOTIFY_LOCK is "false"
  if [[ "$AUTO_NOTIFY_LOCK" == "false" ]]; then
    return
  fi

  export AUTO_NOTIFY_LOCK="false"

  local start_time="$AUTO_NOTIFY_START_TIME"
  local current_time=$(date +%s)

  if [[ -n "$start_time" ]]; then
    local time_difference=$((current_time - start_time))

    if ((time_difference > 10)); then
      ms
    fi
  else
    echo "AUTO_NOTIFY_START_TIME is not set."
  fi
}

timer() {
  if [[ $# -ne 1 || ! $1 =~ ^[0-9]+$ ]]; then
    echo "Usage: timer <seconds>"
    return 1
  fi

  local seconds="$1"
  local start_time=$(date +%s)
  local current_time
  local remaining_time

  while true; do
    current_time=$(date +%s)
    remaining_time=$((start_time + seconds - current_time))

    if [[ $remaining_time -le 0 ]]; then
      break
    fi

    printf "\r%ds remaining..." "$remaining_time"
    sleep 1
  done

  echo "Time's up!"
}
