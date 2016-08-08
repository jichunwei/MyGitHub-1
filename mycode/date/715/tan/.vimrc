colorscheme desert
set nu
set autochdir
" 开启语法高亮
syntax on
" 设置文字编码自动识别
set fencs=utf-8,cp936
" 使用鼠标
set mouse=a
" 设置高亮搜索
set hlsearch
" 输入字符串就显示匹配点
set incsearch
" 输入的命令显示出来，看的清楚些。
set showcmd
" Tlist的内部变量。函数列表。
" 窗口在右边显示
" let Tlist_Use_Right_Window=1
let Tlist_File_Fold_Auto_Close=1
" 打开当前目录文件列表
map <F3> :Explore<CR>
" 函数和变量列表
" map <F4> :TlistToggle<CR>
" 搜索当前词，并打开quickfix窗口
map <F5> :call Search_Word()<CR>
" 全能补全
" inoremap <F8> <C-x><C-o>
" 没事，鼠标画线玩的。
" noremap <F9> :call ToggleSketch()<CR>
" 启动函数变量快速浏览的时间设置
set updatetime=100
if has("cscope")
set csprg=/usr/bin/cscope
set csto=0
set cst
set nocsverb
" add any database in current directory
if filereadable("cscope.out")
cs add cscope.out
" else add database pointed to by environment
elseif $CSCOPE_DB != ""
cs add $CSCOPE_DB
endif
set csverb
set cscopetag
set cscopequickfix=s-,g-,c-,d-,t-,e-,f-,i-
endif
nnoremap <silent> <F8> :TlistToggle<CR>
set autoindent "自动缩进
set smartindent "智能缩进
set cindent "C缩进
set tabstop=4
set softtabstop=4
set shiftwidth=4
set expandtab
set showmatch
set tags=tags;
set autochdir
