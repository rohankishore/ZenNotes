<h1 align="center" >ZenNotes</h1>


<div align="center">
  
  <a href="https://opensource.org/licenses/MIT">![License](https://img.shields.io/badge/License-MIT-yellow)</a>
  <a href="https://github.com/rohankishore/ZenNotes/releases">![Demo](https://img.shields.io/badge/Download-Now-indigo)</a>
  <a href="https://www.fiverr.com/rohancodespy/">![Demo](https://img.shields.io/badge/Fiverr-Hire-green)</a>
    <a style="text-decoration:none">
    <img src="https://img.shields.io/github/downloads/rohankishore/ZenNotes/total.svg"/>
  </a>

*_ZenNotes is being ported to macOS by @matthewyang204. Check the repo [here](https://github.com/matthewyang204/ZenNotes-Mac-Binaries)_*
  
</div>

## ✍️ What is ZenNotes? 
ZenNotes is a minimalistic Notepad app with a sleek design inspired by [Fluent Design](https://fluent2.microsoft.design/). It offers the familiar look of the Windows Notepad while having much more powerful features like Translate, TTS, etc.

![image](https://github.com/rohankishore/ZenNotes/assets/109947257/542f9d8a-8e02-4bfd-a469-f91e9873f60a)

![image](https://github.com/rohankishore/ZenNotes/assets/109947257/49edd3d1-08b9-472b-ae31-0982683687bb)

<br>

## 📃 Features

- Edit files (duh)
- Windows Fluent Design with Mica support
- Built-in Translation
- Text to Speech
- Encrypt and Decrypt
- Markdown support (Note: BR and HR may require closing tags to work)

<br>

## 👒 Getting Started

Let's get ZenNotes set up on your PC!

### Prerequisites
- Windows 10 x64 or later, a Linux distro running kernel 6.x or later, or macOS 11+
- Python 3.9 or later
- Python installation is bootstrapped with pip
- (Recommended) A fresh venv created with `python -m venv venv` and activated with `venv\Scripts\activate`
- The contents of `requirements.txt` installed via `pip install -r requirements.txt`
- (If building an installer) Inno Setup 6.4.3 or later

### Installation
You can download a prebuilt installer from the Releases or build one yourself. If using prebuilt installers, just skip to the use section.

#### Building the installer
1. Clone the repo or download a tarball
2. Install all prerequisites
3. `python build.py` to compile the program first
4. Open up the `.iss` Inno Setup script and compile it via Ctrl+F9 or `Build > Compile` - installer can be found in `Output` folder

##### Using the installer
Just run the `.exe` file, duh.

### Testing
This is for people who solely just want to run without installation for mostly testing purposes.

We need the prerequisites above. After getting them, you can run the program with `pythonw main.py` to run it without flooding your terminal with logging, or you can just run with `python main.py` to troubleshoot errors and debug it.

<br>

## 💖 Credits & Acknowledgements

This project was made possible because of [zhiyiYp](https://github.com/zhiyiYp)'s [PyQt-Fluent-Widgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets).

Icon Credit : [Fluent Icons](https://fluenticons.co/)

<br>


## 🪪 License

This project is licensed under the MIT License. See LICENSE.md for more info.

