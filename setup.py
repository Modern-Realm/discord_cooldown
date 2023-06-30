import re
import setuptools

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

with open("package/discord_cooldown/__init__.py") as f:
    search_v = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE)

    if search_v is not None:
        version = search_v.group(1)
    else:
        raise RuntimeError("Error occurred while installing !\n"
                           "go to https://github.com/Modern-Realm/discord_cooldown for more info ...")

packages = [
    "discord_cooldown",
    "discord_cooldown.ext"
]

setuptools.setup(
    name="discord-cooldown",
    version=version,
    author="P. Sai Keerthan Reddy",
    author_email="saikeerthan.keerthan.9@gmail.com",
    description="Custom Cooldowns for discord Bot commands",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Modern-Realm/discord_cooldown",
    project_urls={
        "Documentation": "https://modern-realm.github.io/discord_cooldown/",
        "Bug Tracker": "https://github.com/Modern-Realm/discord_cooldown/issues",
        "Examples": "https://github.com/Modern-Realm/discord_cooldown/tree/main/Examples",
        "Source": "https://github.com/Modern-Realm/discord_cooldown/tree/main/package/discord_cooldown",
        "Discord Server": "https://discord.gg/GVMWx5EaAN",
    },
    keywords=["cooldown", "custom-cooldown", "cooldowns",
              "py-cord", "nextcord", "disnake", "discordpy"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Topic :: Internet",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Typing :: Typed",
    ],
    license="MIT",
    packages=packages,
    include_package_data=True,
    install_requires=requirements,
    python_requires=">=3.8"
)
