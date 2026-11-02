# Records docs/demo/facts.gif from a real run: `vhs docs/demo/facts.tape` from the repo root.
Output docs/demo/facts.gif
Set Shell "bash"
Set FontSize 15
Set Width 1300
Set Height 460
Set Padding 18
Set Theme "Catppuccin Mocha"
Set TypingSpeed 22ms

Hide
Type `export PS1='$ ' AGENT_MEMORY_DB=$(mktemp -d)/m.db && uv sync -q && source .venv/bin/activate && agent-memory --database $AGENT_MEMORY_DB add 'My favorite editor is Vim. I live in Lisbon.' >/dev/null && agent-memory --database $AGENT_MEMORY_DB add 'Actually, I switched to Neovim for my editor.' >/dev/null && clear` Enter
Sleep 10s
Show
Type `agent-memory --database $AGENT_MEMORY_DB facts` Enter
Sleep 2.5s
Type `agent-memory --database $AGENT_MEMORY_DB stats` Enter
Sleep 3s
