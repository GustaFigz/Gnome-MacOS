# Kali GNOME com o visual deste PC

Kit pessoal do GustaFigz para reproduzir o desktop MacTahoe escuro do computador de referência num portátil com Kali e GNOME. Contém os **ficheiros efetivamente instalados**, incluindo alterações locais de CSS e extensões, em vez de depender da versão mais recente de cada projeto.

Referência capturada em **21/11/2026: Kali Rolling 2026.3, GNOME Shell 50.4**. O conjunto completo de extensões deste snapshot requer **GNOME 50**. O instalador verifica a compatibilidade antes de alterar ficheiros. Não desativa a validação de versões do GNOME.

## Instalar no portátil

Abre um terminal **dentro da sessão GNOME**, como o teu utilizador normal. Não executes os scripts com `sudo`; apenas a instalação dos pacotes pede sudo.

Como este repositório é privado, autentica primeiro o GitHub. Se ainda não tens o GitHub CLI:

```bash
sudo apt update
sudo apt install -y git gh
gh auth login
```

Escolhe GitHub.com, HTTPS e autenticação pelo navegador. Depois:

```bash
git clone https://github.com/GustaFigz/Gnome-MacOS.git
cd Gnome-MacOS
./dependencies.sh
./install.sh --check
./install.sh
```

**Termina a sessão e volta a entrar.** Não basta fechar o terminal. Em Wayland é necessário voltar a entrar para o GNOME descobrir todas as extensões copiadas.

Depois, verifica:

```bash
cd Gnome-MacOS
./verify.sh
```

Se o GNOME for diferente de 50, o instalador para com uma mensagem antes de aplicar o visual. Confirma com `gnome-shell --version`. Usa as atualizações normais do Kali e volta a verificar; não forces versões de extensões nem um downgrade do sistema. Versões futuras podem exigir um novo snapshot compatível.

## O que vem incluído

- MacTahoe-Dark para GTK e GNOME Shell, com as modificações deste PC.
- MacTahoe-dark para ícones e MacTahoe para cursor, incluindo os recursos locais.
- Wallpaper Monterey escuro para o desktop e ecrã de bloqueio.
- CSS, imagens e configurações de GTK 3 e GTK 4/libadwaita.
- Fontes Adwaita, Cantarell e Fira Code usadas na referência.
- Dock em baixo, ícones de 56 px, transparência, ocultação e indicadores configurados.
- Desfoque, efeitos de vidro, menus, animações das janelas e minimização.
- Botões das janelas à esquerda, cor de destaque, relógio e aparência do Nautilus.
- Perfil visual dedicado do GNOME Terminal. Os perfis já existentes são preservados na lista; o perfil MacTahoe torna-se o predefinido.
- Ordem dos favoritos do computador de referência; por padrão, só são fixadas aplicações presentes no portátil.

| Extensão incluída | Origem |
| --- | --- |
| Apps Menu e User Themes | [GNOME Shell Extensions](https://gitlab.gnome.org/GNOME/gnome-shell-extensions) |
| Blur My Shell | [aunetx/blur-my-shell](https://github.com/aunetx/blur-my-shell) |
| Dash to Dock | [Dash to Dock](https://micheleg.github.io/dash-to-dock/) |
| Desktop Icons NG | [rastersoft/desktop-icons-ng](https://gitlab.com/rastersoft/desktop-icons-ng) |
| Kiwi Menu | [kem-a/kiwi-menu](https://github.com/kem-a/kiwi-menu) |
| Liquid Glass | [ryohsuke1231/liquid-glass](https://github.com/ryohsuke1231/liquid-glass) |
| Tiling Assistant | [ubuntu/Tiling-Assistant](https://github.com/ubuntu/Tiling-Assistant) |
| AppIndicator | [gnome-shell-extension-appindicator](https://github.com/ubuntu/gnome-shell-extension-appindicator) |
| Compiz Windows Effect | [hermes83/compiz-windows-effect](https://github.com/hermes83/compiz-windows-effect) |
| Compiz Magic Lamp | [hermes83/compiz-alike-magic-lamp-effect](https://github.com/hermes83/compiz-alike-magic-lamp-effect) |

As versões e UUIDs exatos estão em [config/manifest.json](config/manifest.json). As definições legíveis estão em [config/settings.json](config/settings.json).

## Aplicações do dock

Na referência estão fixados Terminal, Ficheiros, Firefox ESR, Liner, Software, VS Code, Podman Desktop, GitHub Desktop, ChatGPT, TradingView, Obsidian, draw.io, Resources e XAMPP.

Essas aplicações de terceiros não são instaladas pelo kit. Os seus executáveis, contas e dados não fazem parte do tema. O instalador mostra quais estão ausentes e mantém a ordem dos restantes favoritos. Depois de instalares as aplicações que usas, podes executar o instalador novamente ou fixá-las manualmente. Para gravar literalmente a lista da referência, incluindo identificadores de aplicações ausentes:

```bash
./install.sh --exact-favorites
```

## Backup e restauro

Antes de aplicar mudanças, o instalador copia os ficheiros que vai substituir e guarda o valor anterior de cada chave dconf afetada em:

```text
~/.local/state/gnome-macos/DATA-HORA-ID/
```

Cada instalação cria um backup independente. Se a instalação falhar durante a aplicação, tenta restaurar automaticamente. Conserva esse diretório até confirmares o resultado.

Para desfazer a última instalação concluída:

```bash
./restore.sh
```

Ou usa o caminho de um backup específico mostrado pelo instalador:

```bash
./restore.sh ~/.local/state/gnome-macos/DATA-HORA-ID
```

Termina a sessão e volta a entrar depois do restauro. Chaves que não existiam antes são removidas, e recursos criados pelo kit são removidos. O restauro repõe os recursos geridos no estado do backup; alterações posteriores nesses mesmos recursos serão substituídas. Pacotes instalados pelo apt permanecem instalados.

## Limites e solução de problemas

- **Extensões ainda não aparecem:** termina a sessão e entra novamente. Consulta `gnome-extensions list --enabled` e `./verify.sh`.
- **Uma extensão apresenta erro:** abre a aplicação Extensões ou consulta `journalctl --user -b` para identificar a causa. O verificador compara as definições e procura extensões sem carregar; não substitui uma comparação visual no portátil.
- **Vidro/animações lentos:** desativa Liquid Glass ou os efeitos Compiz na aplicação Extensões. São os efeitos da referência e exigem aceleração gráfica funcional.
- **Aplicações Flatpak sem o mesmo tema:** o isolamento de cada aplicação pode impedir o acesso aos recursos do utilizador. Os temas são aplicados às aplicações nativas; aplicações Electron/Qt e aplicações com tema próprio podem precisar de ajustes próprios.
- **Ecrã HiDPI:** a resolução e a escala do portátil afetam o resultado. O kit preserva a escala do portátil e não copia monitores, drivers ou disposição dos ecrãs.
- **Ecrã de login:** o GDM usa uma configuração separada do desktop. Este kit não substitui recursos de sistema do GDM. O wallpaper do ecrã de bloqueio da sessão está incluído.

O kit gere os temas, as extensões listadas, os recursos de GTK 4 e os ficheiros visuais específicos de GTK 3. Os bookmarks do Nautilus são preservados. A lista de extensões ativas é substituída pela lista visual da referência; a anterior fica no backup. Não copia senhas, contas, histórico, chaves SSH, configuração de VPN/proxy ou configurações de hardware.

## Integridade e validação

Os recursos estão em `assets/desktop.tar.xz`, com SHA-256 em `assets/SHA256SUMS`. O instalador valida o arquivo e os valores GVariant antes de aplicar mudanças, extrai os recursos numa pasta temporária e compila os schemas das extensões antes da cópia.

Teste de instalação e restauro com HOME temporário e sessão D-Bus isolada, sem alterar o desktop real:

```bash
/usr/bin/python3 tests/roundtrip.py
```

A validação local cobre simulação, instalação real num diretório temporário, reinstalação, restauro, preservação de bookmarks e remoção de chaves originalmente ausentes. A validação visual final exige entrar na sessão do portátil. O kit não foi executado no portátil remotamente.

## Créditos e licenças

Temas: [MacTahoe GTK](https://github.com/vinceliuice/MacTahoe-gtk-theme) e [MacTahoe Icons](https://github.com/vinceliuice/MacTahoe-icon-theme), de vinceliuice. Os ficheiros e cabeçalhos de licença presentes nas extensões foram preservados; cópias das licenças dos temas e fontes estão em `licenses/`. O arquivo é um snapshot pessoal com modificações locais e não uma versão oficial desses projetos.

O wallpaper é um recurso de terceiros conservado para reproduzir este desktop pessoal. Os recursos de terceiros mantêm os respetivos direitos e não são abrangidos por uma licença geral deste repositório.
