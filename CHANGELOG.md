# Changelog

All notable changes to Julie Julie will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2025-05-22

### Fixed
- **Critical Syntax Error**: Resolved syntax error in `julie_julie_app.py` at line 261 that prevented application startup
- **Command Handler Logic**: Fixed improper `elif` chaining that referenced potentially undefined variables (`spotify_result`, `apple_result`)
- **Control Flow Issues**: Added missing return statements to prevent command fallthrough between handlers

### Changed
- **Command Processing Architecture**: Restructured `process_command_from_user()` function to use sequential handler checks with immediate returns
- **Handler Flow**: Each command handler now returns immediately upon successful processing, preventing conflicts
- **Error Prevention**: Eliminated the possibility of undefined variable references in handler chain

### Technical Details
- Converted nested `else` blocks to sequential `if` statements
- Added proper return statements after each handler processes a command
- Improved code maintainability and debugging capabilities
- Enhanced error handling and logging throughout the command processing chain

### Command Processing Order (Updated)
1. Time commands → immediate return
2. Calculation commands → immediate return if matched
3. Visualizer commands → immediate return if matched
4. Spotify commands → immediate return if matched
5. Apple Music commands → immediate return if matched
6. YouTube commands → immediate return if matched
7. Weather commands → immediate return if matched
8. Everything else → Ollama AI conversation → return

### Migration Notes
- No user-facing changes required
- All existing commands continue to work as before
- Improved reliability and reduced potential for handler conflicts

## [0.3.x] - Previous Versions

### Features Present Before v0.4.0
- Menu bar integration with rumps
- Flask web server for HTTP API
- Voice Control integration via Shortcuts
- Time command handling
- Weather integration with National Weather Service API
- Calculation handler for mathematical expressions
- Spotify and Apple Music control
- YouTube search and browser integration
- Visualizer for data visualization
- Ollama integration for AI conversations with streaming responses
- Real-time text-to-speech synthesis
- Terminal testing interface

### Known Issues Before v0.4.0
- Syntax error preventing application startup
- Potential handler conflicts due to improper control flow
- Command fallthrough causing unexpected behavior

---

## Version Format

- **Major.Minor.Patch** (e.g., 1.0.0)
- **Major**: Breaking changes or significant architectural updates
- **Minor**: New features, backward-compatible changes
- **Patch**: Bug fixes, small improvements

## Categories

- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security improvements
