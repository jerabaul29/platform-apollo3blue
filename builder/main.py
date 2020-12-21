# platform-apollo3blue: Apollo3Blue development platform for platformio.
# Copyright 2019-present NigelB
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from os.path import join, isdir
from pathlib import Path
from SCons.Script import AlwaysBuild, Builder, Default, DefaultEnvironment
import platform as sys_pf

env = DefaultEnvironment()
platform = env.PioPlatform()

upload_protocol = env.subst("$UPLOAD_PROTOCOL")
print("upload protocol: {}".format(upload_protocol))

FRAMEWORK_DIR = platform.get_package_dir("framework-mbedos-apollo3")
print("framework dir: {}".format(FRAMEWORK_DIR))
assert isdir(FRAMEWORK_DIR)

if upload_protocol.startswith("svl"):
    # TODO: fixme in a robust way
    # the path is user dependent; fix
    # assumes that the Artemis IDE package was installed in Arduino IDE; fix or give instructions
    upload_program = "/home/jrlab/.arduino15/packages/SparkFun/hardware/apollo3/2.0.3/tools/uploaders/svl/dist/linux/svl"
    print("upload program: {}".format(upload_program))
    assert(Path(upload_program).exists())
else:
    raise ValueError("Only SVL works reliably for now...")

upload_speed = env.subst("$UPLOAD_SPEED")

if len(upload_speed) == 0:
    upload_speed = "460800"

print("upload speed: {}".format(upload_speed))

upload_port = env.subst("$UPLOAD_PORT")
if len(upload_port) == 0:
    env.AutodetectUploadPort()

print("upload speed: {}".format(upload_port))

# A full list with the available variables
# http://www.scons.org/doc/production/HTML/scons-user.html#app-variables
env.Replace(
    AR="arm-none-eabi-ar",
    AS="arm-none-eabi-as",
    CC="arm-none-eabi-gcc",
    CXX="arm-none-eabi-g++",
    GDB="arm-none-eabi-gdb",
    OBJCOPY="arm-none-eabi-objcopy",
    RANLIB="arm-none-eabi-ranlib",
    SIZETOOL="arm-none-eabi-size",

    ARFLAGS=["rc"],

    UPLOADER=upload_program,
    UPLOADERFLAGS=[
        "$UPLOAD_PORT",
        "-b", upload_speed,
        "-f", "$SOURCES",
        "-v",
    ],
    UPLOADCMD="$UPLOADER $UPLOADERFLAGS"
)

env.Append(
    ARFLAGS=[],
    ASFLAGS=[],
    CCFLAGS=[],
    CXXFLAGS=["-std=gnu++11"],
    LINKFLAGS=[],
    CPPDEFINES=["PART_apollo3", "AM_PACKAGE_BGA", "AM_PART_APOLLO3", "ARDUINO_ARCH_APOLLO3"],
    LIBS=[],
    BUILDERS=dict(
        ElfToBin=Builder(
            action=" ".join([
                "$OBJCOPY",
                "-O",
                "binary",
                "$SOURCES",
                "$TARGET"]),
            suffix=".bin"
        )
    )
)

#
# Target: Build executable and linkable firmware
#
target_elf = env.BuildProgram()

#
# Target: Build the .bin file
#
target_bin = env.ElfToBin(join("$BUILD_DIR", "firmware"), target_elf)

#
# Target: Upload firmware
#
upload = env.Alias(["upload"], target_bin, "$UPLOADCMD")
AlwaysBuild(upload)

#
# Target: Define targets
#
Default(target_bin)
