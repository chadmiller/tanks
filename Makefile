boot: env

env: python-requirements.txt
	#which sdl-config || sudo apt install libsdl-dev
	#which freetype2-config || sudo apt install libfreetype-dev
	env PATH=/bin:/usr/bin python3 -m venv --clear --system-site-packages $@ && . $@/bin/activate && pip install --upgrade pip && pip install -r $< || rm -r $@

shell: env
	. $</bin/activate && exec env PS1="p> $$PS1" $$SHELL -l
