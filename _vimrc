"execute pathogen#infect()
syntax on
set autochdir
filetype plugin indent on
colorscheme Monokai
if has('gui_running')
  set guifont=Consolas:h9:cANSI
endif
"Remove the toolbars and other things from the GUI
set guioptions-=m
set guioptions-=T
set guioptions-=r
set shiftwidth=4
set expandtab
set nobackup
set nowritebackup
set noswapfile
"Using filetype plugin indent instead for workflowish
"set smartindent
nnoremap Y y$
nnoremap ; :
nnoremap : ;
inoremap kj <ESC>    "quicker way to exit a mode

" Do not show stupid q: window
map q: :q
