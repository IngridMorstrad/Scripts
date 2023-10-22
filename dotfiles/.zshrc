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

echo "Done loading zshrc"
