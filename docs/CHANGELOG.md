# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-04-11

### Added
- 🎉 **Initial release** with core download and UI functionality  
- **Dual Download Engines**: Now powered by both `instaloader` and `yt-dlp`.
- **User-Selectable Downloader**: Choose your preferred download engine from the UI.
- **Automatic Fallback**: If one downloader fails, the app automatically switches to the other to ensure success.
- **Enhanced Reliability**: Improved download success rates for a wider range of Reels.

### Security
- Added SECURITY.md

---

## Guidelines for Contributors

When adding entries to this changelog:

1. **Group changes** by type using the categories above
2. **Write for humans** - use clear, descriptive language
3. **Include issue/PR numbers** when relevant: `Fixed login bug (#123)`
4. **Date format** should be YYYY-MM-DD
5. **Version format** should follow [Semantic Versioning](https://semver.org/)
6. **Keep entries concise** but informative

### Version Number Guidelines
- **Major** (X.y.z) - Breaking changes
- **Minor** (x.Y.z) - New features, backwards compatible
- **Patch** (x.y.Z) - Bug fixes, backwards compatible

### Example Entry Format
```markdown
## [1.2.3] - 2024-01-15

### Added
- New feature description (#PR-number)

### Fixed
- Bug fix description (fixes #issue-number)
```
