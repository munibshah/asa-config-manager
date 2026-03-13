from setuptools import setup, find_packages

setup(
    name="asa-config-manager",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "netmiko>=4.3.0",
        "paramiko>=3.4.0",
        "PyYAML>=6.0.1",
        "python-dotenv>=1.0.0",
        "cryptography>=41.0.0",
    ],
    python_requires=">=3.8",
    description="ASA config manager for VLAN and interface changes",
    author="Munib Shah",
    author_email="munibshah@example.com",
    url="https://github.com/munibshah/asa-config-manager",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
