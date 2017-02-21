"execute pathogen#infect()
syntax on
set autochdir
filetype plugin indent on
colorscheme Monokai
if has('gui_running')
  set guifont=Consolas:h9:cANSI
endif
set guioptions-=m
set guioptions-=T
set guioptions-=r
set shiftwidth=4
set softtabstop=4
set expandtab
set nobackup
set nowritebackup
set noswapfile
"Using filetype plugin indent instead for workflowish
"set smartindent
nnoremap Y y$
nnoremap ; :
nnoremap : ;
