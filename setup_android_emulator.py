"""
Android Emulator Setup for AndroidWorld

This module provides utilities to setup and manage an Android emulator
configured specifically for running AndroidWorld benchmarks.
"""

import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path
from typing import Dict, Optional

from loguru import logger

# Constants matching Docker setup
API_LEVEL = "33"
BUILD_TOOLS = "33.0.0"
TARGET = "google_apis"
CLI_REV = "11076708"  # Match Docker exactly
EMULATOR_TIMEOUT = 300  # 5 minutes
MEMORY_MB = 2048


def get_emulator_arch() -> tuple[str, str, str]:
    """Get emulator architecture based on host system.

    Returns:
        (arch, emulator_name, device) tuple
    """
    system = platform.system().lower()
    machine = platform.machine().lower()

    # On Apple Silicon, use ARM64 for much better performance
    if system == "darwin" and machine == "arm64":
        return ("arm64-v8a", "Pixel_6_API_33_ARM64", "pixel_6")
    else:
        # x86_64 for Linux and Intel Macs
        return ("x86_64", "Pixel_6_API_33", "pixel_6")


ARCH, EMULATOR_NAME, DEVICE = get_emulator_arch()


def detect_os() -> str:
    """Detect operating system."""
    system = platform.system().lower()
    if system == "linux":
        return "linux"
    elif system == "darwin":
        return "mac"
    else:
        raise RuntimeError(f"Unsupported OS: {system}. Only linux and macOS supported.")


def sdk_root() -> Path:
    """Get Android SDK root directory."""
    return Path(os.path.expanduser("~/Android/Sdk"))


def build_env(sdk: Path) -> Dict[str, str]:
    """Build environment variables with Android SDK paths."""
    env = os.environ.copy()
    env["ANDROID_SDK_ROOT"] = str(sdk)

    # Match Docker PATH structure: cmdline-tools/tools not latest!
    paths = [
        str(sdk / "cmdline-tools" / "tools" / "bin"),
        str(sdk / "platform-tools"),
        str(sdk / "emulator"),
        str(sdk / "build-tools" / BUILD_TOOLS),
    ]
    env["PATH"] = os.pathsep.join(paths + [env.get("PATH", "")])
    return env


def run_command(
    cmd: str,
    env: Optional[Dict] = None,
    check: bool = True,
    capture_output: bool = False,
    input_text: Optional[str] = None,
) -> subprocess.CompletedProcess:
    """Run shell command with error handling."""
    if not capture_output:
        logger.debug(f"Running command: {cmd}")

    result = subprocess.run(
        cmd,
        shell=True,
        env=env,
        check=False,
        capture_output=capture_output,
        text=True,
        input=input_text,
    )

    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}\n{result.stderr}")

    return result


def ensure_java():
    """Ensure Java is installed."""
    try:
        run_command("java -version", capture_output=True)
        logger.info("Java found")
    except:
        raise RuntimeError(
            "Java (JDK 11+) not found. Please install Java:\n"
            "  Linux: sudo apt install openjdk-11-jdk\n"
            "  macOS: brew install openjdk@11"
        )


def download_cmdline_tools(sdk: Path):
    """Download and install Android command-line tools (idempotent)."""
    os_id = detect_os()
    url = f"https://dl.google.com/android/repository/commandlinetools-{os_id}-{CLI_REV}_latest.zip"

    # Match Docker structure: cmdline-tools/tools not latest!
    tools_dir = sdk / "cmdline-tools" / "tools"

    if (tools_dir / "bin" / "sdkmanager").exists():
        # Ensure permissions are correct on existing installation
        bin_dir = tools_dir / "bin"
        for binary in bin_dir.glob("*"):
            if binary.is_file():
                os.chmod(binary, 0o755)
        logger.info("Command-line tools already installed")
        return

    logger.info(f"Downloading Android cmdline-tools from {url}")

    with tempfile.TemporaryDirectory() as td:
        zip_path = Path(td) / "cmdline-tools.zip"

        # Download
        run_command(f"curl -L --fail -o {zip_path} {url}")

        # Extract
        logger.info("Extracting command-line tools...")
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(Path(td))

        # Move to tools directory (Docker structure)
        extracted = Path(td) / "cmdline-tools"
        tools_dir.parent.mkdir(parents=True, exist_ok=True)

        if tools_dir.exists():
            shutil.rmtree(tools_dir)

        shutil.move(str(extracted), str(tools_dir))

    # Set executable permissions on binaries
    bin_dir = tools_dir / "bin"
    for binary in bin_dir.glob("*"):
        if binary.is_file():
            os.chmod(binary, 0o755)

    logger.info("Command-line tools installed")


def install_sdk_packages(env: Dict):
    """Install required SDK packages (idempotent)."""
    logger.info("Installing Android SDK packages...")

    api = f"android-{API_LEVEL}"
    system_image = f"system-images;{api};{TARGET};{ARCH}"
    platform = f"platforms;{api}"
    build_tool = f"build-tools;{BUILD_TOOLS}"

    # Check if already installed
    result = run_command(
        "sdkmanager --list_installed", env=env, capture_output=True, check=False
    )
    if result.returncode == 0:
        installed = result.stdout
        if all(
            pkg in installed
            for pkg in [
                system_image,
                platform,
                build_tool,
                "platform-tools",
                "emulator",
            ]
        ):
            logger.info("SDK packages already installed")
            return

    # Accept licenses (match Docker: yes Y)
    logger.info("Accepting licenses...")
    yes_proc = subprocess.Popen(
        ["yes", "y"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
    )
    subprocess.run(
        "sdkmanager --licenses",
        shell=True,
        env=env,
        stdin=yes_proc.stdout,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    yes_proc.terminate()

    # Install packages
    packages = (
        f'"{system_image}" "{platform}" "{build_tool}" "platform-tools" "emulator"'
    )
    run_command(f"sdkmanager --verbose --no_https {packages}", env=env)

    logger.info("SDK packages installed")


def create_avd(env: Dict):
    """Create Android Virtual Device (idempotent)."""
    # Check if AVD already exists
    result = run_command(
        "avdmanager list avd", env=env, capture_output=True, check=False
    )
    if result.returncode == 0 and EMULATOR_NAME in result.stdout:
        logger.info(f"AVD already exists: {EMULATOR_NAME}")
        return

    logger.info(f"Creating AVD: {EMULATOR_NAME}")

    api = f"android-{API_LEVEL}"
    system_image = f"system-images;{api};{TARGET};{ARCH}"

    # Match Docker: echo "no" to decline custom hardware profile
    run_command(
        f'echo "no" | avdmanager --verbose create avd --force '
        f'--name "{EMULATOR_NAME}" --device "{DEVICE}" --package "{system_image}"',
        env=env,
    )

    logger.info(f"AVD created: {EMULATOR_NAME}")


def check_hardware_acceleration() -> str:
    """Check if hardware acceleration is available."""
    hw_accel_override = os.environ.get("HW_ACCEL_OVERRIDE")
    if hw_accel_override:
        return hw_accel_override

    os_type = detect_os()

    if os_type == "mac":
        # macOS uses Hypervisor.framework automatically
        result = run_command(
            "sysctl -a | grep -E -c '(vmx|svm)' || true", capture_output=True
        )
        support = int(result.stdout.strip() or "0")
    else:
        # Linux: check for KVM
        result = run_command(
            "grep -E -c '(vmx|svm)' /proc/cpuinfo || true", capture_output=True
        )
        support = int(result.stdout.strip() or "0")

    if support == 0:
        logger.warning("No hardware acceleration found. Emulator will run slowly.")
        return "-accel off"
    else:
        logger.info("Hardware acceleration available")
        return "-accel on"


def kill_emulator(env: Optional[Dict] = None):
    """Kill any running emulators."""
    if env is None:
        sdk = sdk_root()
        env = build_env(sdk)

    logger.info("Killing existing emulators...")
    run_command(
        "adb devices | grep emulator | cut -f1 | xargs -I {} adb -s {} emu kill || true",
        env=env,
        check=False,
    )
    time.sleep(2)


def is_emulator_running(env: Dict) -> bool:
    """Check if emulator is running and booted."""
    result = run_command(
        "adb shell getprop sys.boot_completed 2>&1",
        env=env,
        capture_output=True,
        check=False,
    )
    return result.stdout.strip() == "1"


def launch_emulator_process(env: Dict):
    """Launch emulator in background with AndroidWorld configuration."""
    logger.info(f"Launching emulator: {EMULATOR_NAME}")
    logger.info(f"Using {ARCH} architecture")

    kill_emulator(env)

    hw_accel = check_hardware_acceleration()
    os_type = detect_os()

    # CRITICAL: -grpc 8554 is required for AndroidWorld
    base_options = f"-avd {EMULATOR_NAME} -no-window -no-snapshot -no-boot-anim -memory {MEMORY_MB} {hw_accel} -grpc 8554"

    # GPU settings differ by OS and architecture
    if os_type == "linux":
        gpu_option = "-gpu off"
    else:  # mac
        # On Apple Silicon with ARM64 image, use host GPU
        machine = platform.machine().lower()
        if machine == "arm64" and ARCH == "arm64-v8a":
            gpu_option = "-gpu host"  # Much faster on Apple Silicon
        else:
            gpu_option = "-gpu swiftshader_indirect"

    full_command = f"emulator {base_options} {gpu_option}"

    logger.debug(f"Emulator command: {full_command}")

    # Launch in background
    subprocess.Popen(
        full_command,
        shell=True,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    time.sleep(2)  # Give emulator time to start


def wait_for_boot(env: Dict, timeout: int = EMULATOR_TIMEOUT) -> bool:
    """Wait for emulator to fully boot."""
    logger.info("Waiting for emulator to boot...")

    start_time = time.time()

    while True:
        elapsed = int(time.time() - start_time)

        # Check boot completion
        result = run_command(
            "adb shell getprop sys.boot_completed 2>&1",
            env=env,
            capture_output=True,
            check=False,
        )

        boot_status = result.stdout.strip()

        if boot_status == "1":
            logger.info(f"Emulator ready after {elapsed}s")
            return True

        # Check timeout
        if elapsed > timeout:
            logger.error(f"Timeout after {timeout}s")
            return False

        time.sleep(4)


def configure_emulator(env: Dict):
    """Configure emulator post-boot (animations, hidden API, etc)."""
    logger.info("Configuring emulator...")

    # Get root access (required for AndroidWorld)
    logger.debug("Getting root access...")
    run_command("adb root", env=env, check=False)
    time.sleep(1)

    # Disable animations (critical for deterministic testing)
    logger.debug("Disabling animations...")
    run_command('adb shell "settings put global window_animation_scale 0.0"', env=env)
    run_command(
        'adb shell "settings put global transition_animation_scale 0.0"', env=env
    )
    run_command('adb shell "settings put global animator_duration_scale 0.0"', env=env)

    # Set hidden API policy (required for app testing)
    logger.debug("Setting hidden API policy...")
    run_command(
        'adb shell "settings put global hidden_api_policy_pre_p_apps 1;'
        "settings put global hidden_api_policy_p_apps 1;"
        'settings put global hidden_api_policy 1"',
        env=env,
    )

    # Unlock screen
    logger.debug("Unlocking screen...")
    run_command("adb shell input keyevent 82", env=env)

    time.sleep(1)

    logger.info("Emulator configured successfully")


def setup_emulator() -> Dict[str, str]:
    """
    Setup Android SDK and create AVD (idempotent).
    Returns environment dict with SDK paths.
    """
    logger.info("Setting up Android emulator...")

    ensure_java()

    sdk = sdk_root()
    download_cmdline_tools(sdk)

    env = build_env(sdk)

    # Verify sdkmanager works
    run_command("sdkmanager --version", env=env, capture_output=True)

    install_sdk_packages(env)
    create_avd(env)

    logger.info("Android emulator setup complete")
    return env


def launch_emulator(env: Optional[Dict] = None) -> Dict[str, str]:
    """
    Launch and configure emulator (idempotent).
    If emulator is already running and configured, returns immediately.
    Returns environment dict with SDK paths.
    """
    if env is None:
        sdk = sdk_root()
        env = build_env(sdk)

    # Check if already running
    if is_emulator_running(env):
        logger.info("Emulator already running and configured")
        return env

    logger.info("Launching emulator...")

    launch_emulator_process(env)

    if not wait_for_boot(env):
        raise RuntimeError("Failed to start emulator properly")

    configure_emulator(env)

    logger.info("Emulator ready for AndroidWorld")
    return env


def setup_and_launch_emulator() -> Dict[str, str]:
    """
    Complete setup and launch (idempotent).
    Returns environment dict with SDK paths.
    """
    env = setup_emulator()
    env = launch_emulator(env)
    return env


def main():
    """Main entry point for CLI usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Setup Android Emulator for AndroidWorld benchmarks"
    )
    parser.add_argument(
        "--launch",
        action="store_true",
        help="Launch emulator after setup (default: setup only)",
    )
    parser.add_argument("--kill", action="store_true", help="Kill running emulator")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Configure logging
    logger.remove()
    log_level = "DEBUG" if args.verbose else "INFO"
    logger.add(sys.stderr, level=log_level)

    try:
        if args.kill:
            kill_emulator()
            logger.info("Emulator killed")
        elif args.launch:
            setup_and_launch_emulator()
            logger.info("Setup and launch complete")
        else:
            setup_emulator()
            logger.info("Setup complete. Run with --launch to start emulator.")
    except KeyboardInterrupt:
        logger.warning("Interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
