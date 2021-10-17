"execute pathogen#infect()
syntax on
set autochdir
filetype plugin indent on
try
    colorscheme Monokai
catch
    silent! colorscheme desert
endtry
if has('gui_running')
  set guifont=Consolas:h9:cANSI
endif
" Remove the toolbars and other things from the GUI
set guioptions-=m
set guioptions-=T
set guioptions-=r
set shiftwidth=4
set softtabstop=4
set expandtab
set nobackup
set nowritebackup
set noswapfile
set number
set relativenumber
" Using filetype plugin indent instead for workflowish
" Set smartindent
nnoremap Y y$
nnoremap ; :
nnoremap : ;
" Exit quickly
inoremap kj <ESC>

" Do not show stupid q: window
map q: :q

" Easy pasting
set pastetoggle=<F10>
inoremap <C-v> <F10><C-r>+<F10>

" Persistent undo
set undolist
set undodir=~/.vim/undodir

cmap w!! w !sudo tee > /dev/null %
