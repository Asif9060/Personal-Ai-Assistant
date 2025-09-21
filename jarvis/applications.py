"""
JARVIS Application Discovery and Launcher System

This module automatically discovers all applications installed on Windows PC including:
- System applications
- Installed programs (Program Files)
- Windows Store apps
- Games (Steam, Epic, etc.)
- Start Menu shortcuts
- Desktop applications

Provides intelligent fuzzy matching for natural voice commands.
"""

import os
import sys
import json
import re
import subprocess
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

# Windows-specific imports
if sys.platform == "win32":
    try:
        import winreg
        import psutil
        from fuzzywuzzy import fuzz, process
        WINDOWS_AVAILABLE = True
    except ImportError as e:
        print(f"[APP] Windows dependencies not available: {e}")
        WINDOWS_AVAILABLE = False
else:
    WINDOWS_AVAILABLE = False


@dataclass
class Application:
    """Represents a discovered application"""
    name: str
    display_name: str
    path: str
    launch_command: str
    app_type: str  # 'exe', 'uwp', 'shortcut', 'steam', 'epic'
    description: str = ""
    icon_path: str = ""
    install_location: str = ""
    publisher: str = ""
    version: str = ""
    keywords: List[str] = None
    last_used: Optional[datetime] = None

    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []


class ApplicationDiscovery:
    """Discovers and catalogs all applications on the Windows system"""

    def __init__(self):
        self.applications: Dict[str, Application] = {}
        self.cache_file = Path("jarvis_applications.json")
        self.cache_duration = timedelta(hours=6)  # Refresh cache every 6 hours
        self.discovery_sources = {
            'registry_uninstall': True,
            'start_menu': True,
            'program_files': True,
            'uwp_apps': True,
            'steam_apps': True,
            'epic_games': True,
            'desktop_shortcuts': True,
            'system_apps': True
        }

    def discover_all_applications(self, use_cache: bool = True) -> Dict[str, Application]:
        """Discover all applications on the system"""
        if not WINDOWS_AVAILABLE:
            print("[APP] Windows-specific features not available")
            return {}

        # Check cache first
        if use_cache and self._is_cache_valid():
            print("[APP] Loading applications from cache...")
            return self._load_from_cache()

        print("[APP] Discovering applications on your system...")
        self.applications.clear()

        # Discovery methods
        discovery_methods = [
            ('Registry (Uninstall)', self._discover_from_registry),
            ('Start Menu', self._discover_from_start_menu),
            ('Program Files', self._discover_from_program_files),
            ('UWP Apps', self._discover_uwp_applications),
            ('Steam Games', self._discover_steam_applications),
            ('Epic Games', self._discover_epic_applications),
            ('Desktop Shortcuts', self._discover_desktop_shortcuts),
            ('System Applications', self._discover_system_applications)
        ]

        for source_name, method in discovery_methods:
            try:
                print(f"[APP] Scanning {source_name}...")
                found_count = len(self.applications)
                method()
                new_count = len(self.applications) - found_count
                print(
                    f"[APP] Found {new_count} applications from {source_name}")
            except Exception as e:
                print(f"[APP] Error scanning {source_name}: {e}")

        # Process and clean up discovered applications
        self._process_discovered_applications()

        # Save to cache
        self._save_to_cache()

        print(
            f"[APP] Discovery complete! Found {len(self.applications)} applications")
        return self.applications

    def _discover_from_registry(self):
        """Discover applications from Windows Registry with timeout protection"""
        import time
        start_time = time.time()
        timeout = 15  # 15 second timeout for registry scan
        processed_count = 0

        registry_paths = [
            (winreg.HKEY_LOCAL_MACHINE,
             r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE,
             r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER,
             r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
        ]

        for hkey, reg_path in registry_paths:
            if time.time() - start_time > timeout:
                print(
                    f"[APP] Registry scan timeout after processing {processed_count} entries")
                break

            try:
                with winreg.OpenKey(hkey, reg_path) as key:
                    key_count = winreg.QueryInfoKey(key)[0]
                    for i in range(key_count):
                        if time.time() - start_time > timeout:
                            print(
                                f"[APP] Registry scan timeout after processing {processed_count} entries")
                            return

                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, subkey_name) as subkey:
                                app_info = self._extract_registry_app_info(
                                    subkey)
                                if app_info:
                                    app_id = f"registry_{subkey_name.lower()}"
                                    self.applications[app_id] = app_info
                                processed_count += 1
                        except (OSError, PermissionError):
                            continue
            except (OSError, PermissionError):
                continue

    def _extract_registry_app_info(self, subkey) -> Optional[Application]:
        """Extract application info from registry subkey"""
        try:
            # Get basic info
            display_name = self._get_registry_value(subkey, "DisplayName")
            if not display_name or display_name.startswith("KB") or display_name.startswith("Security Update"):
                return None

            install_location = self._get_registry_value(
                subkey, "InstallLocation") or ""
            display_icon = self._get_registry_value(
                subkey, "DisplayIcon") or ""
            publisher = self._get_registry_value(subkey, "Publisher") or ""
            version = self._get_registry_value(subkey, "DisplayVersion") or ""

            # Try to find executable
            exe_path = ""
            launch_command = ""

            # Check InstallLocation for main executable
            if install_location and os.path.exists(install_location):
                try:
                    install_path = Path(install_location)
                    # Limit search depth to avoid performance issues
                    exe_files = []
                    try:
                        # Search only first 2 levels to avoid deep recursion
                        for pattern in ["*.exe", "*/*.exe", "*/*/*.exe"]:
                            exe_files.extend(list(install_path.glob(pattern)))
                            if len(exe_files) >= 10:  # Limit to first 10 exe files
                                break
                    except (OSError, PermissionError):
                        pass

                    if exe_files:
                        # Prefer exe with same name as app, or first one found
                        app_name_clean = re.sub(
                            r'[^\w\s]', '', display_name).lower()
                        for exe in exe_files:
                            if app_name_clean in exe.stem.lower():
                                exe_path = str(exe)
                                break
                        if not exe_path:
                            exe_path = str(exe_files[0])
                except (OSError, PermissionError, Exception):
                    # Skip if we can't access the directory
                    pass

            # Check DisplayIcon for executable path
            if not exe_path and display_icon:
                icon_path = display_icon.split(',')[0].strip('"')
                if icon_path.endswith('.exe') and os.path.exists(icon_path):
                    exe_path = icon_path

            if exe_path:
                launch_command = f'"{exe_path}"'
            elif install_location:
                launch_command = install_location
            else:
                return None

            # Generate keywords
            keywords = self._generate_keywords(display_name, publisher)

            return Application(
                name=self._clean_app_name(display_name),
                display_name=display_name,
                path=exe_path or install_location,
                launch_command=launch_command,
                app_type="exe",
                description=f"Installed application by {publisher}" if publisher else "Installed application",
                icon_path=display_icon,
                install_location=install_location,
                publisher=publisher,
                version=version,
                keywords=keywords
            )

        except Exception:
            return None

    def _discover_from_start_menu(self):
        """Discover applications from Start Menu"""
        start_menu_paths = [
            os.path.expandvars(
                r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
            os.path.expandvars(
                r"%PROGRAMDATA%\Microsoft\Windows\Start Menu\Programs")
        ]

        for start_path in start_menu_paths:
            if os.path.exists(start_path):
                for root, dirs, files in os.walk(start_path):
                    for file in files:
                        if file.endswith('.lnk'):
                            try:
                                shortcut_path = os.path.join(root, file)
                                app_info = self._process_shortcut(
                                    shortcut_path)
                                if app_info:
                                    app_id = f"startmenu_{file.lower()}"
                                    self.applications[app_id] = app_info
                            except Exception:
                                continue

    def _discover_from_program_files(self):
        """Discover applications from Program Files directories"""
        program_dirs = [
            os.environ.get('PROGRAMFILES', r'C:\Program Files'),
            os.environ.get('PROGRAMFILES(X86)', r'C:\Program Files (x86)'),
            os.environ.get('LOCALAPPDATA', r'C:\Users\{user}\AppData\Local')
        ]

        for prog_dir in program_dirs:
            if os.path.exists(prog_dir):
                try:
                    for item in os.listdir(prog_dir):
                        item_path = os.path.join(prog_dir, item)
                        if os.path.isdir(item_path):
                            # Look for main executable in app directory
                            exe_files = list(Path(item_path).glob("*.exe"))
                            if exe_files:
                                # Find the most likely main executable
                                main_exe = self._find_main_executable(
                                    exe_files, item)
                                if main_exe:
                                    app_info = self._create_app_from_exe(
                                        main_exe, item)
                                    if app_info:
                                        app_id = f"programfiles_{item.lower()}"
                                        self.applications[app_id] = app_info
                except (PermissionError, OSError):
                    continue

    def _discover_uwp_applications(self):
        """Discover UWP (Windows Store) applications"""
        try:
            # Use PowerShell to get UWP apps
            ps_command = """
            Get-AppxPackage | Where-Object { $_.Name -notlike "*Microsoft*" -and $_.Name -notlike "*Windows*" } |
            Select-Object Name, PackageFullName, InstallLocation, DisplayName |
            ConvertTo-Json
            """

            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0 and result.stdout.strip():
                import json
                uwp_apps = json.loads(result.stdout)
                if isinstance(uwp_apps, dict):
                    uwp_apps = [uwp_apps]

                for app in uwp_apps:
                    if app.get('DisplayName'):
                        display_name = app['DisplayName']
                        package_name = app.get('PackageFullName', '')

                        app_info = Application(
                            name=self._clean_app_name(display_name),
                            display_name=display_name,
                            path=app.get('InstallLocation', ''),
                            launch_command=f"explorer.exe shell:appsFolder\\{package_name}!App",
                            app_type="uwp",
                            description="Windows Store App",
                            keywords=self._generate_keywords(
                                display_name, "Microsoft Store")
                        )

                        app_id = f"uwp_{app['Name'].lower()}"
                        self.applications[app_id] = app_info

        except Exception as e:
            print(f"[APP] UWP discovery error: {e}")

    def _discover_steam_applications(self):
        """Discover Steam games"""
        steam_paths = [
            r"C:\Program Files (x86)\Steam",
            r"C:\Program Files\Steam",
            os.path.expanduser(r"~\AppData\Local\Steam")
        ]

        for steam_path in steam_paths:
            if os.path.exists(steam_path):
                try:
                    # Look for steamapps directory
                    steamapps_path = os.path.join(steam_path, "steamapps")
                    if os.path.exists(steamapps_path):
                        # Read appmanifest files
                        for file in os.listdir(steamapps_path):
                            if file.startswith("appmanifest_") and file.endswith(".acf"):
                                try:
                                    manifest_path = os.path.join(
                                        steamapps_path, file)
                                    game_info = self._parse_steam_manifest(
                                        manifest_path)
                                    if game_info:
                                        app_id = f"steam_{game_info.name.lower()}"
                                        self.applications[app_id] = game_info
                                except Exception:
                                    continue
                except Exception:
                    continue

    def _discover_epic_applications(self):
        """Discover Epic Games applications"""
        epic_path = os.path.expanduser(
            r"~\AppData\Local\EpicGamesLauncher\Saved\Config\Windows")
        if os.path.exists(epic_path):
            # Epic Games discovery would require parsing their manifest files
            # This is a simplified version
            pass

    def _discover_desktop_shortcuts(self):
        """Discover applications from desktop shortcuts"""
        desktop_path = os.path.expanduser("~/Desktop")
        if os.path.exists(desktop_path):
            for file in os.listdir(desktop_path):
                if file.endswith('.lnk'):
                    try:
                        shortcut_path = os.path.join(desktop_path, file)
                        app_info = self._process_shortcut(shortcut_path)
                        if app_info:
                            app_id = f"desktop_{file.lower()}"
                            self.applications[app_id] = app_info
                    except Exception:
                        continue

    def _discover_system_applications(self):
        """Discover common system applications"""
        system_apps = {
            "notepad": {
                "name": "notepad",
                "display_name": "Notepad",
                "command": "notepad.exe",
                "description": "Text editor"
            },
            "calculator": {
                "name": "calculator",
                "display_name": "Calculator",
                "command": "calc.exe",
                "description": "Calculator"
            },
            "paint": {
                "name": "paint",
                "display_name": "Paint",
                "command": "mspaint.exe",
                "description": "Image editor"
            },
            "cmd": {
                "name": "command prompt",
                "display_name": "Command Prompt",
                "command": "cmd.exe",
                "description": "Command line interface"
            },
            "powershell": {
                "name": "powershell",
                "display_name": "Windows PowerShell",
                "command": "powershell.exe",
                "description": "Advanced command line"
            },
            "explorer": {
                "name": "file explorer",
                "display_name": "File Explorer",
                "command": "explorer.exe",
                "description": "File manager"
            },
            "control": {
                "name": "control panel",
                "display_name": "Control Panel",
                "command": "control.exe",
                "description": "System settings"
            },
            "msconfig": {
                "name": "system configuration",
                "display_name": "System Configuration",
                "command": "msconfig.exe",
                "description": "System configuration utility"
            },
            "taskmgr": {
                "name": "task manager",
                "display_name": "Task Manager",
                "command": "taskmgr.exe",
                "description": "Process manager"
            }
        }

        for app_id, app_data in system_apps.items():
            app_info = Application(
                name=app_data["name"],
                display_name=app_data["display_name"],
                path=app_data["command"],
                launch_command=app_data["command"],
                app_type="system",
                description=app_data["description"],
                keywords=self._generate_keywords(
                    app_data["display_name"], "Microsoft")
            )
            self.applications[f"system_{app_id}"] = app_info

    def _process_shortcut(self, shortcut_path: str) -> Optional[Application]:
        """Process a .lnk shortcut file"""
        try:
            # Use PowerShell to read shortcut properties
            ps_command = f'''
            $shell = New-Object -ComObject WScript.Shell
            $shortcut = $shell.CreateShortcut("{shortcut_path}")
            $shortcut | Select-Object TargetPath, Arguments, Description, WorkingDirectory | ConvertTo-Json
            '''

            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0 and result.stdout.strip():
                import json
                shortcut_info = json.loads(result.stdout)

                target_path = shortcut_info.get('TargetPath', '')
                if target_path and os.path.exists(target_path):
                    file_name = os.path.splitext(
                        os.path.basename(shortcut_path))[0]

                    # Build launch command
                    launch_command = f'"{target_path}"'
                    if shortcut_info.get('Arguments'):
                        launch_command += f" {shortcut_info['Arguments']}"

                    return Application(
                        name=self._clean_app_name(file_name),
                        display_name=file_name,
                        path=target_path,
                        launch_command=launch_command,
                        app_type="shortcut",
                        description=shortcut_info.get(
                            'Description', 'Desktop shortcut'),
                        keywords=self._generate_keywords(file_name, "")
                    )
        except Exception:
            pass
        return None

    def _parse_steam_manifest(self, manifest_path: str) -> Optional[Application]:
        """Parse Steam app manifest file"""
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract game name and install dir
            name_match = re.search(r'"name"\s*"([^"]+)"', content)
            installdir_match = re.search(r'"installdir"\s*"([^"]+)"', content)
            appid_match = re.search(r'"appid"\s*"([^"]+)"', content)

            if name_match and installdir_match and appid_match:
                game_name = name_match.group(1)
                install_dir = installdir_match.group(1)
                app_id = appid_match.group(1)

                return Application(
                    name=self._clean_app_name(game_name),
                    display_name=game_name,
                    path=f"steam://rungameid/{app_id}",
                    launch_command=f"steam://rungameid/{app_id}",
                    app_type="steam",
                    description="Steam Game",
                    keywords=self._generate_keywords(game_name, "Steam")
                )
        except Exception:
            pass
        return None

    def _find_main_executable(self, exe_files: List[Path], app_dir_name: str) -> Optional[Path]:
        """Find the main executable from a list of exe files"""
        # Skip installers, uninstallers, and utilities
        skip_patterns = [
            'uninstall', 'setup', 'install', 'updater', 'launcher',
            'helper', 'crash', 'report', 'service', 'daemon'
        ]

        # Filter out likely non-main executables
        candidates = []
        for exe in exe_files:
            exe_name_lower = exe.stem.lower()
            if not any(pattern in exe_name_lower for pattern in skip_patterns):
                candidates.append(exe)

        if not candidates:
            return None

        # Prefer exe with name similar to directory
        app_name_clean = re.sub(r'[^\w]', '', app_dir_name).lower()
        for exe in candidates:
            exe_name_clean = re.sub(r'[^\w]', '', exe.stem).lower()
            if app_name_clean in exe_name_clean or exe_name_clean in app_name_clean:
                return exe

        # Return first candidate
        return candidates[0]

    def _create_app_from_exe(self, exe_path: Path, app_name: str) -> Optional[Application]:
        """Create application info from executable path"""
        try:
            if exe_path.exists():
                return Application(
                    name=self._clean_app_name(app_name),
                    display_name=app_name,
                    path=str(exe_path),
                    launch_command=f'"{exe_path}"',
                    app_type="exe",
                    description="Installed application",
                    keywords=self._generate_keywords(app_name, "")
                )
        except Exception:
            pass
        return None

    def _clean_app_name(self, name: str) -> str:
        """Clean and normalize application name"""
        # Remove version numbers, company names in parentheses, etc.
        name = re.sub(r'\s*\([^)]*\)', '', name)  # Remove (...)
        name = re.sub(r'\s*\[[^\]]*\]', '', name)  # Remove [...]
        name = re.sub(r'\s*v?\d+\.[\d\.]+.*$', '',
                      name)  # Remove version numbers
        name = re.sub(r'\s+', ' ', name).strip()  # Normalize whitespace
        return name.lower()

    def _generate_keywords(self, name: str, publisher: str) -> List[str]:
        """Generate search keywords for an application"""
        keywords = []

        # Add the name itself
        keywords.append(name.lower())

        # Add words from the name
        words = re.findall(r'\w+', name.lower())
        keywords.extend(words)

        # Add publisher
        if publisher:
            keywords.append(publisher.lower())
            pub_words = re.findall(r'\w+', publisher.lower())
            keywords.extend(pub_words)

        # Add common abbreviations
        if len(words) > 1:
            # First letters abbreviation
            abbreviation = ''.join(word[0] for word in words if word)
            if len(abbreviation) > 1:
                keywords.append(abbreviation)

        # Remove duplicates and short words
        keywords = list(set(kw for kw in keywords if len(kw) > 1))

        return keywords

    def _get_registry_value(self, key, value_name: str) -> Optional[str]:
        """Get a value from registry key"""
        try:
            value, _ = winreg.QueryValueEx(key, value_name)
            return str(value) if value else None
        except (OSError, FileNotFoundError):
            return None

    def _process_discovered_applications(self):
        """Process and clean up discovered applications"""
        # Remove duplicates based on similar names and paths
        unique_apps = {}

        for app_id, app in self.applications.items():
            # Skip empty or invalid apps
            if not app.name or not app.launch_command:
                continue

            # Create a key for deduplication
            dedup_key = (app.name, app.path.lower() if app.path else "")

            if dedup_key not in unique_apps:
                unique_apps[dedup_key] = app
            else:
                # Keep the one with more complete information
                existing = unique_apps[dedup_key]
                if len(app.description) > len(existing.description) or app.app_type != "shortcut":
                    unique_apps[dedup_key] = app

        # Rebuild applications dict
        self.applications = {f"app_{i}": app for i,
                             app in enumerate(unique_apps.values())}

    def _is_cache_valid(self) -> bool:
        """Check if cache file exists and is recent enough"""
        if not self.cache_file.exists():
            return False

        cache_time = datetime.fromtimestamp(self.cache_file.stat().st_mtime)
        return datetime.now() - cache_time < self.cache_duration

    def _load_from_cache(self) -> Dict[str, Application]:
        """Load applications from cache file"""
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.applications = {}
            for app_id, app_data in data.items():
                # Convert back to Application object
                app_data['keywords'] = app_data.get('keywords', [])
                self.applications[app_id] = Application(**app_data)

            return self.applications
        except Exception as e:
            print(f"[APP] Cache load error: {e}")
            return {}

    def _save_to_cache(self):
        """Save applications to cache file"""
        try:
            cache_data = {}
            for app_id, app in self.applications.items():
                cache_data[app_id] = asdict(app)
                # Convert datetime to string for JSON serialization
                if cache_data[app_id]['last_used']:
                    cache_data[app_id]['last_used'] = cache_data[app_id]['last_used'].isoformat(
                    )

            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)

            print(f"[APP] Applications cached to {self.cache_file}")
        except Exception as e:
            print(f"[APP] Cache save error: {e}")


class ApplicationLauncher:
    """Handles launching applications with fuzzy matching"""

    def __init__(self, discovery: ApplicationDiscovery):
        self.discovery = discovery
        self.applications = {}
        self.refresh_apps()

    def refresh_apps(self):
        """Refresh the application list"""
        self.applications = self.discovery.discover_all_applications()

    def find_application(self, query: str, threshold: int = 70) -> List[Tuple[Application, int]]:
        """Find applications matching the query using fuzzy matching"""
        if not self.applications:
            return []

        # Prepare search candidates
        candidates = []
        for app in self.applications.values():
            # Add display name
            candidates.append((app.display_name, app))
            # Add cleaned name
            candidates.append((app.name, app))
            # Add keywords
            for keyword in app.keywords:
                candidates.append((keyword, app))

        # Perform fuzzy matching
        matches = []
        query_lower = query.lower()

        for candidate_text, app in candidates:
            # Calculate similarity scores
            ratio = fuzz.ratio(query_lower, candidate_text.lower())
            partial_ratio = fuzz.partial_ratio(
                query_lower, candidate_text.lower())
            token_sort_ratio = fuzz.token_sort_ratio(
                query_lower, candidate_text.lower())

            # Use highest score
            best_score = max(ratio, partial_ratio, token_sort_ratio)

            if best_score >= threshold:
                matches.append((app, best_score))

        # Remove duplicates and sort by score
        unique_matches = {}
        for app, score in matches:
            key = (app.name, app.path)
            if key not in unique_matches or unique_matches[key][1] < score:
                unique_matches[key] = (app, score)

        # Sort by score (descending)
        sorted_matches = sorted(unique_matches.values(),
                                key=lambda x: x[1], reverse=True)

        return sorted_matches[:10]  # Return top 10 matches

    def launch_application(self, app: Application) -> bool:
        """Launch an application"""
        try:
            print(f"[APP] Launching {app.display_name}...")

            if app.app_type == "uwp":
                # UWP app
                subprocess.Popen(app.launch_command, shell=True)
            elif app.app_type == "steam":
                # Steam game
                subprocess.Popen(app.launch_command, shell=True)
            elif app.app_type == "system":
                # System application
                subprocess.Popen(app.launch_command, shell=True)
            else:
                # Regular executable or shortcut
                if app.path and os.path.exists(app.path):
                    if app.install_location and os.path.exists(app.install_location):
                        # Launch from install directory
                        subprocess.Popen(app.launch_command,
                                         shell=True, cwd=app.install_location)
                    else:
                        subprocess.Popen(app.launch_command, shell=True)
                else:
                    # Try launch command directly
                    subprocess.Popen(app.launch_command, shell=True)

            # Update last used time
            app.last_used = datetime.now()
            print(f"[APP] Successfully launched {app.display_name}")
            return True

        except Exception as e:
            print(f"[APP] Failed to launch {app.display_name}: {e}")
            return False

    def launch_by_name(self, app_name: str) -> Tuple[bool, str]:
        """Launch application by name with fuzzy matching"""
        matches = self.find_application(app_name)

        if not matches:
            return False, f"No application found matching '{app_name}', Boss."

        # Launch the best match
        best_match, score = matches[0]
        success = self.launch_application(best_match)

        if success:
            return True, f"Launching {best_match.display_name}, Boss."
        else:
            return False, f"Failed to launch {best_match.display_name}, Boss."

    def launch_application_by_name(self, app_name: str) -> dict:
        """Launch application by name and return dict format for AI brain"""
        matches = self.find_application(app_name)

        if not matches:
            # Provide suggestions for similar apps
            # Lower threshold for suggestions
            all_matches = self.find_application(app_name, threshold=50)
            suggestions = []
            for app, score in all_matches[:5]:
                suggestions.append({
                    'name': app.display_name,
                    'score': score,
                    'path': app.path
                })

            return {
                'success': False,
                'app_name': app_name,
                'suggestions': suggestions,
                'message': f"No application found matching '{app_name}'"
            }

        # Launch the best match
        best_match, score = matches[0]
        success = self.launch_application(best_match)

        return {
            'success': success,
            'app_name': best_match.display_name,
            'path': best_match.path,
            'score': score,
            'message': f"Launched {best_match.display_name}" if success else f"Failed to launch {best_match.display_name}"
        }

    def list_applications(self, limit: int = 20) -> List[Application]:
        """List all discovered applications"""
        apps = list(self.applications.values())
        # Sort by name
        apps.sort(key=lambda x: x.display_name.lower())
        return apps[:limit]

    def get_application_info(self, app_name: str) -> Optional[Application]:
        """Get detailed information about an application"""
        matches = self.find_application(app_name)
        if matches:
            return matches[0][0]
        return None

    def find_running_processes(self, app_name: str) -> List[psutil.Process]:
        """Find running processes that match the application name"""
        matching_processes = []
        app_name_lower = app_name.lower()

        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    proc_info = proc.info
                    proc_name = proc_info.get('name', '').lower()
                    proc_exe = proc_info.get('exe', '')

                    # Check if process name or executable path matches
                    if (app_name_lower in proc_name or
                            (proc_exe and app_name_lower in os.path.basename(proc_exe).lower())):
                        matching_processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception as e:
            print(f"[APP] Error finding processes: {e}")

        return matching_processes

    def close_application_by_name(self, app_name: str) -> dict:
        """Close application by name with process matching"""
        try:
            # First try to find the app in our discovered applications for better matching
            matches = self.find_application(app_name)

            search_terms = [app_name.lower()]
            if matches:
                # Add the actual app name and executable name to search terms
                best_match = matches[0][0]
                search_terms.extend([
                    best_match.display_name.lower(),
                    best_match.name.lower(),
                    os.path.basename(
                        best_match.path).lower().replace('.exe', '')
                ])

            # Find running processes
            all_matching_processes = []
            for term in search_terms:
                processes = self.find_running_processes(term)
                all_matching_processes.extend(processes)

            # Remove duplicates
            unique_processes = {}
            for proc in all_matching_processes:
                unique_processes[proc.pid] = proc

            processes_to_close = list(unique_processes.values())

            if not processes_to_close:
                return {
                    'success': False,
                    'app_name': app_name,
                    'message': f"No running processes found for '{app_name}'"
                }

            # Attempt to close the processes
            closed_processes = []
            failed_processes = []

            for proc in processes_to_close:
                try:
                    proc_name = proc.name()
                    print(f"[APP] Closing {proc_name} (PID: {proc.pid})...")

                    # Try graceful termination first
                    proc.terminate()

                    # Wait up to 3 seconds for graceful shutdown
                    try:
                        proc.wait(timeout=3)
                        closed_processes.append(proc_name)
                    except psutil.TimeoutExpired:
                        # Force kill if graceful termination doesn't work
                        print(f"[APP] Force closing {proc_name}...")
                        proc.kill()
                        proc.wait(timeout=2)
                        closed_processes.append(proc_name)

                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    failed_processes.append(f"{proc.name()} ({e})")
                except Exception as e:
                    failed_processes.append(f"{proc.name()} ({e})")

            if closed_processes:
                closed_names = ", ".join(closed_processes)
                message = f"Closed {closed_names}"
                if failed_processes:
                    failed_names = ", ".join(failed_processes)
                    message += f". Failed to close: {failed_names}"

                return {
                    'success': True,
                    'app_name': app_name,
                    'closed_processes': closed_processes,
                    'failed_processes': failed_processes,
                    'message': message
                }
            else:
                return {
                    'success': False,
                    'app_name': app_name,
                    'failed_processes': failed_processes,
                    'message': f"Failed to close any processes for '{app_name}'"
                }

        except Exception as e:
            return {
                'success': False,
                'app_name': app_name,
                'message': f"Error closing application: {e}"
            }


# Convenience functions
def create_app_launcher() -> ApplicationLauncher:
    """Create and return an ApplicationLauncher instance"""
    discovery = ApplicationDiscovery()
    return ApplicationLauncher(discovery)


if __name__ == "__main__":
    # Test the application discovery system
    print("Testing JARVIS Application Discovery System...")

    launcher = create_app_launcher()

    print(f"\nDiscovered {len(launcher.applications)} applications")

    # Test some searches
    test_queries = ["notepad", "calculator", "chrome", "steam"]

    for query in test_queries:
        print(f"\nSearching for '{query}':")
        matches = launcher.find_application(query)
        for app, score in matches[:3]:
            print(f"  {app.display_name} ({score}%) - {app.app_type}")
