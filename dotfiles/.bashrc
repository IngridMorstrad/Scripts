source ~/.commonrc

export PS1="\[\033[01;31m\]\h\[\033[00m\]\[\033[01;32m\] \[\033[01;32m\]\u \[\033[01;34m\]\$(umask) \[\033[00;33m\]\w\[\033[00m\] \n\[\033[01;00m\]$ \[\033[00m\]"
HISTCONTROL=ignoredups:ignorespace
HISTFILESIZE=-1
HISTTIMEFORMAT="%d/%m/%y %T "
shopt -s histappend
PROMPT_COMMAND="history -n; history -w; history -c; history -r; $PROMPT_COMMAND"
