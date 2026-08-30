# Smart File Organizer 🗂️

A powerful, cross-platform Python tool to automatically organize files in a directory by category (images, videos, documents, audio, archives, code, etc.). Features duplicate handling, customizable categories, and a clean CLI interface.

## ✨ Features

- **Automatic Categorization** - Organizes 15+ file categories with 200+ extensions
- **Smart Duplicate Handling** - Auto-rename, custom rename, or delete options
- **Cross-Platform** - Works on Windows, macOS, and Linux
- **Configurable** - Easy to extend categories via JSON config
- **Safe Operations** - Comprehensive error handling, permission checks, and validation
- **Docker Support** - Run in containerized environments
- **GitHub Actions CI** - Automated testing and validation

## 📦 Installation

### From Source
```bash
git clone https://github.com/alirezaazmode2007-create/smart-file-organizer.git
cd smart-file-organizer
pip install -e .
```

### Via pip (after publishing to PyPI)
```bash
pip install smart-file-organizer
```

### Using Docker
```bash
# Build locally
docker build -t smart-file-organizer .
docker run -v /path/to/your/files:/data smart-file-organizer /data

# Or pull from GitHub Container Registry (after publishing)
docker pull ghcr.io/alirezaazmode2007-create/smart-file-organizer:latest
docker run -v /path/to/your/files:/data ghcr.io/alirezaazmode2007-create/smart-file-organizer:latest /data
```

### Development Install
```bash
pip install -e ".[dev]"
```

## 🚀 Quick Start

```bash
# Interactive mode
python -m smart_file_organizer

# Or run directly
python main.py
```

Then enter the directory path you want to organize.

## 📁 Supported Categories

| Category | Icon | Extensions |
|----------|------|------------|
| Images | 🖼️ | jpg, png, gif, webp, svg, heic, raw, psd, ai, ... |
| Videos | 🎬 | mp4, mkv, avi, mov, webm, flv, m4v, ... |
| Documents | 📄 | pdf, docx, txt, md, xlsx, pptx, csv, xml, ... |
| Audio | 🎵 | mp3, wav, flac, aac, ogg, m4a, opus, ... |
| Archives | 📦 | zip, rar, 7z, tar, gz, bz2, xz, iso, dmg, ... |
| Code | 💻 | py, js, html, css, java, cpp, go, rs, ts, json, yaml, ... |
| Executables | ⚙️ | exe, msi, app, deb, rpm, sh, bat, ... |
| Fonts | 🔤 | ttf, otf, woff, woff2, eot, ... |
| Databases | 🗄️ | db, sqlite, mdb, accdb, ... |
| Emails | 📧 | eml, msg, pst, ost, mbox, ... |
| Web | 🌐 | html, htm, xml, rss, url, webloc, ... |
| System | 🖥️ | dll, sys, drv, inf, log, tmp, bak, ... |
| 3D Models | 🎨 | stl, obj, fbx, blend, step, dxf, dwg, ... |
| Disk Images | 💾 | iso, img, vhd, vmdk, qcow2, ... |
| Others | 📎 | torrent, nfo, srt, sub, m3u, ... |

## ⚙️ Configuration

Edit `config/categories.json` to customize categories, extensions, folder names, and icons.

```json
{
  "custom_category": {
    "extensions": [".myext"],
    "folder_name": "Custom",
    "icon": "⭐"
  }
}
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=smart_file_organizer --cov-report=html

# Run specific test file
pytest tests/test_organizer.py -v
```

## 🐳 Docker Usage

```bash
# Build image
docker build -t smart-file-organizer .

# Run on a directory
docker run --rm -v "$(pwd)/test_files:/data" smart-file-organizer /data

# Run with custom config
docker run --rm -v "$(pwd)/config:/app/config" -v "/my/files:/data" smart-file-organizer /data
```

## 📋 Requirements

- Python 3.8+
- No external dependencies (stdlib only)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- Inspired by the need for a simple, reliable file organizer
- Built with Python standard library only

---

**Made with ❤️ for developers who love clean directories**