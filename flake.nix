{
  description = "StreamController — Linux Stream Deck application with plugin ecosystem";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs =
    {
      self,
      nixpkgs,
    }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
    in
    {
      packages.${system} = {
        default = self.packages.${system}.streamcontroller;
        streamcontroller = pkgs.callPackage ./package.nix { };
        streamcontroller-cli = pkgs.callPackage ./cli/package.nix { };
      };

      nixosModules.default = import ./module.nix;
      homeManagerModules.default = import ./hm-module.nix;

      overlays.default = final: _prev: {
        inherit (self.packages.${final.system}) streamcontroller;
      };
    };
}
