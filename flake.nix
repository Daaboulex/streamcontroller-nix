{
  description = "StreamController — Linux Stream Deck application with plugin ecosystem";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
    git-hooks = {
      url = "github:cachix/git-hooks.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    home-manager = {
      url = "github:nix-community/home-manager";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    std = {
      url = "github:Daaboulex/nix-packaging-standard?ref=v2.7.0";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.git-hooks.follows = "git-hooks";
    };
  };

  outputs =
    inputs@{
      flake-parts,
      self,
      ...
    }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      systems = [
        "x86_64-linux"
        "aarch64-linux"
      ];

      imports = [ inputs.std.flakeModules.base ];

      flake.overlays.default = final: _prev: {
        streamcontroller = final.callPackage ./package.nix { };
      };
      flake.nixosModules.default = import ./module.nix;
      flake.homeManagerModules.default = import ./hm-module.nix;

      perSystem =
        {
          system,
          pkgs,
          self',
          ...
        }:
        {
          packages.streamcontroller = pkgs.callPackage ./package.nix { };
          packages.streamcontroller-cli = pkgs.callPackage ./cli/package.nix { };
          packages.default = self'.packages.streamcontroller;

          checks.module-eval-nixos = inputs.std.lib.nixosModuleCheck {
            inherit (inputs) nixpkgs;
            inherit system;
            overlays = [ self.overlays.default ];
            module = ./module.nix;
            config.programs.streamcontroller.enable = true;
          };

          checks.module-eval-hm = inputs.std.lib.homeModuleCheck {
            inherit (inputs) nixpkgs home-manager;
            inherit system;
            overlays = [ self.overlays.default ];
            module = ./hm-module.nix;
            config.programs.streamcontroller.enable = true;
          };
        };
    };
}
