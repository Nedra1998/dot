# Zsh .zshrc
# Arden Rasmussen @ 2018

# Plugins {{{
source ~/.zplug/init.zsh

# Prompt {{{
zplug "Nedra1998/oravi", from:github, as:theme
# }}}

# Highlighting {{{
zplug "zsh-users/zsh-syntax-highlighting", defer:2
zplug "zsh-users/zsh-autosuggestions", defer:2
zplug "zsh-users/zsh-completions"
# }}}

# Navigation {{
zplug "plugins/autojump", from:oh-my-zsh
# }}

# Git {{{
zplug "plugins/git", from:oh-my-zsh
# }}}

# Zplug {{{
zplug 'zplug/zplug', hook-build:'zplug --self-manage'
if ! zplug check --verbose; then
    printf "Install? [y/N]: "
    if read -q; then
        echo; zplug install
    fi
fi
# }}}
zplug load

# }}}

# Path {{{
export PATH=/home/arden/.pyenv/bin:$PATH
export PATH=/home/arden/.swiftenv/bin:$PATH
# }}}

# Theme Settings {{{
ORAVI_DIR_TRUNC=true
# }}}

# Aliases {{{

# alias ls='ls --color=auto'
alias ls='exa'
alias py='bpython'
# Edit Commands {{{
alias ezsh='vim ~/.zshrc'
alias evim='vim ~/.config/nvim/init.vim'
alias eterm='vim ~/.config/termite/config'
alias ei3='vim ~/.config/i3/config'
alias epoly='vim ~/.config/polybar/config'
alias term='termite &'
# }}}

# }}}

# Fzf {{{
[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh
export FZF_DEFAULT_COMMAND='rg --files --no-ignore --hidden --follow --glob "!.git/*"'
export FZF_DEFAULT_OPTS='--color=fg:#ECEFF1,bg:#263238,hl:#FFEB3B,fg+:#ECEFF1,bg+:#455A64,hl+:#FF9800,info:#2196F3,prompt:#FF5722,pointer:#B0BEC5,marker:#4CAf50,spinner:#03A9F4,header:#795548'
# }}}

# PyEnv {{{
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
# }}}
# SwiftEnv {{{
eval "$(swiftenv init -)"
# }}}

eval $(thefuck --alias)
