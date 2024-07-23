import os
import shutil
import re
from stuffs.general import General
from tools.helper import get_download_dir, host, print_color, run, bcolors

class Gapps(General):

    def __init__(self, android_version):

        available_versions = ['5.0', '5.1', '6.0', '7.0', '7.1', '8.0', '8.1', '9.0', '10.0', '11.0'] # OpenGApps library Android versions availability
        version = re.sub(r'\.0$', '', android_version)
        if version not in available_versions:
            version = available_versions[-1]  # Last OpenGApps library available is 11.0, so force it if higher than that (eg: 12.0, 13.0, etc)

        self.dl_links = {
            "x86_64": f"https://downloads.sourceforge.net/project/opengapps/x86_64/20220503/open_gapps-x86_64-{version}-pico-20220503.zip",
            "x86": f"https://downloads.sourceforge.net/project/opengapps/x86/20220503/open_gapps-x86-{version}-pico-20220503.zip",
            "arm64-v8a": f"https://downloads.sourceforge.net/project/opengapps/arm64/20220503/open_gapps-arm64-{version}-pico-20220503.zip",
            "armeabi-v7a": f"https://downloads.sourceforge.net/project/opengapps/arm/20220215/open_gapps-arm-{version}-pico-20220215.zip"
        }
        self.arch = host()
        self.download_loc = get_download_dir()
        self.dl_link = self.dl_links[self.arch[0]]
        self.dl_file_name = os.path.join(self.download_loc, "open_gapps.zip")
        self.copy_dir = "./gapps"
        self.extract_to = "/tmp/ogapps/extract"
        self.non_apks = [
            "defaultetc-common.tar.lz",
            "defaultframework-common.tar.lz",
            "googlepixelconfig-common.tar.lz"
            ]
        self.skip = [
            "setupwizarddefault-x86_64.tar.lz",
            "setupwizardtablet-x86_64.tar.lz"
            ]

    def download(self):
        print_color("Downloading OpenGapps now .....", bcolors.GREEN)
        super().download()

    def copy(self):
        if os.path.exists(self.copy_dir):
            shutil.rmtree(self.copy_dir)
        if not os.path.exists(self.extract_to):
            os.makedirs(self.extract_to)
        if not os.path.exists(os.path.join(self.extract_to, "appunpack")):
            os.makedirs(os.path.join(self.extract_to, "appunpack"))

        for lz_file in os.listdir(os.path.join(self.extract_to, "Core")):
            for d in os.listdir(os.path.join(self.extract_to, "appunpack")):
                shutil.rmtree(os.path.join(self.extract_to, "appunpack", d))
            if lz_file not in self.skip:
                if lz_file not in self.non_apks:
                    print("    Processing app package : "+os.path.join(self.extract_to, "Core", lz_file))
                    run(["tar", "--lzip", "-xvf", os.path.join(self.extract_to, "Core", lz_file), "-C", os.path.join(self.extract_to, "appunpack")])
                    app_name = os.listdir(os.path.join(self.extract_to, "appunpack"))[0]
                    xx_dpi = os.listdir(os.path.join(self.extract_to, "appunpack", app_name))[0]
                    nodpi_path = os.path.join(self.extract_to, "appunpack", app_name, "nodpi")
                    if not os.path.exists(nodpi_path):
                        os.makedirs(nodpi_path)
                        print(f"    Created missing 'nodpi' directory: {nodpi_path}")
                    app_priv = os.listdir(nodpi_path)[0] if os.listdir(nodpi_path) else None
                    if app_priv:
                        app_src_dir = os.path.join(nodpi_path, app_priv)
                        for app in os.listdir(app_src_dir):
                            shutil.copytree(os.path.join(app_src_dir, app), os.path.join(self.copy_dir, "system", "priv-app", app), dirs_exist_ok=True)
                    else:
                        print(f"    [Warning] 'nodpi' directory is empty: {nodpi_path}")
                else:
                    print("    Processing extra package : "+os.path.join(self.extract_to, "Core", lz_file))
                    run(["tar", "--lzip", "-xvf", os.path.join(self.extract_to, "Core", lz_file), "-C", os.path.join(self.extract_to, "appunpack")])
                    app_name = os.listdir(os.path.join(self.extract_to, "appunpack"))[0]
                    common_content_dirs = os.listdir(os.path.join(self.extract_to, "appunpack", app_name, "common"))
                    for ccdir in common_content_dirs:
                        shutil.copytree(os.path.join(self.extract_to, "appunpack", app_name, "common", ccdir), os.path.join(self.copy_dir, "system", ccdir), dirs_exist_ok=True)
