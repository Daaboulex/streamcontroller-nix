# StreamController (Nix)

[StreamController](https://github.com/StreamController/StreamController), the
Linux application for Elgato Stream Deck devices and its plugins, packaged to
run natively instead of as a Flatpak. A NixOS module installs it with its udev
rules. A Home Manager module is there for people who want their pages and
buttons declared in Nix, and a command-line tool edits the same page files
without the application running.

The flake is declared for `x86_64-linux` and `aarch64-linux` and follows
`nixos-unstable`. Nothing in this repository records which Stream Deck models
it has been tried with.

## Install

Add the flake:

```nix
{
  inputs.streamcontroller = {
    url = "github:Daaboulex/streamcontroller-nix";
    inputs.nixpkgs.follows = "nixpkgs";
  };
}
```

Then add the overlay, import the module and switch it on:

```nix
{
  imports = [ inputs.streamcontroller.nixosModules.default ];
  nixpkgs.overlays = [ inputs.streamcontroller.overlays.default ];

  programs.streamcontroller = {
    enable = true;
    autostart = true;
  };
}
```

`enable` installs the application and the udev rules for USB access to the
deck. `autostart` adds an XDG autostart entry, so the application starts at
login. Without it, start the application yourself with `streamcontroller`.

The application keeps its data in `$XDG_DATA_HOME/StreamController`, not in
the Flatpak directory under `~/.var/app`.

## Declaring pages

Pages can stay in the application. To declare them in Nix, add
`inputs.streamcontroller.homeModules.default` to `home-manager.sharedModules`
and describe a page in your Home Manager configuration:

```nix
programs.streamcontroller = {
  enable = true;
  defaultPages."CL12345678" = "Default";
  pages.Default.keys."0x0".states."0" = {
    label.center.text = "Toggle";
    actions = [{
      id = "com_core447_OSPlugin::RunCommand";
      settings.command = "goxlr-toggle";
    }];
  };
};
```

A key is named `COLxROW`, counted from zero at the top left, so `0x0` is the
first key. An action is a plugin's `id` with the `settings` that plugin takes.

The options a person sets first, all under `programs.streamcontroller`:

| Option | What it is for |
|---|---|
| `pages` | Pages written in Nix, one entry per page name |
| `pageFiles` | Pages the application saved itself, handed over as JSON files |
| `defaultPages` | The page each deck opens with, by the deck's serial number |
| `assets` | Icons and images, copied to `<dataPath>/assets/` |

A full two-page example is in [docs/CONFIGURATION.md](docs/CONFIGURATION.md).
Every option, with its type and default: [docs/OPTIONS.md](docs/OPTIONS.md).

## Starting from pages you already have

A page file the application saved can be handed over as it is, through
`pageFiles`. To get Nix instead, run [export-config.sh](export-config.sh) from
a checkout of this repository. It needs `jq`, and its output is ready to paste
into your `programs.streamcontroller` block.

```bash
bash export-config.sh > my-streamcontroller-config.nix
```

If you used the Flatpak before, the Home Manager module copies its plugins,
settings and other runtime data into the new data directory once and leaves
the old directory as it was. Pages are not copied.

## The command-line tool

`streamcontroller-cli` reads and writes the JSON files directly, so it needs
no running application. It is the flake package `streamcontroller-cli` and is
not in the overlay. Every command is in [docs/CLI.md](docs/CLI.md).

```bash
streamcontroller-cli page list
streamcontroller-cli button set-label Default 0x0 "Hello" --position center
streamcontroller-cli --json device list
```

## Known limits

- A declared page is copied again whenever it differs from the deployed file,
  so a change made to it in the application is lost at the next activation.
- Plugins are not declared in Nix. They are installed through StreamController's
  own plugin system.
- The application's built-in autostart is switched off in this package. Use the
  `autostart` option of the NixOS module.
- Importing the NixOS module disables the nixpkgs module of the same name, so
  `programs.streamcontroller` has only the options of this one.

## When something does not work

A plugin keeps its own Python environment, and a system update that replaces
Python breaks it. At every activation the Home Manager module removes an
environment whose Python is gone and, for a plugin with a `requirements.txt`,
builds it again. It prints a warning when that fails.

Before changing pages with the command-line tool, take a backup with
`streamcontroller-cli backup create`. `backup restore` brings one back.

## More

- [docs/CONFIGURATION.md](docs/CONFIGURATION.md): the full example, key
  coordinates, actions, assets, the JSON the module writes, the export script
- [docs/CLI.md](docs/CLI.md): every command of `streamcontroller-cli`
- [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md): building, checks, upstream

## License

The [`LICENSE`](./LICENSE) file of this repository is MIT. Upstream StreamController is [GPL-3.0-only](https://github.com/StreamController/StreamController/blob/main/LICENSE), and [`package.nix`](./package.nix) marks the packaged application `gpl3Only` accordingly. [`cli/package.nix`](./cli/package.nix) marks the command-line tool `gpl3Only` as well.
