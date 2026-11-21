#!/usr/bin/env python3
"""Real installation/restore under a disposable HOME and a private D-Bus."""
from pathlib import Path
import os
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if os.environ.get('GNOME_MACOS_TEST') != '1':
    with tempfile.TemporaryDirectory(prefix='gnome-macos-test-') as tmp:
        env = dict(os.environ, HOME=tmp, XDG_CONFIG_HOME=tmp+'/.config',
                   XDG_DATA_HOME=tmp+'/.local/share', XDG_CACHE_HOME=tmp+'/.cache',
                   GNOME_MACOS_TEST='1')
        subprocess.run(['dbus-run-session', '--', '/usr/bin/python3', __file__], env=env, check=True)
else:
    home = Path.home()
    gtk = home / '.config/gtk-3.0'
    gtk.mkdir(parents=True)
    (gtk/'bookmarks').write_text('file:///tmp test bookmark\n')
    (gtk/'gtk.css').write_text('/* previous CSS */\n')
    key = '/org/gnome/desktop/interface/gtk-theme'
    subprocess.run(['dconf','write',key,"'Original-test-theme'"],check=True)
    command = ['/usr/bin/python3',str(ROOT/'desktop.py')]
    subprocess.run(command+['install','--check'],check=True)
    assert not (home/'.themes').exists(), 'check must not mutate files'
    subprocess.run(command+['install'],check=True)
    assert (gtk/'bookmarks').read_text() == 'file:///tmp test bookmark\n'
    assert '@@HOME@@' not in (gtk/'gtk.css').read_text()
    assert str(home) in (gtk/'gtk.css').read_text()
    assert subprocess.check_output(['dconf','read',key],text=True).strip() == "'MacTahoe-Dark'"
    subprocess.run(command+['install'],check=True)  # repeated install and latest backup
    subprocess.run(command+['restore'],check=True)
    assert subprocess.check_output(['dconf','read',key],text=True).strip() == "'MacTahoe-Dark'"
    backups=sorted((home/'.local/state/gnome-macos').glob('*/backup.json'))
    subprocess.run(command+['restore',str(backups[0].parent)],check=True)
    assert (gtk/'gtk.css').read_text() == '/* previous CSS */\n'
    assert (gtk/'bookmarks').read_text() == 'file:///tmp test bookmark\n'
    assert not (home/'.themes/MacTahoe-Dark').exists()
    assert subprocess.check_output(['dconf','read',key],text=True).strip() == "'Original-test-theme'"
    assert not subprocess.check_output(['dconf','read','/org/gnome/shell/enabled-extensions'],text=True).strip()
    print('PASS: dry run, install, repeated install, restore, bookmarks and absent settings.')
