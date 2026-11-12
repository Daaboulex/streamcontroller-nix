# Development

```bash
git clone https://github.com/Daaboulex/streamcontroller-nix
cd streamcontroller-nix
nix develop
nix fmt
nix flake check --no-build
nix build .#streamcontroller
./result/bin/streamcontroller --help
nix build .#streamcontroller-cli
```

`nix develop` enters the dev shell and installs the pre-commit hooks. `nix fmt`
formats the flake and the two modules. `nix flake check --no-build` is the
evaluation check. The two builds produce the desktop application and the
offline command-line tool, and `./result/bin/streamcontroller --help` verifies
the binary.

## Checks

The flake imports the base module of
[nix-packaging-standard](https://github.com/Daaboulex/nix-packaging-standard),
which brings the hooks, the formatter and the dev shell.
[flake.nix](../flake.nix) adds three checks of its own:

- `requirements-covered` reads upstream's `requirements.txt` against the
  Python environment the package is built with. The names it may skip are the
  `pythonRequirements.ignore` list in
  [.github/update.json](../.github/update.json).
- `module-eval-nixos` evaluates [module.nix](../module.nix) with
  `programs.streamcontroller.enable = true`.
- `module-eval-hm` evaluates [hm-module.nix](../hm-module.nix) the same way.

The command-line tool has tests under
[cli/cli_anything/streamcontroller/tests](../cli/cli_anything/streamcontroller/tests).
The package build does not run them: [cli/package.nix](../cli/package.nix)
sets `doCheck = false`.

CI is [.github/workflows/ci.yml](../.github/workflows/ci.yml), which calls the
standard's package workflow.

## Upstream

| | |
|---|---|
| Project | [StreamController/StreamController](https://github.com/StreamController/StreamController) |
| License | GPL-3.0 |
| Tracked | GitHub releases |

The pinned version and its hash are in [package.nix](../package.nix).
[.github/workflows/update.yml](../.github/workflows/update.yml) runs the
standard's update workflow on a schedule, configured by
[.github/update.json](../.github/update.json).
