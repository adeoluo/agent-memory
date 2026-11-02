# Records docs/demo/recall.gif from a real run: `vhs docs/demo/recall.tape` from the repo root.
Output docs/demo/recall.gif
Set Shell "bash"
Set FontSize 15
Set Width 1300
Set Height 560
Set Padding 18
Set Theme "Catppuccin Mocha"
Set TypingSpeed 22ms

Hide
Type `export PS1='$ ' AGENT_MEMORY_DB=$(mktemp -d)/m.db && uv sync -q && source .venv/bin/activate && clear` Enter
Sleep 10s
Show
Type `agent-memory --database $AGENT_MEMORY_DB add "My favorite editor is Vim. I live in Lisbon."` Enter
Sleep 2s
Type `agent-memory --database $AGENT_MEMORY_DB add "Actually, I switched to Neovim for my editor."` Enter
Sleep 2s
Type `agent-memory --database $AGENT_MEMORY_DB recall "which editor does the user prefer?" -k 2` Enter
Sleep 4s
