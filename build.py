#!/user/bin/env python3
import lzma
import os
import zipfile

import requests


def download_file(url, path):
    file_name = url[url.rfind("/") + 1:]

    print("Downloading '{0}' to '{1}'.".format(file_name, path))

    if os.path.exists(path):
        return

    request = requests.get(url, stream=True)
    with open(path, 'wb') as f:
        for chunk in request.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

    print("  Done.")


def extract_file(archive_path, dest_path):
    print("Extracting '{0}' to '{1}'.".format(os.path.basename(archive_path), os.path.basename(dest_path)))

    if os.path.exists(dest_path):
        return

    with lzma.open(archive_path) as f:
        file_content = f.read()
        path = os.path.dirname(dest_path)

        if not os.path.exists(path):
            os.makedirs(path)

        with open(dest_path, "wb") as out:
            out.write(file_content)


def main():
    base_path = os.path.abspath(os.path.dirname(__file__))
    downloads_path = os.path.join(base_path, "downloads")

    # Fetch frida information.
    frida_releases_url = "https://api.github.com/repos/frida/frida/releases/latest"
    frida_releases = requests.get(frida_releases_url).json()

    frida_release = frida_releases["tag_name"]
    frida_download_url = "https://github.com/frida/frida/releases/download/{0}/".format(frida_release)

    print("Frida version:\t\t\t{0}".format(frida_release))

    # Create module.prop file.
    module_prop = """"id=magiskfrida
name=MagiskFrida
version=v{0}
versionCode={1}
author=AeonLucid
description=Run frida-server as a service with magisk.
cacheModule=false
support=https://github.com/AeonLucid/MagiskFrida/issues""".format(frida_release, frida_release.replace(".", ""))

    with open("module.prop", "w") as f:
        f.write(module_prop)

    # Download frida-server archives.
    frida_server_32 = "frida-server-{0}-android-arm.xz".format(frida_release)
    frida_server_32_path = os.path.join(downloads_path, frida_server_32)

    frida_server_64 = "frida-server-{0}-android-arm64.xz".format(frida_release)
    frida_server_64_path = os.path.join(downloads_path, frida_server_64)

    download_file(frida_download_url + frida_server_32, frida_server_32_path)
    download_file(frida_download_url + frida_server_32, frida_server_64_path)

    # Extract frida-server to correct path.
    extract_file(frida_server_32_path, os.path.join(base_path, "system/xbin/frida_server"))
    extract_file(frida_server_64_path, os.path.join(base_path, "system/xbin/frida_server64"))

    # Create flashable zip.
    print("Building Magisk module.")

    file_list = ["common/service.sh",
                 "common/post-fs-data.sh",
                 "common/system.prop",
                 "META-INF/com/google/android/update-binary",
                 "META-INF/com/google/android/updater-script",
                 "system/xbin/frida_server",
                 "system/xbin/frida_server64",
                 "config.sh",
                 "module.prop",
                 "README.md"]

    with zipfile.ZipFile(os.path.join(base_path, "MagiskFrida-{0}.zip".format(frida_release)), "w") as zf:
        for file_name in file_list:
            path = os.path.join(base_path, file_name)

            if not os.path.exists(path):
                print("\t{0} does not exist..".format(path))
                continue

            zf.write(path, arcname=file_name)

    print("Done.")


if __name__ == "__main__":
    main()
