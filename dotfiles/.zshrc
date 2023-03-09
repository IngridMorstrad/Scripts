source ~/.commonrc
echo "Loading ~/.zshrc"
# export PS1="%{$fg[red]%}%n%{$reset_color%}@%{$fg[blue]%}%m %{$fg[yellow]%}%~ %{$reset_color%}%% "
# export PS1="\[\033[36m\]\u\[\033[m\]@\[\033[32m\]\h:\[\033[33;1m\]\w\[\033[m\]\$ "
# This was last used:
# export PS1="%{%F{cyan}%}%n%{%f%}@%{%F{green}%}%m %{%F{yellow}%}%~ %{$%f%} % % "
PROMPT='%F{cyan}%n%f@%F{green}%m %F{yellow} %~ $%f '
export CLICOLOR=1
export LSCOLORS=gxBxhxDxfxhxhxhxhxcxcx

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

echo "Done loading zshrc"
