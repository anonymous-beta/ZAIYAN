from setuptools import setup, find_packages

setup(
    name="zaiyan",
    version="1.0.0",
    description="Advanced Exploitation Framework — Made by Anonymous-beta for Zaiyan",
    author="Anonymous-beta",
    packages=find_packages(),
    install_requires=[
        "flask>=2.3.0",
        "flask-socketio>=5.3.0",
        "requests>=2.31.0",
        "cryptography>=41.0.0",
        "psutil>=5.9.0",
        "pyOpenSSL>=23.0.0",
        "pynacl>=1.5.0",
        "paramiko>=3.3.0",
        "pefile>=2023.0.0",
        "colorama>=0.4.6",
        "rich>=13.5.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "zaiyan=zaiyan:main",
        ],
    },
)
