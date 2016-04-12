autocmd BufWritePre *.py call yapf#YAPF()

nnoremap <silent> <Leader>l :Egrep<CR>

set wildignore+=*/env/**
