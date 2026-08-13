# streamcontroller-cli — offline CLI for managing Stream Deck pages, buttons, plugins, and settings.
{
  lib,
  python3Packages,
}:
python3Packages.buildPythonApplication {
  pname = "streamcontroller-cli";
  version = "0.1.0";
  pyproject = true;

  src = ./.;

  build-system = with python3Packages; [
    setuptools
  ];

  propagatedBuildInputs = with python3Packages; [
    click
  ];

  doCheck = false;

  meta = {
    homepage = "https://github.com/StreamController/StreamController";
    description = "StreamController CLI — manage Stream Deck pages, buttons, plugins, and settings offline";
    license = lib.licenses.gpl3Only;
    platforms = lib.platforms.linux;
    mainProgram = "streamcontroller-cli";
  };
}
