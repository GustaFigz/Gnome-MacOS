#!/usr/bin/env python3
"""Install or restore the captured desktop without changing system configuration."""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime

ROOT = Path(__file__).resolve().parent
HOME = Path.home()
STATE = HOME / '.local/state/gnome-macos'


def run(*args):
    return subprocess.check_output(args, text=True).strip()


def read_json(path):
    return json.loads(path.read_text())


def remove(path):
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def copy(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir() and not src.is_symlink():
        shutil.copytree(src, dst, symlinks=True)
    else:
        shutil.copy2(src, dst, follow_symlinks=False)


def load_payload():
    archive = ROOT / 'assets/desktop.tar.xz'
    expected = (ROOT / 'assets/SHA256SUMS').read_text().split()[0]
    if hashlib.sha256(archive.read_bytes()).hexdigest() != expected:
        raise RuntimeError('Arquivo de recursos corrompido: checksum incorreto.')
    return archive


def session():
    if os.geteuid() == 0:
        raise RuntimeError('Executa como utilizador normal, sem sudo.')
    if not os.environ.get('DBUS_SESSION_BUS_ADDRESS'):
        raise RuntimeError('Executa num terminal dentro da sessão GNOME do portátil.')
    for cmd in ['dconf', 'gsettings', 'gnome-shell', 'glib-compile-schemas']:
        if not shutil.which(cmd):
            raise RuntimeError('Dependência em falta: ' + cmd + '. Executa ./dependencies.sh')
    # Fail before making changes if the session backend is unavailable.
    run('dconf', 'read', '/org/gnome/shell/enabled-extensions')


def compatibility(manifest):
    version = re.search(r'(\d+)\.', run('gnome-shell', '--version')).group(1)
    bad = [e['uuid'] for e in manifest['extensions'] if version not in e['versions']]
    if bad:
        raise RuntimeError('GNOME ' + version + ' incompatível com o snapshot: ' + ', '.join(bad)
                           + '. Este conjunto completo requer GNOME 50; não forces a compatibilidade.')
    return version


def app_exists(app):
    bases = [HOME / '.local/share', HOME / '.local/share/flatpak/exports/share']
    bases += [Path(p) for p in os.environ.get('XDG_DATA_DIRS', '/usr/local/share:/usr/share').split(':')]
    bases += [Path('/var/lib/flatpak/exports/share')]
    return any((p / 'applications' / app).is_file() for p in bases)


def desired_settings(exact_favorites=False):
    settings = read_json(ROOT / 'config/settings.json')
    for k, v in settings.items():
        settings[k] = v.replace('@@HOME@@', str(HOME))
    terminal_list = '/org/gnome/terminal/legacy/profiles:/list'
    previous = run('dconf', 'read', terminal_list)
    if previous:
        profiles = ast.literal_eval(previous.removeprefix('@as '))
        settings[terminal_list] = repr(list(dict.fromkeys(profiles + ast.literal_eval(settings[terminal_list]))))
    key = '/org/gnome/shell/favorite-apps'
    if not exact_favorites:
        apps = ast.literal_eval(settings[key])
        missing = [app for app in apps if not app_exists(app)]
        if missing:
            print('Aplicações ausentes (não fixadas no dock): ' + ', '.join(missing))
        settings[key] = repr([app for app in apps if app_exists(app)])
    return settings


def validate_settings(settings):
    # GLib parses every GVariant before any write or file replacement.
    from gi.repository import GLib
    for key, value in settings.items():
        if not key.startswith('/') or key.endswith('/'):
            raise RuntimeError('Chave inválida: ' + key)
        GLib.Variant.parse(None, value, None, None)


def write_settings(settings):
    # Enable extensions last, once their assets and preferences are in place.
    enable = '/org/gnome/shell/enabled-extensions'
    for key in sorted(settings, key=lambda k: k == enable):
        value = settings[key]
        if value is None:
            subprocess.run(['dconf', 'reset', key], check=True)
        else:
            subprocess.run(['dconf', 'write', key, value], check=True)


def backup(units, settings):
    STATE.mkdir(parents=True, exist_ok=True)
    dest = Path(tempfile.mkdtemp(prefix=datetime.now().strftime('%Y%m%d-%H%M%S-'), dir=STATE))
    previous = {}
    present = []
    for key in settings:
        previous[key] = run('dconf', 'read', key) or None
    for unit in units:
        src = HOME / unit
        if src.exists() or src.is_symlink():
            copy(src, dest / 'files' / unit)
            present.append(unit)
    (dest / 'backup.json').write_text(json.dumps({'home': str(HOME), 'units': units,
                                                'present': present, 'settings': previous}, indent=2))
    return dest


def caches():
    if shutil.which('fc-cache'):
        subprocess.run(['fc-cache', '-f'], check=True)
    if shutil.which('gtk-update-icon-cache'):
        for name in ['MacTahoe', 'MacTahoe-dark']:
            path = HOME / '.local/share/icons' / name
            if path.exists():
                subprocess.run(['gtk-update-icon-cache', '-f', '-t', str(path)], check=True)


def restore(path):
    info = read_json(path / 'backup.json')
    if info['home'] != str(HOME):
        raise RuntimeError('O backup pertence a outro utilizador.')
    print('A restaurar:', path)
    for unit in info['units']:
        if Path(unit).is_absolute() or '..' in Path(unit).parts:
            raise RuntimeError('Caminho inválido no backup.')
        remove(HOME / unit)
        if unit in info['present']:
            copy(path / 'files' / unit, HOME / unit)
    write_settings(info['settings'])
    caches()
    print('Restauro concluído. Termina a sessão e volta a entrar.')


def install(args):
    session()
    manifest = read_json(ROOT / 'config/manifest.json')
    version = compatibility(manifest)
    archive = load_payload()
    settings = desired_settings(args.exact_favorites)
    validate_settings(settings)
    print('GNOME', version, '|', len(manifest['extensions']), 'extensões |', len(settings), 'definições')
    if args.check:
        print('Verificação concluída; nenhuma alteração aplicada.')
        return
    # Extract and compile away from the live configuration first.
    with tempfile.TemporaryDirectory(prefix='gnome-macos-') as tmp:
        stage = Path(tmp)
        with tarfile.open(archive) as tar:
            tar.extractall(stage, filter='data')
        for schema_dir in stage.glob('.local/share/gnome-shell/extensions/*/schemas'):
            subprocess.run(['glib-compile-schemas', '--strict', str(schema_dir)], check=True)
        css = stage / '.config/gtk-3.0/gtk.css'
        css.write_text(css.read_text().replace('@@HOME@@', str(HOME)))
        saved = backup(manifest['units'], settings)
        print('Backup:', saved, flush=True)
        try:
            for unit in manifest['units']:
                remove(HOME / unit)
                copy(stage / unit, HOME / unit)
            write_settings(settings)
            caches()
        except BaseException:
            print('Falha na instalação. A restaurar automaticamente...', file=sys.stderr)
            restore(saved)
            raise
    (STATE / 'last-backup').write_text(str(saved))
    print('Instalado. Termina a sessão GNOME e volta a entrar para carregar todas as extensões.')
    print('Para desfazer: ./restore.sh ' + str(saved))


def verify():
    session()
    manifest = read_json(ROOT / 'config/manifest.json')
    compatibility(manifest)
    load_payload()
    from gi.repository import GLib
    errors = []
    for unit in manifest['units']:
        if not (HOME / unit).exists():
            errors.append('Recurso ausente: ' + unit)
    for key, value in desired_settings().items():
        actual = run('gsettings', 'get', 'org.gnome.shell', 'enabled-extensions') if key == '/org/gnome/shell/enabled-extensions' else run('dconf', 'read', key)
        try:
            equal = GLib.Variant.parse(None, actual, None, None).equal(GLib.Variant.parse(None, value, None, None))
        except GLib.Error:
            equal = False
        if not equal:
            errors.append('Definição diferente: ' + key)
    enabled = set(run('gnome-extensions', 'list', '--enabled').splitlines())
    for ext in manifest['extensions']:
        if ext['uuid'] not in enabled:
            errors.append('Extensão por carregar (volta a entrar na sessão): ' + ext['uuid'])
        else:
            details = subprocess.check_output(['gnome-extensions', 'info', ext['uuid']],
                                              text=True, env=dict(os.environ, LC_ALL='C'))
            if re.search(r'\b(ERROR|OUT OF DATE|INCOMPATIBLE)\b', details):
                errors.append('Erro de execução: ' + ext['uuid'])
    if errors:
        print('\n'.join(errors))
        sys.exit(1)
    print('Recursos, definições e extensões conferidos.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    ins = sub.add_parser('install')
    ins.add_argument('--check', action='store_true', help='verificar sem instalar')
    ins.add_argument('--exact-favorites', action='store_true', help='incluir ícones de aplicações ausentes')
    res = sub.add_parser('restore')
    res.add_argument('backup', nargs='?')
    sub.add_parser('verify')
    args = parser.parse_args()
    if args.command == 'install':
        install(args)
    elif args.command == 'verify':
        verify()
    else:
        session()
        path = Path(args.backup) if args.backup else Path((STATE / 'last-backup').read_text().strip())
        restore(path)


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError, subprocess.CalledProcessError) as exc:
        sys.exit('Erro: ' + str(exc))
