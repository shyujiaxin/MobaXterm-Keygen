# /usr/bin/env python3
"""
Author: Double Sine
License: GPLv3
Modified by: jasonyu
Supports automatic recognition of the latest version
"""
import os, sys, zipfile

VariantBase64Table = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
VariantBase64Dict = {i: VariantBase64Table[i] for i in range(len(VariantBase64Table))}
VariantBase64ReverseDict = {VariantBase64Table[i]: i for i in range(len(VariantBase64Table))}


def VariantBase64Encode(bs: bytes):
    result = b""
    blocks_count, left_bytes = divmod(len(bs), 3)

    for i in range(blocks_count):
        coding_int = int.from_bytes(bs[3 * i : 3 * i + 3], "little")
        block = VariantBase64Dict[coding_int & 0x3F]
        block += VariantBase64Dict[(coding_int >> 6) & 0x3F]
        block += VariantBase64Dict[(coding_int >> 12) & 0x3F]
        block += VariantBase64Dict[(coding_int >> 18) & 0x3F]
        result += block.encode()

    if left_bytes == 0:
        return result
    elif left_bytes == 1:
        coding_int = int.from_bytes(bs[3 * blocks_count :], "little")
        block = VariantBase64Dict[coding_int & 0x3F]
        block += VariantBase64Dict[(coding_int >> 6) & 0x3F]
        result += block.encode()
        return result
    else:
        coding_int = int.from_bytes(bs[3 * blocks_count :], "little")
        block = VariantBase64Dict[coding_int & 0x3F]
        block += VariantBase64Dict[(coding_int >> 6) & 0x3F]
        block += VariantBase64Dict[(coding_int >> 12) & 0x3F]
        result += block.encode()
        return result


def VariantBase64Decode(s: str):
    result = b""
    blocks_count, left_bytes = divmod(len(s), 4)

    for i in range(blocks_count):
        block = VariantBase64ReverseDict[s[4 * i]]
        block += VariantBase64ReverseDict[s[4 * i + 1]] << 6
        block += VariantBase64ReverseDict[s[4 * i + 2]] << 12
        block += VariantBase64ReverseDict[s[4 * i + 3]] << 18
        result += block.to_bytes(3, "little")

    if left_bytes == 0:
        return result
    elif left_bytes == 2:
        block = VariantBase64ReverseDict[s[4 * blocks_count]]
        block += VariantBase64ReverseDict[s[4 * blocks_count + 1]] << 6
        result += block.to_bytes(1, "little")
        return result
    elif left_bytes == 3:
        block = VariantBase64ReverseDict[s[4 * blocks_count]]
        block += VariantBase64ReverseDict[s[4 * blocks_count + 1]] << 6
        block += VariantBase64ReverseDict[s[4 * blocks_count + 2]] << 12
        result += block.to_bytes(2, "little")
        return result
    else:
        raise ValueError("Invalid encoding.")


def EncryptBytes(key: int, bs: bytes):
    result = bytearray()
    for i in range(len(bs)):
        result.append(bs[i] ^ ((key >> 8) & 0xFF))
        key = result[-1] & key | 0x482D
    return bytes(result)


def DecryptBytes(key: int, bs: bytes):
    result = bytearray()
    for i in range(len(bs)):
        result.append(bs[i] ^ ((key >> 8) & 0xFF))
        key = bs[i] & key | 0x482D
    return bytes(result)


class LicenseType:
    Professional = 1
    Educational = 3
    Persional = 4


def GenerateLicense(Type: LicenseType, Count: int, UserName: str, MajorVersion: int, MinorVersion):
    assert Count >= 0
    LicenseString = "%d#%s|%d%d#%d#%d3%d6%d#%d#%d#%d#" % (
        Type,
        UserName,
        MajorVersion,
        MinorVersion,
        Count,
        MajorVersion,
        MinorVersion,
        MinorVersion,
        0,  # Unknown
        0,  # No Games flag. 0 means "NoGames = false". But it does not work.
        0,
    )  # No Plugins flag. 0 means "NoPlugins = false". But it does not work.
    EncodedLicenseString = VariantBase64Encode(EncryptBytes(0x787, LicenseString.encode())).decode()
    with zipfile.ZipFile("Custom.mxtpro", "w") as f:
        f.writestr("Pro.key", data=EncodedLicenseString)


def help():
    print("Usage:")
    print("    MobaXterm-Keygen.py <UserName> <Version>")
    print()
    print("    <UserName>:      The Name licensed to")
    print("    <Version>:       The Version of MobaXterm")
    print("                     Example:    10.9")
    print()


if __name__ == "__main__":
    import os
    import re

    # Find the latest MobaXterm executable in the current directory
    if sys.executable.endswith("python.exe"):
        os.chdir(os.path.dirname(__file__))
    else:
        os.chdir(os.path.dirname(sys.executable))
    print(os.getcwd())
    latest_moba_exe = None
    latest_moba_version = None
    for file in os.listdir():
        if file.lower().startswith("mobaxterm") and file.lower().endswith(".exe"):
            # Extract version from the file name
            print(file)
            match = re.search(r"_(\d+\.\d+)(?=\.\w+$)", file)
            if match:
                version = match.group(1)
                if latest_moba_version is None or version > latest_moba_version:
                    latest_moba_exe = file
                    latest_moba_version = version

    if latest_moba_exe:
        print(f"Found the latest MobaXterm executable: {latest_moba_exe}")
        print(f"Version: {latest_moba_version}")
    else:
        print("No MobaXterm executable found in the current directory.")
    if latest_moba_version is None:
        print("No MobaXterm version found.")
        input("Press Enter to continue...")
        sys.exit(0)
    else:
        MajorVersion, MinorVersion = map(int, latest_moba_version.split("."))
        MajorVersion = int(MajorVersion)
        MinorVersion = int(MinorVersion)
        GenerateLicense(LicenseType.Professional, 1000, "user", MajorVersion, MinorVersion)
        print("[*] Success!")
        print("[*] File generated: %s" % os.path.join(os.getcwd(), "Custom.mxtpro"))
        print("[*] Please move or copy the newly-generated file to MobaXterm's installation path.")
        print()
        user_input = input("Do you want to remove all but the latest MobaXterm executable? (y/yes): ")
        if user_input.lower() in ["y", "yes"]:
            for file in os.listdir():
                if re.match(r"^mobaxterm.*\.exe$", file.lower()) and file not in [
                    latest_moba_exe,
                    os.path.basename(sys.executable),
                ]:
                    os.remove(file)
                    print(f"Removed {file}")
            print("All but the latest MobaXterm executable have been removed.")
            rename_input = input("Do you want to rename the latest MobaXterm executable to 'mobaxterm.exe'? (y/yes): ")
            if rename_input.lower() in ["y", "yes"]:
                os.rename(latest_moba_exe, "MobaXterm.exe")
                print(f"Renamed {latest_moba_exe} to 'MobaXterm.exe'")
            else:
                print("No renaming done.")
        else:
            print("No files removed.")
else:
    print("[*] ERROR: Please run this script directly")
