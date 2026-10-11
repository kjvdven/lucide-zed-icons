#!/usr/bin/env python3
"""Build the Lucide icon theme for Zed.

Usage: python build.py /path/to/lucide-clone
Icons come from the Lucide repo (icons/ and lab/) or from ./custom/*.svg.
Change CHOICES / FILE_ICONS / mappings below and rebuild.
"""
import json, os, re, sys, shutil

LUCIDE = sys.argv[1] if len(sys.argv) > 1 else "/tmp/lucide"
HERE = os.path.dirname(os.path.abspath(__file__))

APPEARANCES = {            # theme name suffix -> (appearance, stroke colour)
    "Dark": ("dark", "#a9afbc"),
    "Light": ("light", "#5c6370"),
}

CHOICES = {                 # icons still to be decided
    "blade": "custom:file-at",     # or "custom:file-at-large", "custom:file-sword", "custom:file-sword-center", "at-sign"
    "erb": "custom:file-gem",      # or "custom:file-gem-center", "custom:erb-tag", "percent"
    "markdown": "custom:markdown", # or "pilcrow"
}

# key -> source ("name" = Lucide icon/lab, "custom:name" = ./custom/name.svg)
FILE_ICONS = {
    "default": "file",
    "html": "file-code-corner", "css": "hash", "js": "custom:js", "ts": "custom:ts",
    "json": "braces", "php": "elephant-face",
    "blade": CHOICES["blade"], "erb": CHOICES["erb"],
    "ruby": "gem", "rake": "hammer",
    "yaml": "sliders-horizontal", "env": "key-round", "lock": "lock",
    "database": "database", "docker": "ship", "shell": "square-terminal",
    "markdown": CHOICES["markdown"], "text": "file-text", "readme": "book-open",
    "license": "scale", "image": "image", "vector": "pen-tool", "font": "type",
    "package": "package", "tailwind": "wind", "git": "git-branch",
    "xml": "file-code-corner",
    # general file types (from the old Tokyo Night set)
    "audio": "file-music", "video": "film", "log": "scroll-text", "diff": "diff",
    "document": "file-text", "spreadsheet": "sheet", "archive": "file-archive",
    "backup": "archive-restore", "storage": "database", "notebook": "notebook-pen",
    # tooling & project files
    "settings": "sliders-horizontal", "linter": "list-checks", "formatter": "paintbrush",
    "ci": "workflow", "deploy": "cloud-upload", "helm": "ship-wheel",
    "version": "tag",
    "code": "code",          # generic fallback for programming languages
}

# Zed's own file type keys (crates/theme/src/icon_theme.rs). Zed merges its default
# suffix list into every theme, so every key it knows needs an icon here - otherwise
# Zed falls back to its own (non-Lucide) icon for that type.
ZED_KEYS = {
    "javascript": "js", "typescript": "ts", "react": "js", "css": "css", "sass": "css",
    "html": "html", "template": "html", "json": "json", "php": "php", "ruby": "ruby",
    "markdown": "markdown", "yaml": "yaml", "toml": "yaml", "settings": "settings",
    "editorconfig": "settings", "csproj": "settings", "fsproj": "settings",
    "vbproj": "settings", "vs_sln": "settings", "vs_suo": "settings",
    "docker": "docker", "lock": "lock", "bun": "lock", "image": "image", "font": "font",
    "terminal": "shell", "vcs": "git", "audio": "audio", "video": "video", "log": "log",
    "diff": "diff", "document": "document", "storage": "storage", "ipynb": "notebook",
    "prisma": "database", "surrealql": "database",
    "eslint": "linter", "stylelint": "linter", "prettier": "formatter",
    "gitlab": "ci", "heroku": "deploy", "helm": "helm", "coffeescript": "code",
    "default": "default",
}
for _k in ("astro ballerina bicep c cairo code cpp crystal csharp cue dart elixir elm "
           "erlang fsharp gleam go graphql haskell hcl java julia kdl kotlin lua luau "
           "metal nim nix ocaml odin phoenix puppet python r roc rust scala solidity "
           "svelte swift tcl terraform v vue vyper wgsl zig").split():
    ZED_KEYS.setdefault(_k, "code")
FILE_SUFFIXES = {
    "html": "html", "htm": "html", "css": "css", "scss": "css", "sass": "css", "less": "css",
    "js": "js", "mjs": "js", "cjs": "js", "jsx": "js",
    "ts": "ts", "mts": "ts", "cts": "ts", "tsx": "ts",
    "json": "json", "jsonc": "json", "php": "php", "blade.php": "blade",
    "erb": "erb", "html.erb": "erb", "rb": "ruby", "gemspec": "ruby", "rake": "rake",
    "yml": "yaml", "yaml": "yaml", "toml": "yaml", "ini": "yaml", "env": "env",
    "lock": "lock", "sql": "database", "sqlite": "database", "sqlite3": "database",
    "sh": "shell", "bash": "shell", "zsh": "shell", "fish": "shell",
    "md": "markdown", "mdx": "markdown", "txt": "text",
    "png": "image", "jpg": "image", "jpeg": "image", "gif": "image", "webp": "image",
    "avif": "image", "ico": "image", "svg": "vector",
    "woff": "font", "woff2": "font", "ttf": "font", "otf": "font", "xml": "xml",
    "zip": "archive", "tar": "archive", "gz": "archive", "tgz": "archive", "rar": "archive",
    "7z": "archive", "bz2": "archive", "xz": "archive",
    "csv": "spreadsheet", "tsv": "spreadsheet", "xls": "spreadsheet", "xlsx": "spreadsheet",
    "ods": "spreadsheet", "bak": "backup", "backup": "backup", "orig": "backup",
    "pdf": "document", "doc": "document", "docx": "document", "odt": "document",
    "rtf": "document",
}
FILE_STEMS = {
    "Gemfile": "ruby", "Gemfile.lock": "lock", "Rakefile": "rake", "Dockerfile": "docker",
    "docker-compose.yml": "docker", "compose.yaml": "docker", ".env": "env",
    ".env.example": "env", "package.json": "package", "composer.json": "package",
    "tailwind.config.js": "tailwind", "tailwind.config.ts": "tailwind",
    ".gitignore": "git", ".gitattributes": "git", ".gitkeep": "git", ".keep": "git",
    ".ruby-version": "version", ".node-version": "version", ".nvmrc": "version",
    ".python-version": "version", ".php-version": "version", ".tool-versions": "version",
    ".go-version": "version", ".terraform-version": "version", ".bun-version": "version",
    ".java-version": "version", ".sdkmanrc": "version", "VERSION": "version",
    "README": "readme", "README.md": "readme", "LICENSE": "license", "LICENSE.md": "license",
}
FOLDERS = {                 # collapsed (Lucide), expanded (custom)
    "code": ("folder-code", "custom:folder-code-open"),
    "test": ("folder-check", "custom:folder-check-open"),
    "config": ("folder-cog", "custom:folder-cog-open"),
    "vendor": ("folder-archive", "custom:folder-archive-open"),
    "git": ("folder-git", "custom:folder-git-open"),
}
NAMED_DIRS = {
    "src": "code", "app": "code", "lib": "code", "resources": "code",
    "test": "test", "tests": "test", "spec": "test",
    "config": "config", ".config": "config",
    "vendor": "vendor", "node_modules": "vendor",
    ".git": "git", ".github": "git",
}


def source_svg(src):
    if src.startswith("custom:"):
        p = os.path.join(HERE, "custom", src[7:] + ".svg")
    else:
        p = next((q for q in (os.path.join(LUCIDE, d, src + ".svg") for d in ("icons", "lab"))
                  if os.path.exists(q)), None)
        if not p:
            raise SystemExit(f"icon not found: {src}")
    return open(p).read()


def main():
    out_icons = os.path.join(HERE, "icons")
    shutil.rmtree(out_icons, ignore_errors=True)
    themes = []
    for suffix, (appearance, colour) in APPEARANCES.items():
        d = os.path.join(out_icons, appearance)
        os.makedirs(d)
        written = {}

        def put(src):
            if src not in written:
                name = src.replace("custom:", "")
                svg = source_svg(src).replace("currentColor", colour)
                svg = re.sub(r'\s*class="[^"]*"', "", svg)
                open(os.path.join(d, name + ".svg"), "w").write(svg)
                written[src] = f"./icons/{appearance}/{name}.svg"
            return written[src]

        theme = {
            "name": f"Lucide {suffix}",
            "appearance": appearance,
            "directory_icons": {"collapsed": put("folder"), "expanded": put("folder-open")},
            "named_directory_icons": {
                n: {"collapsed": put(FOLDERS[k][0]), "expanded": put(FOLDERS[k][1])}
                for n, k in NAMED_DIRS.items()},
            "chevron_icons": {"collapsed": put("chevron-right"), "expanded": put("chevron-down")},
            "file_stems": FILE_STEMS,
            "file_suffixes": FILE_SUFFIXES,
            "file_icons": {**{k: {"path": put(FILE_ICONS[v])} for k, v in ZED_KEYS.items()},
                           **{k: {"path": put(v)} for k, v in FILE_ICONS.items()}},
        }
        themes.append(theme)
    os.makedirs(os.path.join(HERE, "icon_themes"), exist_ok=True)
    json.dump({"$schema": "https://zed.dev/schema/icon_themes/v0.3.0.json",
               "name": "Lucide Icons", "author": "Lemone", "themes": themes},
              open(os.path.join(HERE, "icon_themes", "lucide.json"), "w"), indent=2)
    # sanity: every referenced key exists
    for m in (FILE_SUFFIXES, FILE_STEMS):
        missing = set(m.values()) - set(FILE_ICONS)
        assert not missing, missing
        missing = set(ZED_KEYS.values()) - set(FILE_ICONS)
        assert not missing, missing
    print(f"built {len(themes)} themes, {len(os.listdir(os.path.join(out_icons, 'dark')))} icons each")


if __name__ == "__main__":
    main()
