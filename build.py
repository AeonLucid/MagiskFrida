#!/user/bin/env python3
import lzma
import os
import zipfile

import requests

base_path = os.path.abspath(os.path.dirname(__file__))
downloads_path = os.path.join(base_path, "downloads")


def traverse_path_to_list(file_list, path):
    for dp, dn, fn in os.walk(path):
        for f in fn:
            if f == "placeholder" or f == ".gitkeep":
                continue
            file_list.append(os.path.join(dp, f))


def download_file(url, path):
    file_name = url[url.rfind("/") + 1:]

    print("Downloading '{0}' to '{1}'.".format(file_name, path))

    if os.path.exists(path):
        return

    r = requests.get(url, allow_redirects=True)
    with open(path, 'wb') as f:
        f.write(r.content)

    print("Done.")


def extract_file(archive_path, dest_path):
    print("Extracting '{0}' to '{1}'.".format(os.path.basename(archive_path), os.path.basename(dest_path)))

    with lzma.open(archive_path) as f:
        file_content = f.read()
        path = os.path.dirname(dest_path)

        if not os.path.exists(path):
            os.makedirs(path)

        with open(dest_path, "wb") as out:
            out.write(file_content)


def create_module(platform, frida_release):
    # Download frida-server archives.
    frida_download_url = "https://github.com/frida/frida/releases/download/{0}/".format(frida_release)
    frida_server = "frida-server-{0}-android-{1}.xz".format(frida_release, platform)
    frida_server_path = os.path.join(downloads_path, frida_server)

    download_file(frida_download_url + frida_server, frida_server_path)

    # Extract frida-server to correct path.
    extract_file(frida_server_path, os.path.join(base_path, "system/xbin/frida-server"))

    # Create flashable zip.
    print("Building Magisk module.")

    file_list = ["config.sh", "module.prop", "README.md"]

    traverse_path_to_list(file_list, "./common")
    traverse_path_to_list(file_list, "./system")
    traverse_path_to_list(file_list, "./META-INF")

    with zipfile.ZipFile(os.path.join(base_path, "MagiskFrida-{0}-{1}.zip".format(frida_release, platform)), "w") as zf:
        for file_name in file_list:
            path = os.path.join(base_path, file_name)

            if not os.path.exists(path):
                print("\t{0} does not exist..".format(path))
                continue

            zf.write(path, arcname=file_name)


def main():
    # Create necessary folders.
    if not os.path.exists(downloads_path):
        os.makedirs(downloads_path)

    # Fetch frida information.
    frida_releases_url = "https://api.github.com/repos/frida/frida/releases/latest"
    frida_releases = requests.get(frida_releases_url).json()
    frida_release = frida_releases["tag_name"]

    print("Latest frida version is {0}.".format(frida_release))

    # Create module.prop file.
    module_prop = """id=magiskfrida
name=MagiskFrida
version=v{0}
versionCode={1}
author=AeonLucid
description=Runs frida-server on boot as root with magisk.
support=https://github.com/AeonLucid/MagiskFrida/issues
minMagisk=1530""".format(frida_release, frida_release.replace(".", ""))

    with open("module.prop", "w", newline='\n') as f:
        f.write(module_prop)

    # Create flashable modules.
    create_module("arm", frida_release)
    create_module("arm64", frida_release)

    print("Done.")


if __name__ == "__main__":
    main()
